import abc
from collections.abc import Sequence
import dataclasses
import datetime
import math
import os
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

import bpy
import mathutils

from .build_id import BUILD_ID
from .props import other_mode_props
from .props import tiles_props
from .props import combiner_props
from .props import vals_props
from .props import geometry_mode_props

if TYPE_CHECKING:
    import dragex_backend
else:
    try:
        import dragex_backend
    except ModuleNotFoundError:
        dragex_backend = None


def new_float_buf(len):
    return np.empty(
        shape=len,
        dtype=np.float32,
        order="C",
    )


def new_uint_buf(len):
    return np.empty(
        shape=len,
        dtype=np.uint32,  # np.uint leads to L format (unsigned long)
        order="C",
    )


C_IDENTIFIER_ALLOWED = frozenset(
    "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_" "0123456789"
)
C_IDENTIFIER_START_ALLOWED = frozenset(
    "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_"
)


def make_c_identifier(s: str):
    if s == "":
        return "_"
    s = "".join(c if c in C_IDENTIFIER_ALLOWED else "_" for c in s)
    if s[0] not in C_IDENTIFIER_START_ALLOWED:
        s = "_" + s
    return s


def material_to_MaterialInfo(
    mat: bpy.types.Material,
    image_infos: dict[bpy.types.Image, "dragex_backend.MaterialInfoImage"],
):
    mat_dragex: DragExMaterialProperties = mat.dragex
    other_modes = mat_dragex.other_modes
    tiles = mat_dragex.tiles
    combiner = mat_dragex.combiner
    vals = mat_dragex.vals
    mat_geomode = mat_dragex.geometry_mode

    mat_info_tiles = list[dragex_backend.MaterialInfoTile]()
    for tile in tiles.tiles:
        image: bpy.types.Image | None = tile.image
        if image is None:
            image_info = None
        else:
            image_info = image_infos.get(image)
            if image_info is None:
                width, height = image.size
                image_info = dragex_backend.MaterialInfoImage(
                    c_identifier=make_c_identifier(image.name),
                    width=width,
                    height=height,
                )
                image_infos[image] = image_info
        mat_info_tiles.append(
            dragex_backend.MaterialInfoTile(
                image=image_info,
                format=tile.format,
                size=tile.size,
                line=tile.line,
                address=tile.address,
                palette=tile.palette,
                clamp_T=tile.clamp_T,
                mirror_T=tile.mirror_T,
                mask_T=tile.mask_T,
                shift_T=tile.shift_T,
                clamp_S=tile.clamp_S,
                mirror_S=tile.mirror_S,
                mask_S=tile.mask_S,
                shift_S=tile.shift_S,
                upper_left_S=tile.upper_left_S,
                upper_left_T=tile.upper_left_T,
                lower_right_S=tile.lower_right_S,
                lower_right_T=tile.lower_right_T,
            )
        )

    mat_info = dragex_backend.MaterialInfo(
        name=make_c_identifier(mat.name),
        uv_basis_s=mat_dragex.uv_basis_s,
        uv_basis_t=mat_dragex.uv_basis_t,
        other_modes=dragex_backend.MaterialInfoOtherModes(
            atomic_prim=other_modes.atomic_prim,
            cycle_type=other_modes.cycle_type,
            persp_tex_en=other_modes.persp_tex_en,
            detail_tex_en=other_modes.detail_tex_en,
            sharpen_tex_en=other_modes.sharpen_tex_en,
            tex_lod_en=other_modes.tex_lod_en,
            tlut_en=other_modes.tlut_en,
            tlut_type=other_modes.tlut_type,
            #
            sample_type=other_modes.sample_type,
            mid_texel=other_modes.mid_texel,
            bi_lerp_0=other_modes.bi_lerp_0,
            bi_lerp_1=other_modes.bi_lerp_1,
            convert_one=other_modes.convert_one,
            key_en=other_modes.key_en,
            rgb_dither_sel=other_modes.rgb_dither_sel,
            alpha_dither_sel=other_modes.alpha_dither_sel,
            #
            bl_m1a_0=other_modes.bl_m1a_0,
            bl_m1a_1=other_modes.bl_m1a_1,
            bl_m1b_0=other_modes.bl_m1b_0,
            bl_m1b_1=other_modes.bl_m1b_1,
            bl_m2a_0=other_modes.bl_m2a_0,
            bl_m2a_1=other_modes.bl_m2a_1,
            bl_m2b_0=other_modes.bl_m2b_0,
            bl_m2b_1=other_modes.bl_m2b_1,
            #
            force_blend=other_modes.force_blend,
            alpha_cvg_select=other_modes.alpha_cvg_select,
            cvg_x_alpha=other_modes.cvg_x_alpha,
            z_mode=other_modes.z_mode,
            cvg_dest=other_modes.cvg_dest,
            color_on_cvg=other_modes.color_on_cvg,
            #
            image_read_en=other_modes.image_read_en,
            z_update_en=other_modes.z_update_en,
            z_compare_en=other_modes.z_compare_en,
            antialias_en=other_modes.antialias_en,
            z_source_sel=other_modes.z_source_sel,
            dither_alpha_en=other_modes.dither_alpha_en,
            alpha_compare_en=other_modes.alpha_compare_en,
        ),
        tiles=mat_info_tiles,
        combiner=dragex_backend.MaterialInfoCombiner(
            combiner.rgb_A_0,
            combiner.rgb_B_0,
            combiner.rgb_C_0,
            combiner.rgb_D_0,
            combiner.alpha_A_0,
            combiner.alpha_B_0,
            combiner.alpha_C_0,
            combiner.alpha_D_0,
            combiner.rgb_A_1,
            combiner.rgb_B_1,
            combiner.rgb_C_1,
            combiner.rgb_D_1,
            combiner.alpha_A_1,
            combiner.alpha_B_1,
            combiner.alpha_C_1,
            combiner.alpha_D_1,
        ),
        vals=dragex_backend.MaterialInfoVals(
            primitive_depth_z=vals.primitive_depth_z,
            primitive_depth_dz=vals.primitive_depth_dz,
            fog_color=vals.fog_color,
            blend_color=vals.blend_color,
            min_level=vals.min_level,
            prim_lod_frac=vals.prim_lod_frac,
            primitive_color=vals.primitive_color,
            environment_color=vals.environment_color,
        ),
        geometry_mode=dragex_backend.MaterialInfoGeometryMode(
            lighting=mat_geomode.lighting,
        ),
    )

    return mat_info


transform_zup_to_yup = mathutils.Matrix(
    (
        (1, 0, 0),
        (0, 0, 1),
        (0, -1, 0),
    )
)


def mesh_to_mesh_info(
    obj: bpy.types.Object,
    mesh: bpy.types.Mesh,
    transform: mathutils.Matrix,
):
    # TODO test more with different matrix_world
    transform = transform.to_4x4() @ obj.matrix_world
    if transform[3] != mathutils.Vector((0, 0, 0, 1)):
        raise Exception("Unexpected transform", transform)
    transform3 = transform.to_3x3()
    transform3_np = np.array(transform3)
    transform_translation = transform.translation
    transform_translation_np = np.array(transform_translation)

    # note: if size is too small, error is undescriptive:
    # "RuntimeError: internal error setting the array"
    buf_vertices_co = new_float_buf(3 * len(mesh.vertices))
    mesh.vertices.foreach_get("co", buf_vertices_co)
    mesh.calc_loop_triangles()
    buf_triangles_loops = new_uint_buf(3 * len(mesh.loop_triangles))
    buf_triangles_material_index = new_uint_buf(len(mesh.loop_triangles))
    mesh.loop_triangles[0].loops
    mesh.loop_triangles[0].material_index
    mesh.loop_triangles.foreach_get("loops", buf_triangles_loops)
    mesh.loop_triangles.foreach_get("material_index", buf_triangles_material_index)
    mesh.loops[0].vertex_index
    mesh.loops[0].normal
    buf_loops_vertex_index = new_uint_buf(len(mesh.loops))
    buf_loops_normal = new_float_buf(3 * len(mesh.loops))
    mesh.loops.foreach_get("vertex_index", buf_loops_vertex_index)
    mesh.loops.foreach_get("normal", buf_loops_normal)

    buf_vertices_co_Nx3 = buf_vertices_co.reshape((len(mesh.vertices), 3))
    np.matmul(transform3_np, buf_vertices_co_Nx3.T, out=buf_vertices_co_Nx3.T)
    buf_vertices_co_Nx3 += transform_translation_np

    buf_loops_normal_Nx3 = buf_loops_normal.reshape((len(mesh.loops), 3))
    np.matmul(transform3_np, buf_loops_normal_Nx3.T, out=buf_loops_normal_Nx3.T)

    active_color_attribute = mesh.color_attributes.active_color
    if active_color_attribute is None:
        buf_corners_color = None
        buf_points_color = None
    else:
        if active_color_attribute.data_type in {"FLOAT_COLOR", "BYTE_COLOR"}:
            assert isinstance(
                active_color_attribute,
                (
                    bpy.types.FloatColorAttribute,
                    bpy.types.ByteColorAttribute,
                ),
            )
            # Note: for ByteColorAttribute too the color uses floats
            if active_color_attribute.domain == "CORNER":
                buf_corners_color = new_float_buf(4 * len(mesh.loops))
                active_color_attribute.data.foreach_get("color", buf_corners_color)
                buf_points_color = None
            elif active_color_attribute.domain == "POINT":
                buf_corners_color = None
                buf_points_color = new_float_buf(4 * len(mesh.vertices))
                active_color_attribute.data.foreach_get("color", buf_points_color)
            else:
                raise NotImplementedError(active_color_attribute.domain)
        else:
            raise NotImplementedError(active_color_attribute.data_type)

    active_uv_layer = mesh.uv_layers.active
    if active_uv_layer is None:
        buf_loops_uv = None
    else:
        buf_loops_uv = new_float_buf(2 * len(mesh.loops))
        active_uv_layer.uv.foreach_get("vector", buf_loops_uv)

    image_infos = dict[bpy.types.Image, dragex_backend.MaterialInfoImage]()
    material_infos = list[dragex_backend.MaterialInfo | None]()
    for mat_index in range(len(obj.material_slots)):
        mat = obj.material_slots[mat_index].material
        if mat is None:
            mat_info = None
        else:
            mat_info = material_to_MaterialInfo(mat, image_infos)
        material_infos.append(mat_info)
    default_material_info = dragex_backend.MaterialInfo(
        name="DEFAULT_MATERIAL",
        uv_basis_s=1,
        uv_basis_t=1,
        other_modes=dragex_backend.MaterialInfoOtherModes(
            # TODO put more thought into default material
            atomic_prim=False,
            cycle_type="1CYCLE",
            persp_tex_en=False,
            detail_tex_en=False,
            sharpen_tex_en=False,
            tex_lod_en=False,
            tlut_en=False,
            tlut_type=False,
            #
            sample_type=False,
            mid_texel=False,
            bi_lerp_0=False,
            bi_lerp_1=False,
            convert_one=False,
            key_en=False,
            rgb_dither_sel="MAGIC_SQUARE",
            alpha_dither_sel="NONE",
            #
            bl_m1a_0="INPUT",
            bl_m1a_1="INPUT",
            bl_m1b_0="0",
            bl_m1b_1="0",
            bl_m2a_0="INPUT",
            bl_m2a_1="INPUT",
            bl_m2b_0="1",
            bl_m2b_1="1",
            #
            force_blend=False,
            alpha_cvg_select=False,
            cvg_x_alpha=False,
            z_mode="OPAQUE",
            cvg_dest="CLAMP",
            color_on_cvg=False,
            #
            image_read_en=False,
            z_update_en=False,
            z_compare_en=False,
            antialias_en=False,
            z_source_sel=False,
            dither_alpha_en=False,
            alpha_compare_en=False,
        ),
        tiles=(
            [
                dragex_backend.MaterialInfoTile(
                    image=None,
                    format="RGBA",
                    size="16",
                    line=0,
                    address=0,
                    palette=0,
                    clamp_T=False,
                    mirror_T=False,
                    mask_T=0,
                    shift_T=0,
                    clamp_S=False,
                    mirror_S=False,
                    mask_S=0,
                    shift_S=0,
                    upper_left_S=0,
                    upper_left_T=0,
                    lower_right_S=0,
                    lower_right_T=0,
                )
            ]
            * 8
        ),
        combiner=dragex_backend.MaterialInfoCombiner(
            "0",
            "0",
            "0",
            "PRIMITIVE",
            "0",
            "0",
            "0",
            "1",
            "0",
            "0",
            "0",
            "PRIMITIVE",
            "0",
            "0",
            "0",
            "1",
        ),
        vals=dragex_backend.MaterialInfoVals(
            primitive_depth_z=0,
            primitive_depth_dz=0,
            fog_color=(1, 1, 1, 1),
            blend_color=(1, 1, 1, 1),
            min_level=0,
            prim_lod_frac=0,
            primitive_color=(1, 1, 1, 1),
            environment_color=(1, 1, 1, 1),
        ),
        geometry_mode=dragex_backend.MaterialInfoGeometryMode(
            lighting=True,
        ),
    )
    mesh_info = dragex_backend.create_MeshInfo(
        buf_vertices_co,
        buf_triangles_loops,
        buf_triangles_material_index,
        buf_loops_vertex_index,
        buf_loops_normal,
        buf_corners_color,
        buf_points_color,
        buf_loops_uv,
        material_infos,
        default_material_info,
    )
    return mesh_info


def mesh_to_OoTCollisionMesh(
    obj: bpy.types.Object,
    mesh: bpy.types.Mesh,
    transform: mathutils.Matrix,
):
    # TODO test more with different matrix_world
    transform = transform.to_4x4() @ obj.matrix_world
    print(f"{transform=}")
    if transform[3] != mathutils.Vector((0, 0, 0, 1)):
        raise Exception("Unexpected transform", transform)
    transform3 = transform.to_3x3()
    transform3_np = np.array(transform3)
    transform_translation = transform.translation
    transform_translation_np = np.array(transform_translation)

    buf_vertices_co = new_float_buf(3 * len(mesh.vertices))
    mesh.vertices.foreach_get("co", buf_vertices_co)
    mesh.calc_loop_triangles()
    buf_triangles_loops = new_uint_buf(3 * len(mesh.loop_triangles))
    buf_triangles_material_index = new_uint_buf(len(mesh.loop_triangles))
    mesh.loop_triangles.foreach_get("loops", buf_triangles_loops)
    mesh.loop_triangles.foreach_get("material_index", buf_triangles_material_index)
    buf_loops_vertex_index = new_uint_buf(len(mesh.loops))
    mesh.loops.foreach_get("vertex_index", buf_loops_vertex_index)

    buf_vertices_co_Nx3 = buf_vertices_co.reshape((len(mesh.vertices), 3))
    np.matmul(transform3_np, buf_vertices_co_Nx3.T, out=buf_vertices_co_Nx3.T)
    buf_vertices_co_Nx3 += transform_translation_np

    materials = list[dragex_backend.OoTCollisionMaterial | None]()
    for mat_index in range(len(obj.material_slots)):
        mat = obj.material_slots[mat_index].material
        if mat is None:
            colmat = None
        else:
            colmat = None  # material_to_OoTCollisionMaterial(mat)  # TODO
        materials.append(colmat)

    default_material = dragex_backend.OoTCollisionMaterial(
        surface_type_0="SURFACETYPE0(0, 0, FLOOR_TYPE_0, 0, WALL_TYPE_0, FLOOR_PROPERTY_0, false, false)",
        surface_type_1="SURFACETYPE1(SURFACE_MATERIAL_DIRT, FLOOR_EFFECT_0, 31, 1, false, CONVEYOR_SPEED_DISABLED, 0, false)",
        flags_a="0",
        flags_b="0",
    )

    collision_mesh = dragex_backend.create_OoTCollisionMesh(
        buf_vertices_co,
        buf_triangles_loops,
        buf_triangles_material_index,
        buf_loops_vertex_index,
        materials,
        default_material,
    )

    return collision_mesh


class DragExBackendDemoOperator(bpy.types.Operator):
    bl_idname = "dragex.dragex_backend_demo"
    bl_label = "DragEx backend demo"

    def execute_impl(self, context: bpy.types.Context):
        import time

        start = time.time()

        print("Hello World")
        assert context.object is not None
        mesh = context.object.data
        assert isinstance(mesh, bpy.types.Mesh)
        mesh_info = mesh_to_mesh_info(
            context.object,
            mesh,
            (transform_zup_to_yup @ mathutils.Matrix.Scale(1, 3)),
        )
        with open(
            "/home/dragorn421/Documents/dragex/dragex_attempt2/output.c", "w"
        ) as f:
            mesh_info.write_c(f.fileno())
        end = time.time()
        print("dragex_backend_demo took", end - start, "seconds")
        return {"FINISHED"}

    def execute(self, context):
        try:
            return self.execute_impl(context)
        finally:
            dragex_backend.logging.flush()


class DragExMaterialProperties(bpy.types.PropertyGroup):
    uv_basis_s: bpy.props.IntProperty(name="UV Basis S", min=1, default=1)
    uv_basis_t: bpy.props.IntProperty(name="UV Basis T", min=1, default=1)

    other_modes_: bpy.props.PointerProperty(
        type=other_mode_props.DragExMaterialOtherModesProperties
    )
    tiles_: bpy.props.PointerProperty(type=tiles_props.DragExMaterialTilesProperties)
    combiner_: bpy.props.PointerProperty(
        type=combiner_props.DragExMaterialCombinerProperties
    )
    vals_: bpy.props.PointerProperty(type=vals_props.DragExMaterialValsProperties)
    geometry_mode_: bpy.props.PointerProperty(
        type=geometry_mode_props.DragExMaterialGeometryModeProperties
    )

    @property
    def other_modes(self) -> other_mode_props.DragExMaterialOtherModesProperties:
        return self.other_modes_

    @property
    def tiles(self) -> tiles_props.DragExMaterialTilesProperties:
        return self.tiles_

    @property
    def combiner(self) -> combiner_props.DragExMaterialCombinerProperties:
        return self.combiner_

    @property
    def vals(self) -> vals_props.DragExMaterialValsProperties:
        return self.vals_

    @property
    def geometry_mode(self) -> geometry_mode_props.DragExMaterialGeometryModeProperties:
        return self.geometry_mode_


class DragExMaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_dragex"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.scene.dragex.target != "NONE" and context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex: DragExMaterialProperties = mat.dragex
        mat_geomode = mat_dragex.geometry_mode
        other_modes = mat_dragex.other_modes
        combiner = mat_dragex.combiner
        vals = mat_dragex.vals
        tiles = mat_dragex.tiles.tiles
        self.layout.prop(mat_geomode, "lighting")
        self.layout.prop(mat_dragex, "uv_basis_s")
        self.layout.prop(mat_dragex, "uv_basis_t")
        self.layout.prop(vals, "primitive_depth_z")
        self.layout.prop(vals, "primitive_depth_dz")
        self.layout.prop(vals, "fog_color")
        self.layout.prop(vals, "blend_color")
        self.layout.prop(vals, "min_level")
        self.layout.prop(vals, "prim_lod_frac")
        self.layout.prop(vals, "primitive_color")
        self.layout.prop(vals, "environment_color")
        box = self.layout.box()
        box.prop(other_modes, "atomic_prim")
        box.prop(other_modes, "cycle_type")
        box.prop(other_modes, "persp_tex_en")
        box.prop(other_modes, "detail_tex_en")
        box.prop(other_modes, "sharpen_tex_en")
        box.prop(other_modes, "tex_lod_en")
        box.prop(other_modes, "tlut_en")
        box.prop(other_modes, "tlut_type")
        box.prop(other_modes, "sample_type")
        box.prop(other_modes, "mid_texel")
        box.prop(other_modes, "bi_lerp_0")
        box.prop(other_modes, "bi_lerp_1")
        box.prop(other_modes, "convert_one")
        box.prop(other_modes, "key_en")
        box.prop(other_modes, "rgb_dither_sel")
        box.prop(other_modes, "alpha_dither_sel")
        box.prop(other_modes, "bl_m1a_0")
        box.prop(other_modes, "bl_m1a_1")
        box.prop(other_modes, "bl_m1b_0")
        box.prop(other_modes, "bl_m1b_1")
        box.prop(other_modes, "bl_m2a_0")
        box.prop(other_modes, "bl_m2a_1")
        box.prop(other_modes, "bl_m2b_0")
        box.prop(other_modes, "bl_m2b_1")
        box.prop(other_modes, "force_blend")
        box.prop(other_modes, "alpha_cvg_select")
        box.prop(other_modes, "cvg_x_alpha")
        box.prop(other_modes, "z_mode")
        box.prop(other_modes, "cvg_dest")
        box.prop(other_modes, "color_on_cvg")
        box.prop(other_modes, "image_read_en")
        box.prop(other_modes, "z_update_en")
        box.prop(other_modes, "z_compare_en")
        box.prop(other_modes, "antialias_en")
        box.prop(other_modes, "z_source_sel")
        box.prop(other_modes, "dither_alpha_en")
        box.prop(other_modes, "alpha_compare_en")
        box = self.layout.box()
        box.prop(combiner, "rgb_A_0")
        box.prop(combiner, "rgb_B_0")
        box.prop(combiner, "rgb_C_0")
        box.prop(combiner, "rgb_D_0")
        box.prop(combiner, "alpha_A_0")
        box.prop(combiner, "alpha_B_0")
        box.prop(combiner, "alpha_C_0")
        box.prop(combiner, "alpha_D_0")
        box.prop(combiner, "rgb_A_1")
        box.prop(combiner, "rgb_B_1")
        box.prop(combiner, "rgb_C_1")
        box.prop(combiner, "rgb_D_1")
        box.prop(combiner, "alpha_A_1")
        box.prop(combiner, "alpha_B_1")
        box.prop(combiner, "alpha_C_1")
        box.prop(combiner, "alpha_D_1")
        for i, tile in enumerate(tiles):
            box = self.layout.box()
            box.label(text=f"Tile {i}")
            box.template_ID(tile, "image", new="image.new", open="image.open")
            box.prop(tile, "format")
            box.prop(tile, "size")
            box.prop(tile, "line")
            box.prop(tile, "address")
            box.prop(tile, "palette")
            box.prop(tile, "clamp_T")
            box.prop(tile, "mirror_T")
            box.prop(tile, "mask_T")
            box.prop(tile, "shift_T")
            box.prop(tile, "clamp_S")
            box.prop(tile, "mirror_S")
            box.prop(tile, "mask_S")
            box.prop(tile, "shift_S")
            box.prop(tile, "upper_left_S")
            box.prop(tile, "upper_left_T")
            box.prop(tile, "lower_right_S")
            box.prop(tile, "lower_right_T")


class OoTRoomShape(abc.ABC):
    pass


@dataclasses.dataclass(eq=False)  # Use id-based equality and hashing
class OoTRoom:
    echo: str
    room_behavior_type: str
    room_behavior_environment: str
    room_behavior_showInvisActors: str
    room_behavior_disableWarpSongs: bool
    skybox_disables_disableSky: bool
    skybox_disables_disableSunMoon: bool
    time_settings_hour: str
    time_settings_min: str
    time_settings_timeSpeed: str
    shape: OoTRoomShape


@dataclasses.dataclass(eq=False)
class OoTRoomShapeNormal(OoTRoomShape):
    entries_opa: Sequence["dragex_backend.MeshInfo"]
    entries_xlu: Sequence["dragex_backend.MeshInfo"]


@dataclasses.dataclass(eq=False)
class OoTSpawn:
    player_entry: "OoTActorEntry"
    room: OoTRoom


class OoTActorParams(abc.ABC):
    def to_c(self) -> str: ...


@dataclasses.dataclass(eq=False)
class OoTPlayerActorParams(OoTActorParams):
    startMode: str
    startBgCamIndex: int

    def to_c(self):
        # TODO use PLAYER_START_BG_CAM_DEFAULT
        return f"PLAYER_PARAMS({self.startMode}, {self.startBgCamIndex})"


@dataclasses.dataclass(eq=False)
class OoTActorEntry:
    id: str
    pos: tuple[int, int, int]
    rot: tuple[float, float, float]  # radians
    params: OoTActorParams


@dataclasses.dataclass(eq=False)
class OoTEnvLightSettings:
    ambientColor: tuple[float, float, float]
    light1Dir: tuple[float, float, float]
    light1Color: tuple[float, float, float]
    light2Dir: tuple[float, float, float]
    light2Color: tuple[float, float, float]
    fogColor: tuple[float, float, float]
    blend_rate: str
    fog_near: str
    zFar: str


@dataclasses.dataclass(eq=False)
class OoTScene:
    sound_settings_specId: str
    sound_settings_natureAmbienceId: str
    sound_settings_seqId: str
    rooms: list[OoTRoom]
    collision: "dragex_backend.OoTCollisionMesh"
    spawns: list[OoTSpawn]
    special_files_naviQuestHintFileId: str
    special_files_keepObjectId: str
    player_entry_list: list[OoTActorEntry]
    skybox_settings_skyboxId: str
    skybox_settings_skyboxConfig: str
    skybox_settings_envLightMode: str
    env_light_settings_list: list[OoTEnvLightSettings]


class CollectMapException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def collect_map(coll_scene: bpy.types.Collection, export_options: "ExportOptions"):
    transform_inverted = export_options.transform.inverted()

    room_colls = dict[int, bpy.types.Collection]()
    for coll in coll_scene.children_recursive:
        coll_dragex: DragExCollectionProperties = coll.dragex
        if coll_dragex.oot.type == "ROOM":
            room_number = coll_dragex.oot.room.number
            if room_number in room_colls:
                raise CollectMapException(
                    f"Duplicate room number {room_number}: used by "
                    f"{room_colls[room_number].name} and {coll.name}"
                )
            room_colls[room_number] = coll

    n_rooms = max(room_colls.keys()) + 1
    expected_room_numbers = set(range(n_rooms))
    assert expected_room_numbers.issuperset(room_colls.keys())
    if room_colls.keys() != expected_room_numbers:
        raise CollectMapException(
            "The following room numbers are missing: "
            + ", ".join(map(str, sorted(expected_room_numbers - room_colls.keys())))
        )

    rooms = list[OoTRoom]()
    spawns = dict[int, OoTSpawn]()
    spawns_empties = dict[int, bpy.types.Object]()

    for i in range(n_rooms):
        room_coll = room_colls[i]
        room_coll_dragex: DragExCollectionProperties = room_coll.dragex
        room_spawns = list[OoTSpawn]()
        entries_opa = list[dragex_backend.MeshInfo]()
        entries_xlu = list[dragex_backend.MeshInfo]()
        for obj in room_coll.all_objects:
            if obj.type == "EMPTY":
                obj_dragex: DragExObjectProperties = obj.dragex
                if obj_dragex.oot.empty.type == "PLAYER_ENTRY":
                    player_entry_props = obj_dragex.oot.empty.player_entry
                    if player_entry_props.spawn_index in spawns:
                        raise CollectMapException(
                            f"Duplicate spawn index {player_entry_props.spawn_index}: "
                            f"used by "
                            f"{spawns_empties[player_entry_props.spawn_index].name} "
                            f"and {obj.name}"
                        )
                    spawns_empties[player_entry_props.spawn_index] = obj
                    params = OoTPlayerActorParams(
                        startMode=player_entry_props.start_mode,
                        startBgCamIndex=player_entry_props.start_bg_cam_index,
                    )
                    player_entry_pos = export_options.transform @ obj.location
                    saved_rotation_mode = obj.rotation_mode
                    try:
                        obj.rotation_mode = "QUATERNION"
                        player_entry_rot_quaternion = obj.rotation_quaternion
                    finally:
                        obj.rotation_mode = saved_rotation_mode
                    # TODO we want what oot calls YXZ, iirc it's what blender calls ZXY but check
                    player_entry_rot = (
                        export_options.transform
                        @ player_entry_rot_quaternion.to_matrix()
                        @ transform_inverted
                    ).to_euler("ZXY")
                    player_entry = OoTActorEntry(
                        id="ACTOR_PLAYER",
                        pos=(
                            round(player_entry_pos.x),
                            round(player_entry_pos.y),
                            round(player_entry_pos.z),
                        ),
                        rot=(
                            player_entry_rot.x,
                            player_entry_rot.y,
                            player_entry_rot.z,
                        ),
                        params=params,
                    )
                    spawn = OoTSpawn(
                        player_entry=player_entry,
                        room=None,  # TODO is set after, find better way
                    )
                    room_spawns.append(spawn)
                    spawns[player_entry_props.spawn_index] = spawn
            if obj.type == "MESH":
                assert isinstance(obj.data, bpy.types.Mesh)
                # TODO this is inefficient if mesh is shared between rooms
                mesh_info = mesh_to_mesh_info(
                    obj,
                    obj.data,
                    export_options.transform,
                )
                # TODO prop to set draw layer opa/xlu
                entries_opa.append(mesh_info)

        shape = OoTRoomShapeNormal(
            entries_opa=entries_opa,
            entries_xlu=entries_xlu,
        )

        room = OoTRoom(
            echo="10",
            room_behavior_type="ROOM_TYPE_NORMAL",
            room_behavior_environment="ROOM_ENV_DEFAULT",
            room_behavior_showInvisActors="LENS_MODE_SHOW_ACTORS",
            room_behavior_disableWarpSongs=False,
            skybox_disables_disableSky=False,
            skybox_disables_disableSunMoon=False,
            time_settings_hour="0xFF",
            time_settings_min="0xFF",
            time_settings_timeSpeed="0",
            shape=shape,
        )
        for spawn in room_spawns:
            spawn.room = room
        rooms.append(room)

    env_light_settings_list = list[OoTEnvLightSettings]()
    for i in range(4):
        env_light_settings_list.append(
            OoTEnvLightSettings(
                ambientColor=(1, 1, 1),
                light1Dir=(1, 0, 0),
                light1Color=(0, 0, 0),
                light2Dir=(1, 0, 0),
                light2Color=(0, 0, 0),
                fogColor=(1, 1, 1),
                blend_rate="4",
                fog_near="ENV_FOGNEAR_MAX",
                zFar="12800",
            )
        )

    n_spawns = max(spawns.keys()) + 1
    expected_spawn_indices = set(range(n_spawns))
    assert expected_spawn_indices.issuperset(spawns.keys())
    if spawns.keys() != expected_spawn_indices:
        raise CollectMapException(
            "The following spawn indices are missing: "
            + ", ".join(map(str, sorted(expected_spawn_indices - spawns.keys())))
        )

    spawns_list = [spawns[_i] for _i in range(n_spawns)]
    player_entry_list = [_spawn.player_entry for _spawn in spawns_list]

    collision_meshes = list[dragex_backend.OoTCollisionMesh]()
    for obj in coll_scene.all_objects:
        if obj.type == "MESH":
            assert isinstance(obj.data, bpy.types.Mesh)
            collision_mesh = mesh_to_OoTCollisionMesh(
                obj,
                obj.data,
                export_options.transform,
            )
            collision_meshes.append(collision_mesh)
    collision = dragex_backend.join_OoTCollisionMeshes(collision_meshes)

    oot_scene = OoTScene(
        sound_settings_specId="0",
        sound_settings_natureAmbienceId="NATURE_ID_NONE",
        sound_settings_seqId="NA_BGM_NO_MUSIC",
        rooms=rooms,
        collision=collision,
        spawns=spawns_list,
        special_files_naviQuestHintFileId="NAVI_QUEST_HINTS_NONE",
        special_files_keepObjectId="OBJECT_INVALID",
        player_entry_list=player_entry_list,
        skybox_settings_skyboxId="SKYBOX_NORMAL_SKY",
        skybox_settings_skyboxConfig="0",
        skybox_settings_envLightMode="LIGHT_MODE_TIME",
        env_light_settings_list=env_light_settings_list,
    )
    return oot_scene


class FDManager:
    def __init__(self):
        self.fds = list[int]()
        self.entered = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.entered = False
        for fd in self.fds:
            os.close(fd)

    def open_w(self, p: os.PathLike):
        fd = os.open(p, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
        self.fds.append(fd)
        return fd


@dataclasses.dataclass
class ExportOptions:
    transform: mathutils.Matrix


def export_coll_scene(
    coll_scene: bpy.types.Collection, out_dir_p: Path, export_options: ExportOptions
):
    oot_scene = collect_map(coll_scene, export_options)

    from pprint import pprint

    pprint(oot_scene)

    map_name_c_identifier = make_c_identifier(coll_scene.name)

    with FDManager() as fd_manager:
        scene_fd = fd_manager.open_w(out_dir_p / f"{map_name_c_identifier}_scene.c")

        room_list_name = f"{map_name_c_identifier}_RoomList"
        col_header_name = f"{map_name_c_identifier}_Col"
        spawn_list_name = f"{map_name_c_identifier}_SpawnList"
        player_entry_list_name = f"{map_name_c_identifier}_PlayerEntryList"
        env_light_settings_list_name = f"{map_name_c_identifier}_EnvLightSettingsList"

        col_vtx_list_name = f"{map_name_c_identifier}_VtxList"
        col_poly_list_name = f"{map_name_c_identifier}_PolyList"
        col_surface_types_name = f"{map_name_c_identifier}_SurfaceTypes"

        with open(scene_fd, "w", closefd=False) as f:
            f.write(
                '#include "stdbool.h"\n'
                '#include "ultra64.h"\n'
                '#include "actor.h"\n'
                '#include "array_count.h"\n'
                '#include "camera.h"\n'
                '#include "object.h"\n'
                '#include "ocarina.h"\n'
                '#include "player.h"\n'
                '#include "scene.h"\n'
                '#include "segment_symbols.h"\n'
                '#include "sequence.h"\n'
                '#include "skybox.h"\n'
            )
            f.write(f"extern RomFile {room_list_name}[{len(oot_scene.rooms)}];\n")
            f.write(f"extern CollisionHeader {col_header_name};\n")
            f.write(f"extern Spawn {spawn_list_name}[];\n")
            f.write(
                f"extern ActorEntry {player_entry_list_name}"
                f"[{len(oot_scene.player_entry_list)}];\n"
            )
            f.write(
                f"extern EnvLightSettings {env_light_settings_list_name}"
                f"[{len(oot_scene.env_light_settings_list)}];\n"
            )
            f.write("// Hi1\n")
            f.write(
                f"SceneCmd {map_name_c_identifier}_scene[] = "
                "{\n"
                f"    SCENE_CMD_SOUND_SETTINGS({oot_scene.sound_settings_specId}, {oot_scene.sound_settings_natureAmbienceId}, {oot_scene.sound_settings_seqId}),\n"
                f"    SCENE_CMD_ROOM_LIST(ARRAY_COUNT({room_list_name}), {room_list_name}),\n"
                f"    SCENE_CMD_COL_HEADER(&{col_header_name}),\n"
                f"    SCENE_CMD_SPAWN_LIST({spawn_list_name}),\n"
                f"    SCENE_CMD_SPECIAL_FILES({oot_scene.special_files_naviQuestHintFileId}, {oot_scene.special_files_keepObjectId}),\n"
                f"    SCENE_CMD_PLAYER_ENTRY_LIST(ARRAY_COUNT({player_entry_list_name}), {player_entry_list_name}),\n"
                f"    SCENE_CMD_SKYBOX_SETTINGS({oot_scene.skybox_settings_skyboxId}, {oot_scene.skybox_settings_skyboxConfig}, {oot_scene.skybox_settings_envLightMode}),\n"
                f"    SCENE_CMD_ENV_LIGHT_SETTINGS(ARRAY_COUNT({env_light_settings_list_name}), {env_light_settings_list_name}),\n"
                f"    SCENE_CMD_END(),\n"
                "};\n"
                "\n"
            )

            for i in range(len(oot_scene.rooms)):
                f.write(f"DECLARE_ROM_SEGMENT({map_name_c_identifier}_room_{i})\n")

            f.write(f"RomFile {room_list_name}[] = " "{\n")
            for i in range(len(oot_scene.rooms)):
                f.write(f"    ROM_FILE({map_name_c_identifier}_room_{i}),\n")
            f.write("};\n" "\n")

            f.write(f"Spawn {spawn_list_name}[] = " "{\n")
            for spawn in oot_scene.spawns:
                player_entry_index = oot_scene.player_entry_list.index(
                    spawn.player_entry
                )
                room_number = oot_scene.rooms.index(spawn.room)
                f.write("    { " f"{player_entry_index}, {room_number}" " },\n")
            f.write("};\n" "\n")

            f.write(f"ActorEntry {player_entry_list_name}[] = " "{\n")
            for player_entry in oot_scene.player_entry_list:

                def rad2bin(v: float):
                    v = round(v / math.pi * 0x8000)
                    v = v % 0x10000
                    if v >= 0x8000:
                        v -= 0x10000
                    return v

                f.write(
                    "    {\n"
                    f"        {player_entry.id},\n"
                    "        {"
                    f" {player_entry.pos[0]},"
                    f" {player_entry.pos[1]},"
                    f" {player_entry.pos[2]} "
                    "},\n"
                    "        {"
                    f" {rad2bin(player_entry.rot[0]):#X},"
                    f" {rad2bin(player_entry.rot[1]):#X},"
                    f" {rad2bin(player_entry.rot[2]):#X} "
                    "},\n"
                    f"        {player_entry.params.to_c()},\n"
                    "    },\n"
                )
            f.write("};\n" "\n")

            f.write(f"EnvLightSettings {env_light_settings_list_name}[] = " "{\n")
            for env_light_settings in oot_scene.env_light_settings_list:

                def colorf2u8(v):
                    v = round(v * 255)
                    return v

                def dirf2s8(v):
                    v = round(v * 127)
                    return v

                f.write(
                    "    {\n"
                    "        {"
                    f" {colorf2u8(env_light_settings.ambientColor[0])},"
                    f" {colorf2u8(env_light_settings.ambientColor[1])},"
                    f" {colorf2u8(env_light_settings.ambientColor[2])} "
                    "},\n"
                    "        {"
                    f" {dirf2s8(env_light_settings.light1Dir[0])},"
                    f" {dirf2s8(env_light_settings.light1Dir[1])},"
                    f" {dirf2s8(env_light_settings.light1Dir[2])} "
                    "},\n"
                    "        {"
                    f" {colorf2u8(env_light_settings.light1Color[0])},"
                    f" {colorf2u8(env_light_settings.light1Color[1])},"
                    f" {colorf2u8(env_light_settings.light1Color[2])} "
                    "},\n"
                    "        {"
                    f" {dirf2s8(env_light_settings.light2Dir[0])},"
                    f" {dirf2s8(env_light_settings.light2Dir[1])},"
                    f" {dirf2s8(env_light_settings.light2Dir[2])} "
                    "},\n"
                    "        {"
                    f" {colorf2u8(env_light_settings.light2Color[0])},"
                    f" {colorf2u8(env_light_settings.light2Color[1])},"
                    f" {colorf2u8(env_light_settings.light2Color[2])} "
                    "},\n"
                    "        {"
                    f" {colorf2u8(env_light_settings.fogColor[0])},"
                    f" {colorf2u8(env_light_settings.fogColor[1])},"
                    f" {colorf2u8(env_light_settings.fogColor[2])} "
                    "},\n"
                    "        BLEND_RATE_AND_FOG_NEAR("
                    f"{env_light_settings.blend_rate}, "
                    f"{env_light_settings.fog_near}),\n"
                    f"        {env_light_settings.zFar},\n"
                    "    },\n"
                )
            f.write("};\n" "\n")

        collision_bounds = oot_scene.collision.write_c(
            scene_fd,
            col_vtx_list_name,
            col_poly_list_name,
            col_surface_types_name,
        )

        with open(scene_fd, "w", closefd=False) as f:
            f.write("// Hi2\n")
            collision_bounds_min = collision_bounds.min
            collision_bounds_max = collision_bounds.max
            f.write(
                f"CollisionHeader {col_header_name} = "
                "{\n"
                "    {"
                f" {collision_bounds_min[0]},"
                f" {collision_bounds_min[1]},"
                f" {collision_bounds_min[2]} "
                "},\n"
                "    {"
                f" {collision_bounds_max[0]},"
                f" {collision_bounds_max[1]},"
                f" {collision_bounds_max[2]} "
                "},\n"
                f"    ARRAY_COUNT({col_vtx_list_name}),\n"
                f"    {col_vtx_list_name},\n"
                f"    ARRAY_COUNT({col_poly_list_name}),\n"
                f"    {col_poly_list_name},\n"
                f"    {col_surface_types_name},\n"
                f"    NULL,\n"  # TODO BgCamList
                f"    0,\n"  # TODO waterboxes
                f"    NULL,\n"
                "};\n"
                "\n"
            )

    for i, room in enumerate(oot_scene.rooms):
        with FDManager() as fd_manager:
            room_fd = fd_manager.open_w(
                out_dir_p / f"{map_name_c_identifier}_room_{i}.c"
            )

            room_shape_name = f"{map_name_c_identifier}_room_{i}_RoomShape"

            with open(room_fd, "w", closefd=False) as f:
                f.write(
                    '#include "stdbool.h"\n'
                    '#include "ultra64.h"\n'
                    '#include "actor.h"\n'
                    '#include "array_count.h"\n'
                    '#include "gfx.h"\n'
                    '#include "object.h"\n'
                    '#include "room.h"\n'
                    '#include "scene.h"\n'
                    '#include "sequence.h"\n'
                    '#include "skybox.h"\n'
                )
                f.write("// Hi3\n")

                if isinstance(room.shape, OoTRoomShapeNormal):
                    f.write(f"extern RoomShapeNormal {room_shape_name};\n")
                else:
                    raise NotImplementedError(type(room.shape))

                def cbool(v: bool):
                    return "true" if v else "false"

                f.write(
                    f"SceneCmd {map_name_c_identifier}_room_{i}[] = "
                    "{\n"
                    f"    SCENE_CMD_ECHO_SETTINGS({room.echo}),\n"
                    f"    SCENE_CMD_ROOM_BEHAVIOR({room.room_behavior_type}, {room.room_behavior_environment}, {room.room_behavior_showInvisActors}, {cbool(room.room_behavior_disableWarpSongs)}),\n"
                    f"    SCENE_CMD_SKYBOX_DISABLES({cbool(room.skybox_disables_disableSky)}, {cbool(room.skybox_disables_disableSunMoon)}),\n"
                    f"    SCENE_CMD_TIME_SETTINGS({room.time_settings_hour}, {room.time_settings_min}, {room.time_settings_timeSpeed}),\n"
                    f"    SCENE_CMD_ROOM_SHAPE(&{room_shape_name}),\n"
                    f"    SCENE_CMD_END(),\n"
                    "};\n"
                    "\n"
                )

            room_shape = room.shape
            if isinstance(room_shape, OoTRoomShapeNormal):
                opa_dlists_names = list[str]()
                xlu_dlists_names = list[str]()
                for mi in room_shape.entries_opa:
                    # TODO batch the fopen() inside write_c by passing a list of MeshInfo to dragex_backend instead
                    dl_name = mi.write_c(room_fd)
                    opa_dlists_names.append(dl_name)
                for mi in room_shape.entries_xlu:
                    dl_name = mi.write_c(room_fd)
                    xlu_dlists_names.append(dl_name)

                if len(opa_dlists_names) < len(xlu_dlists_names):
                    opa_dlists_names += ["NULL"] * (
                        len(xlu_dlists_names) - len(opa_dlists_names)
                    )
                else:
                    xlu_dlists_names += ["NULL"] * (
                        len(opa_dlists_names) - len(xlu_dlists_names)
                    )

                with open(room_fd, "w", closefd=False) as f:
                    f.write("// Hi4\n")
                    dlists_entries_name = f"{map_name_c_identifier}_DListsEntries"
                    f.write(f"RoomShapeDListsEntry {dlists_entries_name}[] = " "{\n")
                    for opa_dl_name, xlu_dl_name in zip(
                        opa_dlists_names, xlu_dlists_names
                    ):
                        f.write(
                            "    {\n"
                            f"        {opa_dl_name},\n"
                            f"        {xlu_dl_name},\n"
                            "    },\n"
                        )
                    f.write("};\n" "\n")

                    f.write(
                        f"RoomShapeNormal {room_shape_name} = "
                        "{\n"
                        "    { ROOM_SHAPE_TYPE_NORMAL },\n"
                        f"    ARRAY_COUNT({dlists_entries_name}),\n"
                        f"    {dlists_entries_name},\n"
                        f"    {dlists_entries_name} + ARRAY_COUNT({dlists_entries_name}),\n"
                        "};\n"
                        "\n"
                    )
            else:
                raise NotImplementedError(type(room_shape))


class DragExOoTExportSceneOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_export_scene"
    bl_label = "DragEx OoT Export Scene"

    def scene_coll_name_search(self, context: bpy.types.Context, edit_text: str):
        edit_text = edit_text.lower()
        scene = context.scene
        assert scene is not None
        for coll in scene.collection.children_recursive:
            coll_dragex: DragExCollectionProperties = coll.dragex
            if coll_dragex.oot.type == "SCENE":
                if edit_text in coll.name.lower():
                    yield coll.name

    scene_coll_name: bpy.props.StringProperty(
        name="Scene",
        description="OoT scene collection to export",
        search=scene_coll_name_search,
        search_options=set(),
    )

    directory: bpy.props.StringProperty(subtype="DIR_PATH", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex: DragExSceneProperties = scene.dragex
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def execute(self, context):
        if self.scene_coll_name == "":
            self.report({"ERROR_INVALID_INPUT"}, "No scene given")
            return {"CANCELLED"}
        coll_scene_to_export = bpy.data.collections[self.scene_coll_name]
        export_directory = Path(self.directory)

        export_coll_scene(
            coll_scene_to_export,
            export_directory,
            ExportOptions(
                transform=(
                    transform_zup_to_yup
                    @ mathutils.Matrix.Scale(1 / context.scene.dragex.oot.scale, 3)
                ),
            ),
        )

        return {"FINISHED"}

    def invoke(self, context, event):
        assert context.window_manager is not None
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class DragExCollectionOoTSceneProperties(bpy.types.PropertyGroup):
    pass


class DragExCollectionOoTRoomProperties(bpy.types.PropertyGroup):
    number: bpy.props.IntProperty(
        name="Room Number",
        description="Number/ID for this room",
        min=0,
    )


class DragExCollectionOoTProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description="OoT collection type",
        items=(
            ("NONE", "None", "No type. A regular collection"),
            ("SCENE", "Scene", "Collection represents an OoT scene"),
            ("ROOM", "Room", "Collection represents an OoT room"),
        ),
        default="NONE",
    )

    scene_: bpy.props.PointerProperty(type=DragExCollectionOoTSceneProperties)
    room_: bpy.props.PointerProperty(type=DragExCollectionOoTRoomProperties)

    @property
    def scene(self) -> DragExCollectionOoTSceneProperties:
        return self.scene_

    @property
    def room(self) -> DragExCollectionOoTRoomProperties:
        return self.room_


class DragExCollectionProperties(bpy.types.PropertyGroup):
    oot_: bpy.props.PointerProperty(type=DragExCollectionOoTProperties)

    @property
    def oot(self) -> DragExCollectionOoTProperties:
        return self.oot_


class DragExSceneOoTProperties(bpy.types.PropertyGroup):
    scale: bpy.props.FloatProperty(
        name="Scale",
        description=(
            "OoT to Blender scaling factor. "
            "For example the default value of 0.01 means 1 Blender centimeter "
            "corresponds to 1 OoT unit"
        ),
        default=0.01,
    )


class DragExSceneProperties(bpy.types.PropertyGroup):
    target: bpy.props.EnumProperty(
        name="Target",
        description="DragEx target",
        default="NONE",
        items=(
            ("NONE", "None", "Disable DragEx features", 1),
            (
                "OOT_F3DEX2_PL",
                "OoT F3DEX2 PosLight",
                "Ocarina of Time 64 with the F3DEX2 Positional Light microcode",
                2,
            ),
        ),
    )

    oot_: bpy.props.PointerProperty(type=DragExSceneOoTProperties)

    @property
    def oot(self) -> DragExSceneOoTProperties:
        return self.oot_


class DragExObjectOoTEmptyPlayerEntryProperties(bpy.types.PropertyGroup):
    start_mode: bpy.props.EnumProperty(
        name="Start Mode",
        description=(
            "Player start mode (PLAYER_START_MODE_ values) indicates the "
            "animation/action to perform when spawning in"
        ),
        default="PLAYER_START_MODE_IDLE",
        items=(
            (
                "PLAYER_START_MODE_NOTHING",
                "NOTHING",
                (
                    "Update is empty and draw function is NULL, nothing occurs. "
                    "Useful in cutscenes, for example."
                ),
            ),
            (
                "PLAYER_START_MODE_TIME_TRAVEL",
                "TIME_TRAVEL",
                "Arriving from time travel. Automatically adjusts by age.",
            ),
            (
                "PLAYER_START_MODE_BLUE_WARP",
                "BLUE_WARP",
                "Arriving from a blue warp.",
            ),
            (
                "PLAYER_START_MODE_DOOR",
                "DOOR",
                (
                    "Unused. Use a door immediately if one is nearby. "
                    "If no door is in usable range, a softlock occurs."
                ),
            ),
            (
                "PLAYER_START_MODE_GROTTO",
                "GROTTO",
                "Arriving from a grotto, launched upward from the ground.",
            ),
            (
                "PLAYER_START_MODE_WARP_SONG",
                "WARP_SONG",
                "Arriving from a warp song.",
            ),
            (
                "PLAYER_START_MODE_FARORES_WIND",
                "FARORES_WIND",
                "Arriving from a Farores Wind warp.",
            ),
            (
                "PLAYER_START_MODE_KNOCKED_OVER",
                "KNOCKED_OVER",
                "Knocked over on the ground and flashing red.",
            ),
            (
                "PLAYER_START_MODE_UNUSED_8",
                "UNUSED_8",
                "Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.",
            ),
            (
                "PLAYER_START_MODE_UNUSED_9",
                "UNUSED_9",
                "Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.",
            ),
            (
                "PLAYER_START_MODE_UNUSED_10",
                "UNUSED_10",
                "Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.",
            ),
            (
                "PLAYER_START_MODE_UNUSED_11",
                "UNUSED_11",
                "Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.",
            ),
            (
                "PLAYER_START_MODE_UNUSED_12",
                "UNUSED_12",
                "Unused, behaves the same as PLAYER_START_MODE_MOVE_FORWARD_SLOW.",
            ),
            (
                "PLAYER_START_MODE_IDLE",
                "IDLE",
                "Idle standing still, or swim if in water.",
            ),
            (
                "PLAYER_START_MODE_MOVE_FORWARD_SLOW",
                "MOVE_FORWARD_SLOW",
                "Take a few steps forward at a slow speed (2.0f), or swim if in water.",
            ),
            (
                "PLAYER_START_MODE_MOVE_FORWARD",
                "MOVE_FORWARD",
                (
                    "Take a few steps forward, using the speed from the last exit "
                    "(gSaveContext.entranceSpeed), or swim if in water."
                ),
            ),
        ),
    )

    # TODO replace with some kind of pointer property to scene camera object
    start_bg_cam_index: bpy.props.IntProperty(
        name="Start BG Cam Index",
        description=(
            "Player start BG cam index sets the initial camera on spawn. "
            "0xFF sets no camera"
        ),
        min=0,
        max=0xFF,
        default=0xFF,
    )

    spawn_index: bpy.props.IntProperty(
        name="Spawn Index",
        description=(
            "Index for the spawn associated to this player entry. "
            "This index is to be used in the entrance table"
        ),
    )


class DragExObjectOoTEmptyProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description="Type of OoT empty object",
        default="NONE",
        items=(
            ("NONE", "None", "No type. A regular empty object"),
            (
                "PLAYER_ENTRY",
                "Player Entry",
                (
                    "Empty represents a Player Entry, a spawn point's location and "
                    "metadata for when loading the map"
                ),
            ),
        ),
    )

    player_entry_: bpy.props.PointerProperty(
        type=DragExObjectOoTEmptyPlayerEntryProperties
    )

    @property
    def player_entry(self) -> DragExObjectOoTEmptyPlayerEntryProperties:
        return self.player_entry_


class DragExObjectOoTProperties(bpy.types.PropertyGroup):
    empty_: bpy.props.PointerProperty(type=DragExObjectOoTEmptyProperties)

    @property
    def empty(self) -> DragExObjectOoTEmptyProperties:
        return self.empty_


class DragExObjectProperties(bpy.types.PropertyGroup):
    oot_: bpy.props.PointerProperty(type=DragExObjectOoTProperties)

    @property
    def oot(self) -> DragExObjectOoTProperties:
        return self.oot_


class DragExTargetPanel(bpy.types.Panel):
    bl_idname = "DRAGEX_PT_target"
    bl_label = "Target"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DragEx"
    bl_order = 0

    def draw(self, context):
        assert self.layout is not None
        scene = context.scene
        assert scene is not None
        dragex: DragExSceneProperties = scene.dragex
        self.layout.prop(dragex, "target")


class DragExOoTNewSceneOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_new_scene"
    bl_label = "New OoT Scene"
    bl_options = {"REGISTER", "UNDO"}

    map_name: bpy.props.StringProperty(
        name="Map Name",
        description="Map name to name the added items from",
        default="My map",
    )
    n_rooms: bpy.props.IntProperty(
        name="Rooms",
        description="Amount of rooms in the map",
        min=1,
        default=1,
    )

    def execute(self, context):
        map_name: str = self.map_name
        cont = True
        i = 0
        while cont:
            scene_name = f"{map_name} Scene"
            room_names = [f"{map_name} Room {_i}" for _i in range(self.n_rooms)]
            cont = scene_name in bpy.data.collections or any(
                _room_name in bpy.data.collections for _room_name in room_names
            )
            if cont:
                i += 1
                map_name = self.map_name + f".{i:03}"

        scene = context.scene
        assert scene is not None
        scene_dragex: DragExSceneProperties = scene.dragex

        scene_coll = bpy.data.collections.new(scene_name)
        scene_coll_dragex: DragExCollectionProperties = scene_coll.dragex
        scene_coll_dragex.oot.type = "SCENE"

        scale = scene_dragex.oot.scale
        room_colls = list[bpy.types.Collection]()
        for room_number, room_name in enumerate(room_names):
            room_coll = bpy.data.collections.new(room_name)
            room_colls.append(room_coll)
            room_coll_dragex: DragExCollectionProperties = room_coll.dragex
            room_coll_dragex.oot.type = "ROOM"
            room_coll_dragex.oot.room.number = room_number
            scene_coll.children.link(room_coll)
            room_mesh = bpy.data.meshes.new(f"{room_name} Mesh")
            x = (room_number * 1000 - 400) * scale
            y = -400 * scale
            w = 800 * scale
            h = 800 * scale
            room_mesh.from_pydata(
                (
                    (x, y, 0),
                    (x + w, y, 0),
                    (x + w, y + h, 0),
                    (x, y + h, 0),
                ),
                (),
                ((0, 1, 2, 3),),
            )
            room_mesh_obj = bpy.data.objects.new(f"{room_name} Mesh", room_mesh)
            room_coll.objects.link(room_mesh_obj)

        player_entry_empty_obj = bpy.data.objects.new(f"{map_name} Player Entry", None)
        player_entry_empty_obj_dragex: DragExObjectProperties = (
            player_entry_empty_obj.dragex
        )
        player_entry_empty_obj.location = (0, 0, 0)
        player_entry_empty_obj.empty_display_type = "ARROWS"
        player_entry_empty_obj_dragex.oot.empty.type = "PLAYER_ENTRY"
        room_colls[0].objects.link(player_entry_empty_obj)

        scene.collection.children.link(scene_coll)
        return {"FINISHED"}


class DragExOoTPanel(bpy.types.Panel):
    bl_idname = "DRAGEX_PT_oot"
    bl_label = "OoT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DragEx"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex: DragExSceneProperties = scene.dragex
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        assert self.layout is not None
        scene = context.scene
        assert scene is not None
        scene_dragex: DragExSceneProperties = scene.dragex
        self.layout.prop(scene_dragex.oot, "scale")
        self.layout.operator(DragExOoTNewSceneOperator.bl_idname)
        self.layout.operator(DragExOoTExportSceneOperator.bl_idname)


class DragExCollectionOoTPanel(bpy.types.Panel):
    bl_idname = "COLLECTION_PT_dragex_oot"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "collection"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex: DragExSceneProperties = scene.dragex
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        coll = context.collection
        assert coll is not None
        coll_dragex: DragExCollectionProperties = coll.dragex
        layout.prop(coll_dragex.oot, "type")
        if coll_dragex.oot.type == "ROOM":
            layout.prop(coll_dragex.oot.room, "number")


class DragExObjectOoTEmptyPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_dragex_oot_empty"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        obj = context.object
        if scene is None or obj is None:
            return False
        scene_dragex: DragExSceneProperties = scene.dragex
        return scene_dragex.target == "OOT_F3DEX2_PL" and obj.type == "EMPTY"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        obj = context.object
        assert obj is not None
        obj_dragex: DragExObjectProperties = obj.dragex
        layout.prop(obj_dragex.oot.empty, "type")
        if obj_dragex.oot.empty.type == "PLAYER_ENTRY":
            layout.prop(obj_dragex.oot.empty.player_entry, "start_mode")
            layout.prop(obj_dragex.oot.empty.player_entry, "start_bg_cam_index")


classes = (
    geometry_mode_props.DragExMaterialGeometryModeProperties,
    other_mode_props.DragExMaterialOtherModesProperties,
    tiles_props.DragExMaterialTileProperties,
    tiles_props.DragExMaterialTilesProperties,
    combiner_props.DragExMaterialCombinerProperties,
    vals_props.DragExMaterialValsProperties,
    DragExMaterialProperties,
    DragExMaterialPanel,
    DragExCollectionOoTSceneProperties,
    DragExCollectionOoTRoomProperties,
    DragExCollectionOoTProperties,
    DragExCollectionProperties,
    DragExSceneOoTProperties,
    DragExSceneProperties,
    DragExObjectOoTEmptyPlayerEntryProperties,
    DragExObjectOoTEmptyProperties,
    DragExObjectOoTProperties,
    DragExObjectProperties,
    DragExTargetPanel,
    DragExOoTNewSceneOperator,
    DragExOoTPanel,
    DragExCollectionOoTPanel,
    DragExObjectOoTEmptyPanel,
    DragExBackendDemoOperator,
    DragExOoTExportSceneOperator,
)

cannot_register = False


def register():
    global cannot_register
    cannot_register = False

    print("Hi from", __package__)

    if dragex_backend is None:
        print("DragEx cannot register, dragex_backend is missing")
        cannot_register = True
        return

    print(dir(dragex_backend))

    print(f"{BUILD_ID=}")
    print(f"{dragex_backend.get_build_id()=}")

    if dragex_backend.get_build_id() != BUILD_ID:
        print("DragEx cannot register, dragex_backend has a mismatching BUILD_ID")
        cannot_register = True
        return

    logs_folder_p = Path(
        bpy.utils.extension_path_user(__package__, path="logs", create=True)
    )

    with os.scandir(logs_folder_p) as it:
        logs_entries = [_entry for _entry in it if _entry.is_file()]
    if len(logs_entries) > 200:
        logs_entries.sort(key=lambda entry: entry.stat().st_mtime)
        # delete all entries except the 100 most recent ones
        for entry in logs_entries[:-100]:
            os.unlink(entry.path)

    log_file_p = (
        logs_folder_p
        / f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}.txt"
    )

    dragex_backend.logging.set_log_file(log_file_p)

    dragex_backend.logging.info(f"Now logging to {log_file_p}")

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.dragex = bpy.props.PointerProperty(type=DragExSceneProperties)
    bpy.types.Collection.dragex = bpy.props.PointerProperty(
        type=DragExCollectionProperties
    )
    bpy.types.Object.dragex = bpy.props.PointerProperty(type=DragExObjectProperties)
    bpy.types.Material.dragex = bpy.props.PointerProperty(type=DragExMaterialProperties)

    from . import f64render_dragex

    f64render_dragex.register()


def unregister():
    if cannot_register:
        print("DragEx unregister skipped as it could not register")
        return

    try:
        unregister_impl()
    finally:
        dragex_backend.logging.clear_log_file()


def unregister_impl():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    from . import f64render_dragex

    f64render_dragex.unregister()

    print("Bye from", __package__)
