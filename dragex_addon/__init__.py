import abc
from collections.abc import Sequence
import dataclasses
import datetime
import math
import os
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import numpy as np

import bpy
import mathutils

from .build_id import BUILD_ID
from .props import other_mode_props
from .props import tiles_props
from .props import combiner_props
from .props import vals_props
from .props import rsp_props

if TYPE_CHECKING:
    from ..dragex_backend import dragex_backend
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


@dataclasses.dataclass(frozen=True)
class ImageKey:
    image: bpy.types.Image
    format: str
    size: str


@dataclasses.dataclass
class ImageInfos:
    info_by_key: dict[ImageKey, "dragex_backend.MaterialInfoImage"] = dataclasses.field(
        default_factory=dict
    )
    key_by_c_identifier: dict[str, ImageKey] = dataclasses.field(default_factory=dict)


def material_to_MaterialInfo(
    c_identifiers_prefix: str,
    mat: bpy.types.Material,
    image_infos: ImageInfos,
):
    mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
    other_modes = mat_dragex.rdp.other_modes
    tiles = mat_dragex.rdp.tiles
    combiner = mat_dragex.rdp.combiner
    vals = mat_dragex.rdp.vals
    mat_geomode = mat_dragex.rsp

    mat_info_tiles = list[dragex_backend.MaterialInfoTile]()
    for tile in tiles.tiles:
        image: bpy.types.Image | None = tile.image
        if image is None:
            image_info = None
        else:
            image_key = ImageKey(image, tile.format, tile.size)
            image_info = image_infos.info_by_key.get(image_key)
            if image_info is None:
                c_identifier = c_identifiers_prefix + make_c_identifier(image.name)
                if c_identifier in image_infos.key_by_c_identifier:
                    c_identifier = c_identifiers_prefix + make_c_identifier(
                        f"{image.name}_{tile.format}{tile.size}"
                    )
                    c_identifier_candidate = c_identifier
                    i = 2
                    while c_identifier_candidate in image_infos.key_by_c_identifier:
                        c_identifier_candidate = f"{c_identifier}_{i}"
                        i += 1
                    c_identifier = c_identifier_candidate

                width, height = image.size
                image_info = dragex_backend.MaterialInfoImage(
                    c_identifier=c_identifier,
                    width=width,
                    height=height,
                )
                image_infos.info_by_key[image_key] = image_info
                image_infos.key_by_c_identifier[c_identifier] = image_key
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
        name=c_identifiers_prefix + make_c_identifier(mat.name),
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
            zbuffer=mat_geomode.zbuffer,
            lighting=mat_geomode.lighting,
            vertex_colors=mat_geomode.vertex_colors,
            cull_front=mat_geomode.cull_front,
            cull_back=mat_geomode.cull_back,
            fog=mat_geomode.fog,
            uv_gen_spherical=mat_geomode.uv_gen_spherical,
            uv_gen_linear=mat_geomode.uv_gen_linear,
            shade_smooth=mat_geomode.shade_smooth,
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
    image_infos: ImageInfos,
    c_identifiers_prefix: str,
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

    material_infos = list[dragex_backend.MaterialInfo | None]()
    for mat_index in range(len(obj.material_slots)):
        mat = obj.material_slots[mat_index].material
        if mat is None:
            mat_info = None
        else:
            mat_info = material_to_MaterialInfo(c_identifiers_prefix, mat, image_infos)
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
            zbuffer=True,
            lighting=False,
            vertex_colors=False,
            cull_front=False,
            cull_back=True,
            fog=False,
            uv_gen_spherical=False,
            uv_gen_linear=False,
            shade_smooth=False,
        ),
    )
    mesh_info = dragex_backend.create_MeshInfo(
        c_identifiers_prefix + make_c_identifier(obj.name),
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
            mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
            polytype_name = mat_dragex.polytype_name
            if polytype_name:
                colmat = dragex_backend.OoTCollisionMaterial(name=polytype_name)
            else:
                colmat = None
        materials.append(colmat)

    default_material = dragex_backend.OoTCollisionMaterial(name="DEFAULT")

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
        image_infos = ImageInfos()
        mesh_info = mesh_to_mesh_info(
            context.object,
            mesh,
            (transform_zup_to_yup @ mathutils.Matrix.Scale(1, 3)),
            image_infos,
            "",
        )
        with open(
            "/home/dragorn421/Documents/dragex/dragex_attempt2/output.c", "w"
        ) as f:
            mesh_info.write_c(f.fileno())
        end = time.time()
        print("dragex_backend_demo took", end - start, "seconds")
        return {"FINISHED"}

    def execute(self, context):  # type: ignore
        try:
            return self.execute_impl(context)
        finally:
            dragex_backend.logging.flush()


def intlog2(v: int):
    r = round(math.log2(v))
    if 2**r == v:
        return r
    else:
        return None


TMEM_SIZE = 4096


class MaterialMode(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def init(material: bpy.types.Material, prev_mode: str) -> None: ...

    @staticmethod
    @abc.abstractmethod
    def draw(layout: bpy.types.UILayout, material: bpy.types.Material) -> None: ...


class NoneMaterialMode(MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        pass

    @staticmethod
    def draw(layout, material):
        pass


class BasicMaterialMode(MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        BasicMaterialMode.apply_mode_props(material)

    @staticmethod
    def draw(layout, material):
        material_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        mode_basic = material_dragex.modes.basic
        layout.template_ID(mode_basic, "texture", new="image.new", open="image.open")
        texture = mode_basic.texture
        if texture is not None and tuple(texture.size) != (0, 0):
            texture_w, texture_h = texture.size
            if texture_w * texture_h * 2 > TMEM_SIZE:
                layout.label(text="Texture too big: max 32x64 or 64x32", icon="ERROR")
            if texture_w * 2 % 8 != 0:
                layout.label(text="Texture width must be a multiple of 4", icon="ERROR")
            if intlog2(texture_w) is None:
                layout.label(
                    text="Texture width must be a power of 2 for wrapping", icon="INFO"
                )
            if intlog2(texture_h) is None:
                layout.label(
                    text="Texture height must be a power of 2 for wrapping", icon="INFO"
                )
        layout.prop(mode_basic, "shading")
        layout.prop(mode_basic, "alpha_blend")
        layout.prop(mode_basic, "fog")

    @staticmethod
    def apply_mode_props(material):
        material_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        basic_props = material_dragex.modes.basic
        texture: bpy.types.Image | None = basic_props.texture

        tile0 = material_dragex.rdp.tiles.tiles[0]
        tile0.image = texture
        tile0.format = "RGBA"
        tile0.size = "16"
        tile0.address = 0
        tile0.palette = 0
        if texture is not None and tuple(texture.size) != (0, 0):
            # TODO check if s=width, t=height (test with non-square texture)
            texture_w, texture_h = texture.size
            if texture_w * texture_h * 2 > TMEM_SIZE:
                tile0.image = None
            material_dragex.uv_basis_s = texture_w
            material_dragex.uv_basis_t = texture_h
            if texture_w * 2 % 8 != 0:
                tile0.image = None
            tile0.line = texture_w * 2 // 8
            mask_S = intlog2(texture_w)
            mask_T = intlog2(texture_h)
            if mask_S is None:
                tile0.clamp_S = True
                tile0.mask_S = 0
            else:
                tile0.clamp_S = False
                tile0.mask_S = mask_S
            tile0.mirror_S = False
            tile0.shift_S = 0
            if mask_T is None:
                tile0.clamp_T = True
                tile0.mask_T = 0
            else:
                tile0.clamp_T = False
                tile0.mask_T = mask_T
            tile0.mirror_T = False
            tile0.shift_T = 0
            tile0.upper_left_S = 0
            tile0.upper_left_T = 0
            tile0.lower_right_S = texture_w - 1
            tile0.lower_right_T = texture_h - 1

        rsp_props = material_dragex.rsp

        one_cycle = True
        if basic_props.fog:
            one_cycle = False

        rsp_props.zbuffer = True
        if basic_props.shading == "LIGHTING":
            rsp_props.lighting = True
            rsp_props.vertex_colors = False
        elif basic_props.shading == "VERTEX_COLORS":
            rsp_props.lighting = False
            rsp_props.vertex_colors = True
        else:
            assert False, basic_props.shading
        rsp_props.cull_front = False
        rsp_props.cull_back = True
        rsp_props.fog = basic_props.fog
        rsp_props.uv_gen_spherical = False
        rsp_props.uv_gen_linear = False
        rsp_props.shade_smooth = True

        om = material_dragex.rdp.other_modes
        om.atomic_prim = False
        om.cycle_type = "1CYCLE" if one_cycle else "2CYCLE"
        om.persp_tex_en = True
        om.detail_tex_en = False
        om.sharpen_tex_en = False
        om.tex_lod_en = False
        om.tlut_en = False
        om.tlut_type = False
        om.sample_type = True
        om.mid_texel = False
        om.bi_lerp_0 = True
        om.bi_lerp_1 = True
        om.convert_one = False  # TODO ?
        om.key_en = False
        om.rgb_dither_sel = "MAGIC_SQUARE"
        om.alpha_dither_sel = "SAME_AS_RGB"  # ?
        if rsp_props.fog:
            assert not one_cycle
            om.bl_m1a_0 = "FOG_COLOR"
            om.bl_m1b_0 = "SHADE_ALPHA"
            om.bl_m2a_0 = "INPUT"
            om.bl_m2b_0 = "1_MINUS_A"
            om.bl_m1a_1 = "INPUT"
            om.bl_m1b_1 = "INPUT_ALPHA"
            om.bl_m2a_1 = "MEMORY"
            om.bl_m2b_1 = (
                "1_MINUS_A"
                if basic_props.alpha_blend == "TRANSPARENT"
                else "MEMORY_COVERAGE"
            )
        else:
            om.bl_m1a_0 = "INPUT"
            om.bl_m1b_0 = "INPUT_ALPHA"
            om.bl_m2a_0 = "MEMORY"
            om.bl_m2b_0 = (
                "1_MINUS_A"
                if basic_props.alpha_blend == "TRANSPARENT"
                else "MEMORY_COVERAGE"
            )
            if one_cycle:
                om.bl_m1a_1 = om.bl_m1a_0
                om.bl_m1b_1 = om.bl_m1b_0
                om.bl_m2a_1 = om.bl_m2a_0
                om.bl_m2b_1 = om.bl_m2b_0
            else:
                om.bl_m1a_1 = "INPUT"
                om.bl_m1b_1 = "0"
                om.bl_m2a_1 = "INPUT"
                om.bl_m2b_1 = "1"
        if basic_props.alpha_blend in {"OPAQUE", "CUTOUT"}:
            om.force_blend = False
            om.alpha_cvg_select = True
            om.cvg_x_alpha = basic_props.alpha_blend == "CUTOUT"
            om.z_mode = "OPAQUE"
            om.cvg_dest = "CLAMP"
            om.color_on_cvg = False
            om.z_update_en = True
        elif basic_props.alpha_blend == "TRANSPARENT":
            om.force_blend = True
            om.alpha_cvg_select = False
            om.cvg_x_alpha = False
            om.z_mode = "TRANSPARENT"
            om.cvg_dest = "WRAP"
            om.color_on_cvg = True
            om.z_update_en = False
        else:
            assert False, basic_props.alpha_blend
        om.image_read_en = True
        om.z_compare_en = True
        om.antialias_en = True
        om.z_source_sel = False
        om.dither_alpha_en = False
        om.alpha_compare_en = False

        cb = material_dragex.rdp.combiner
        if texture is None:
            cb.rgb_A_0 = "0"
            cb.rgb_B_0 = "0"
            cb.rgb_C_0 = "0"
            cb.rgb_D_0 = "SHADE"
        else:
            cb.rgb_A_0 = "TEX0"
            cb.rgb_B_0 = "0"
            cb.rgb_C_0 = "SHADE"
            cb.rgb_D_0 = "0"
        if basic_props.alpha_blend in {"CUTOUT", "TRANSPARENT"}:
            if basic_props.fog:
                cb.alpha_A_0 = "0"
                cb.alpha_B_0 = "0"
                cb.alpha_C_0 = "0"
                cb.alpha_D_0 = "1" if texture is None else "TEX0"
            else:
                if texture is None:
                    cb.alpha_A_0 = "0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "0"
                    cb.alpha_D_0 = "SHADE"
                else:
                    cb.alpha_A_0 = "TEX0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "SHADE"
                    cb.alpha_D_0 = "0"
        else:
            cb.alpha_A_0 = "0"
            cb.alpha_B_0 = "0"
            cb.alpha_C_0 = "0"
            cb.alpha_D_0 = "1"
        if one_cycle:
            cb.rgb_A_1 = cb.rgb_A_0
            cb.rgb_B_1 = cb.rgb_B_0
            cb.rgb_C_1 = cb.rgb_C_0
            cb.rgb_D_1 = cb.rgb_D_0
            cb.alpha_A_1 = cb.alpha_A_0
            cb.alpha_B_1 = cb.alpha_B_0
            cb.alpha_C_1 = cb.alpha_C_0
            cb.alpha_D_1 = cb.alpha_D_0
        else:
            cb.rgb_A_1 = "0"
            cb.rgb_B_1 = "0"
            cb.rgb_C_1 = "0"
            cb.rgb_D_1 = "COMBINED"
            cb.alpha_A_1 = "0"
            cb.alpha_B_1 = "0"
            cb.alpha_C_1 = "0"
            cb.alpha_D_1 = "COMBINED"

    @staticmethod
    def on_mode_prop_update(_self, context: bpy.types.Context):
        material = context.material
        assert material is not None
        BasicMaterialMode.apply_mode_props(material)


class DragExMaterialModesBasicProperties(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(
        name="Texture",
        type=bpy.types.Image,
        update=BasicMaterialMode.on_mode_prop_update,
    )
    shading: bpy.props.EnumProperty(
        name="Shading",
        description="Pick the shade color source for vertices",
        items=(
            ("LIGHTING", "Lighting", "Vertices are colored by the active lights"),
            (
                "VERTEX_COLORS",
                "Vertex Colors",
                "Vertices are colored according to the painted vertex colors",
            ),
        ),
        default="LIGHTING",
        update=BasicMaterialMode.on_mode_prop_update,
    )
    alpha_blend: bpy.props.EnumProperty(
        name="Alpha Blend",
        description="Choose how the alpha affects the material",
        items=(
            ("OPAQUE", "Opaque", "Material is fully opaque"),
            (
                "CUTOUT",
                "Cutout",
                (
                    "Material is opaque with holes (fully transparent spots)"
                    " where the alpha is below threshold (e.g. fences)"
                ),
            ),
            (
                "TRANSPARENT",
                "Transparent",
                (
                    "Material is transparent, drawing some geometry that"
                    " can be seen through (e.g. colored glass)"
                ),
            ),
        ),
        default="OPAQUE",
        update=BasicMaterialMode.on_mode_prop_update,
    )
    fog: bpy.props.BoolProperty(
        name="Fog",
        description=(
            "Whether this material is affected by fog"
            " (blend with the fog color as the geometry is further from the camera)"
        ),
        default=True,
        update=BasicMaterialMode.on_mode_prop_update,
    )


class DragExMaterialModesProperties(bpy.types.PropertyGroup):
    basic_: bpy.props.PointerProperty(type=DragExMaterialModesBasicProperties)

    @property
    def basic(self) -> DragExMaterialModesBasicProperties:
        return self.basic_


class FullMaterialMode(MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        pass

    @staticmethod
    def draw(layout, material):
        mat_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        mat_geomode = mat_dragex.rsp
        other_modes = mat_dragex.rdp.other_modes
        combiner = mat_dragex.rdp.combiner
        vals = mat_dragex.rdp.vals
        tiles = mat_dragex.rdp.tiles.tiles
        layout.prop(mat_geomode, "zbuffer")
        layout.prop(mat_geomode, "lighting")
        layout.prop(mat_geomode, "vertex_colors")
        layout.prop(mat_geomode, "cull_front")
        layout.prop(mat_geomode, "cull_back")
        layout.prop(mat_geomode, "fog")
        layout.prop(mat_geomode, "uv_gen_spherical")
        layout.prop(mat_geomode, "uv_gen_linear")
        layout.prop(mat_geomode, "shade_smooth")
        layout.prop(mat_dragex, "uv_basis_s")
        layout.prop(mat_dragex, "uv_basis_t")
        layout.prop(vals, "primitive_depth_z")
        layout.prop(vals, "primitive_depth_dz")
        layout.prop(vals, "fog_color")
        layout.prop(vals, "blend_color")
        layout.prop(vals, "min_level")
        layout.prop(vals, "prim_lod_frac")
        layout.prop(vals, "primitive_color")
        layout.prop(vals, "environment_color")
        box = layout.box()
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
        box = layout.box()
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
            box = layout.box()
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


material_modes_dict: dict[str, type[MaterialMode]] = {
    "NONE": NoneMaterialMode,
    "BASIC": BasicMaterialMode,
    "FULL": FullMaterialMode,
}

material_mode_items = (
    # TODO add descriptions
    ("NONE", "None", ""),
    ("BASIC", "Basic", ""),
    ("FULL", "Full", ""),
)


class DragExMaterialRDPProperties(bpy.types.PropertyGroup):
    other_modes_: bpy.props.PointerProperty(
        type=other_mode_props.DragExMaterialOtherModesProperties
    )
    tiles_: bpy.props.PointerProperty(type=tiles_props.DragExMaterialTilesProperties)
    combiner_: bpy.props.PointerProperty(
        type=combiner_props.DragExMaterialCombinerProperties
    )
    vals_: bpy.props.PointerProperty(type=vals_props.DragExMaterialValsProperties)

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


def search_polytype_names(self, context: bpy.types.Context, edit_text: str):
    if not hasattr(context, "object") or context.object is None:
        return list[str]()
    obj = context.object
    search = edit_text.lower()
    used_polytypes = set[str]()
    for coll in bpy.data.collections.values():
        assert coll is not None
        coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
        if coll_dragex.oot.type == "SCENE" and obj in coll.all_objects.values():
            for obj in coll.all_objects:
                if obj.type == "MESH":
                    for mat_slot in obj.material_slots:
                        mat = mat_slot.material
                        if mat is not None:
                            mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
                            if search in mat_dragex.polytype_name.lower():
                                used_polytypes.add(mat_dragex.polytype_name)
    return sorted(used_polytypes)


class DragExMaterialProperties(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(
        items=material_mode_items,
        default="NONE",
    )
    modes_: bpy.props.PointerProperty(type=DragExMaterialModesProperties)

    @property
    def modes(self) -> DragExMaterialModesProperties:
        return self.modes_

    uv_basis_s: bpy.props.IntProperty(name="UV Basis S", min=1, default=1)
    uv_basis_t: bpy.props.IntProperty(name="UV Basis T", min=1, default=1)

    rdp_: bpy.props.PointerProperty(type=DragExMaterialRDPProperties)

    rsp_: bpy.props.PointerProperty(type=rsp_props.DragExMaterialRSPProperties)

    @property
    def rdp(self) -> DragExMaterialRDPProperties:
        return self.rdp_

    @property
    def rsp(self) -> rsp_props.DragExMaterialRSPProperties:
        return self.rsp_

    polytype_name: bpy.props.StringProperty(
        name="Polytype",
        description=(
            "The name of the polytype (surface type) this material uses"
            " for exporting collision, as found in table_polytypes.h"
        ),
        default="DEFAULT",
        search=search_polytype_names,
    )


class DragExMaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_dragex"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        scene_dragex: DragExSceneProperties = context.scene.dragex  # type: ignore
        return scene_dragex.target != "NONE" and context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
        self.layout.operator(DragExSetMaterialModeOperator.bl_idname)
        material_modes_dict[mat_dragex.mode].draw(self.layout, mat)


class DragExMaterialOoTCollisionPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_dragex_oot_collision"
    bl_label = "DragEx OoT Collision"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        scene_dragex: DragExSceneProperties = context.scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL" and context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
        self.layout.prop(mat_dragex, "polytype_name")


class DragExSetMaterialModeOperator(bpy.types.Operator):
    bl_idname = "dragex.set_material_mode"
    bl_label = "DragEx Set Material Mode"
    bl_property = "mode"

    def get_modes(self, context: bpy.types.Context | None):
        return material_mode_items

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=get_modes,
    )

    @classmethod
    def poll(cls, context):
        return hasattr(context, "material") and context.material is not None

    def execute(self, context):  # type: ignore
        material = context.material
        assert material is not None
        material_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        prev_mode = material_dragex.mode
        material_dragex.mode = self.mode
        material_modes_dict[self.mode].init(material, prev_mode)
        if context.region is not None:
            context.region.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):  # type: ignore
        assert context.window_manager is not None
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}


@dataclasses.dataclass(eq=False)
class OoTRoomShape(abc.ABC):
    image_infos: ImageInfos


@dataclasses.dataclass(eq=False)  # Use id-based equality and hashing
class OoTRoom:
    c_identifier: str
    shape: OoTRoomShape


@dataclasses.dataclass(eq=False)
class OoTRoomShapeNormal(OoTRoomShape):
    entries_opa: Sequence["dragex_backend.MeshInfo"]
    entries_xlu: Sequence["dragex_backend.MeshInfo"]


@dataclasses.dataclass(eq=False)
class OoTScene:
    c_identifier: str
    rooms: list[OoTRoom]
    collision: "dragex_backend.OoTCollisionMesh"
    positions: dict[str, tuple[int, int, int]]
    rotations_yxz: dict[str, mathutils.Euler]
    yaws: dict[str, float]  # radians


class CollectMapException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def collect_map(coll_scene: bpy.types.Collection, export_options: "ExportOptions"):
    scene_c_identifier = make_c_identifier(coll_scene.name)

    transform_inverted = export_options.transform.inverted()

    room_colls = dict[int, bpy.types.Collection]()
    for coll in coll_scene.children_recursive:
        coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
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

    for i in range(n_rooms):
        room_coll = room_colls[i]
        room_c_identifier = make_c_identifier(room_coll.name)
        room_coll_dragex: DragExCollectionProperties = room_coll.dragex  # type: ignore
        entries_opa = list[dragex_backend.MeshInfo]()
        entries_xlu = list[dragex_backend.MeshInfo]()
        image_infos = ImageInfos()
        for obj in room_coll.all_objects:
            if obj.type == "EMPTY":
                obj_dragex: DragExObjectProperties = obj.dragex  # type: ignore
                ...
            if obj.type == "MESH":
                assert isinstance(obj.data, bpy.types.Mesh)
                # TODO this is inefficient if mesh is shared between rooms
                mesh_info = mesh_to_mesh_info(
                    obj,
                    obj.data,
                    export_options.transform,
                    image_infos,
                    f"{scene_c_identifier}_{room_c_identifier}_",
                )
                # TODO prop to set draw layer opa/xlu
                entries_opa.append(mesh_info)

        shape = OoTRoomShapeNormal(
            image_infos=image_infos,
            entries_opa=entries_opa,
            entries_xlu=entries_xlu,
        )

        room = OoTRoom(
            c_identifier=room_c_identifier,
            shape=shape,
        )
        rooms.append(room)

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

    positions = dict[str, tuple[int, int, int]]()
    rotations_yxz = dict[str, mathutils.Euler]()
    yaws = dict[str, float]()
    for obj in coll_scene.all_objects:
        if obj.type == "EMPTY":
            obj_dragex: DragExObjectProperties = obj.dragex  # type: ignore

            if obj_dragex.oot.empty.export_pos:
                pos = export_options.transform @ obj.location
                positions[obj_dragex.oot.empty.export_pos_name] = (
                    round(pos.x),
                    round(pos.y),
                    round(pos.z),
                )

            saved_rotation_mode = obj.rotation_mode
            try:
                obj.rotation_mode = "QUATERNION"
                obj_rot_quaternion = obj.rotation_quaternion.copy()
            finally:
                obj.rotation_mode = saved_rotation_mode

            # TODO check this is correct
            # 1) check transform @ rot @ 1/transform is correct
            # 2) check Euler ZXY does correspond to oot's YXZ
            obj_transformed_rot_matrix = (
                export_options.transform
                @ obj_rot_quaternion.to_matrix()
                @ transform_inverted
            )

            if obj_dragex.oot.empty.export_rot_yxz:
                rotations_yxz[obj_dragex.oot.empty.export_rot_yxz_name] = (
                    obj_transformed_rot_matrix.to_euler("ZXY")
                )

            if obj_dragex.oot.empty.export_yaw:
                yaws[obj_dragex.oot.empty.export_yaw_name] = (
                    obj_transformed_rot_matrix.to_euler("ZXY").y
                )

    oot_scene = OoTScene(
        c_identifier=scene_c_identifier,
        rooms=rooms,
        collision=collision,
        positions=positions,
        rotations_yxz=rotations_yxz,
        yaws=yaws,
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
    decomp_repo_p: Path


def export_coll_scene(
    coll_scene: bpy.types.Collection, out_dir_p: Path, export_options: ExportOptions
):
    oot_scene = collect_map(coll_scene, export_options)

    from pprint import pprint

    pprint(oot_scene)

    map_prefix_lower = oot_scene.c_identifier.lower()
    map_prefix_upper = oot_scene.c_identifier.upper()

    exported_dir_p = out_dir_p / "exported"
    exported_dir_p.mkdir(exist_ok=True)

    with FDManager() as fd_manager:
        collision_inc_c_fd = fd_manager.open_w(exported_dir_p / f"collision.inc.c")

        col_header_name = f"{map_prefix_lower}_Col"

        col_vtx_list_name = f"{map_prefix_lower}_VtxList"
        col_poly_list_name = f"{map_prefix_lower}_PolyList"
        col_surface_types_name = f"{map_prefix_lower}_SurfaceTypes"
        col_bg_cam_list_name = f"{map_prefix_lower}_BgCamList"

        with open(collision_inc_c_fd, "w", closefd=False) as f:
            f.write(
                """\
#include "collision.h"

#include "stddef.h"
#include "array_count.h"
#include "bgcheck.h"
#include "z_math.h"

"""
            )

        collision_bounds = oot_scene.collision.write_c(
            collision_inc_c_fd,
            map_prefix_upper,
            col_vtx_list_name,
            col_poly_list_name,
            col_surface_types_name,
        )

        with open(collision_inc_c_fd, "w", closefd=False) as f:
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
                f"    {col_bg_cam_list_name},\n"
                f"    0,\n"  # TODO waterboxes
                f"    NULL,\n"
                "};\n"
                "\n"
            )

        (exported_dir_p / "collision.h").write_text(
            f"""\
#include "bgcheck.h"

extern CollisionHeader {col_header_name};
"""
        )

    for i, room in enumerate(oot_scene.rooms):
        with FDManager() as fd_manager:
            room_fd = fd_manager.open_w(exported_dir_p / f"room_{i}_shape.inc.c")

            room_shape = room.shape

            room_shape_name = f"{map_prefix_lower}_room_{i}_RoomShape"

            if isinstance(room.shape, OoTRoomShapeNormal):
                (exported_dir_p / f"room_{i}_shape.h").write_text(
                    f"""\
#include "room.h"

extern RoomShapeNormal {room_shape_name};
"""
                )
            else:
                raise NotImplementedError(type(room.shape))

            with open(room_fd, "w", closefd=False) as f:
                f.write(
                    f"""\
#include "room_{i}_shape.h"

#include "ultra64.h"
#include "array_count.h"
#include "room.h"

"""
                )

                for (
                    c_identifier,
                    image_key,
                ) in room_shape.image_infos.key_by_c_identifier.items():
                    image_file_stem = (
                        f"{c_identifier}.{image_key.format.lower()}{image_key.size}"
                    )
                    # TODO save() may set the image's filepath as a side-effect?
                    # (not in 4.2.11 at least, but recent versions (which?) have a save_copy argument to save())
                    # if so, need to copy() the datablock before save to avoid modifying it
                    image_key.image.save(
                        filepath=str(exported_dir_p / f"{image_file_stem}.png"),
                    )
                    image_inc_c_p = (
                        PurePosixPath(
                            *exported_dir_p.relative_to(
                                export_options.decomp_repo_p
                            ).parts
                        )
                        / f"{image_file_stem}.inc.c"
                    )
                    f.write(
                        f"u64 {c_identifier}[] = "
                        "{\n"
                        f'#include "{image_inc_c_p}"\n'
                        "};\n"
                        "\n"
                    )

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
                    dlists_entries_name = (
                        f"{map_prefix_lower}_{room.c_identifier}_DListsEntries"
                    )
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

    with (exported_dir_p / "positions.h").open("w") as f:
        f.write(
            f"#ifndef {map_prefix_upper}_POSITIONS_H\n"
            f"#define {map_prefix_upper}_POSITIONS_H\n"
            "\n"
        )
        for name, (x, y, z) in oot_scene.positions.items():
            f.write(f"#define {name} {x}, {y}, {z}\n")
        f.write("\n")
        for name, rot in oot_scene.rotations_yxz.items():
            f.write(f"#define {name} ")
            f.write(", ".join(f"DEG_TO_BINANG({math.degrees(_v)})" for _v in rot))
            f.write("\n")
        f.write("\n")
        for name, yaw in oot_scene.yaws.items():
            f.write(f"#define {name} DEG_TO_BINANG({math.degrees(yaw)})\n")
        f.write("\n")
        f.write("\n" "#endif\n")

    replacements = {
        "map_prefix_lower": map_prefix_lower,
        "MAP_PREFIX_UPPER": map_prefix_upper,
    }

    def apply_replacements(text: str):
        for repl_from, repl_to in replacements.items():
            text = text.replace(repl_from, repl_to)
        return text

    map_template_dir_p = Path(__file__).parent / "map_template"

    (out_dir_p / "glue").mkdir(exist_ok=True)

    def write_if_missing(p: Path, text: str):
        if not p.exists():
            p.write_text(text)

    for p in (
        Path("glue/glue_scene.c"),
        Path("glue/glue_scene.h"),
        Path("header_scene.inc.c"),
        Path("table_cameras.h"),
        Path("table_envlightsettings.h"),
        Path("table_polytypes.h"),
        Path("table_spawns.h"),
    ):
        write_if_missing(
            out_dir_p / p,
            apply_replacements((map_template_dir_p / p).read_text()),
        )

    spec_frags = []
    spec_frags.append(
        apply_replacements((map_template_dir_p / "frag_spec_scene.inc").read_text())
    )

    frag_table_rooms_h_template = (
        map_template_dir_p / "frag_table_rooms.h"
    ).read_text()
    glue_room_c_template = (map_template_dir_p / "glue/glue_room_0.c").read_text()
    glue_room_h_template = (map_template_dir_p / "glue/glue_room_0.h").read_text()
    header_room_inc_c_template = (
        map_template_dir_p / "header_room_0.inc.c"
    ).read_text()
    table_actors_room_h_template = (
        map_template_dir_p / "table_actors_room_0.h"
    ).read_text()
    table_objects_room_h_template = (
        map_template_dir_p / "table_objects_room_0.h"
    ).read_text()
    frag_spec_room_inc_template = (
        map_template_dir_p / "frag_spec_room.inc"
    ).read_text()

    table_rooms_frags = []
    for i, room in enumerate(oot_scene.rooms):
        replacements_room = replacements.copy()
        replacements_room.update(
            {
                "ROOM_NAME": room.c_identifier.upper(),
                "ROOM_NUMBER": f"{i}",
            }
        )

        def apply_replacements_room(text: str):
            for repl_from, repl_to in replacements_room.items():
                text = text.replace(repl_from, repl_to)
            return text

        table_rooms_frags.append(apply_replacements_room(frag_table_rooms_h_template))

        write_if_missing(
            out_dir_p / f"glue/glue_room_{i}.c",
            apply_replacements_room(glue_room_c_template),
        )
        write_if_missing(
            out_dir_p / f"glue/glue_room_{i}.h",
            apply_replacements_room(glue_room_h_template),
        )
        write_if_missing(
            out_dir_p / f"header_room_{i}.inc.c",
            apply_replacements_room(header_room_inc_c_template),
        )
        write_if_missing(
            out_dir_p / f"table_actors_room_{i}.h",
            apply_replacements_room(table_actors_room_h_template),
        )
        write_if_missing(
            out_dir_p / f"table_objects_room_{i}.h",
            apply_replacements_room(table_objects_room_h_template),
        )

        spec_frags.append(apply_replacements_room(frag_spec_room_inc_template))

    write_if_missing(
        out_dir_p / "table_rooms.h",
        "".join(table_rooms_frags),
    )

    write_if_missing(
        out_dir_p / "spec.inc",
        "\n".join(spec_frags),
    )


class DragExOoTExportSceneOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_export_scene"
    bl_label = "DragEx OoT Export Scene"

    def scene_coll_name_search(self, context: bpy.types.Context, edit_text: str):
        edit_text = edit_text.lower()
        scene = context.scene
        assert scene is not None
        for coll in scene.collection.children_recursive:
            coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
            if coll_dragex.oot.type == "SCENE":
                if edit_text in coll.name.lower():
                    yield coll.name

    scene_coll_name: bpy.props.StringProperty(
        name="Scene",
        description="OoT scene collection to export",
        search=scene_coll_name_search,  # type: ignore
        search_options=set(),
    )

    directory: bpy.props.StringProperty(subtype="DIR_PATH", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def execute(self, context):  # type: ignore
        if self.scene_coll_name == "":
            self.report({"ERROR_INVALID_INPUT"}, "No scene given")
            return {"CANCELLED"}
        coll_scene_to_export = bpy.data.collections[self.scene_coll_name]
        export_directory = Path(self.directory)

        scene = context.scene
        assert scene is not None
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore

        # TODO pass in the decomp repo path as a prop or something instead
        candidate_decomp_repo_p = export_directory.parent
        while not (candidate_decomp_repo_p / "spec").exists():
            parent_p = candidate_decomp_repo_p.parent
            if parent_p == candidate_decomp_repo_p:
                self.report(
                    {"ERROR"},
                    (
                        "Cannot find decomp repo (a folder with spec)"
                        f" in parents of {export_directory}"
                    ),
                )
                return {"CANCELLED"}
            candidate_decomp_repo_p = parent_p
        decomp_repo_p = candidate_decomp_repo_p

        export_coll_scene(
            coll_scene_to_export,
            export_directory,
            ExportOptions(
                transform=(
                    transform_zup_to_yup
                    @ mathutils.Matrix.Scale(1 / scene_dragex.oot.scale, 3)
                ),
                decomp_repo_p=decomp_repo_p,
            ),
        )

        return {"FINISHED"}

    def invoke(self, context, event):  # type: ignore
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


def validate_export_pos_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = make_c_identifier(self.export_pos_name)
    if self.export_pos_name != c_identifier:
        self.export_pos_name = c_identifier


def validate_export_rot_yxz_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = make_c_identifier(self.export_rot_yxz_name)
    if self.export_rot_yxz_name != c_identifier:
        self.export_rot_yxz_name = c_identifier


def validate_export_yaw_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = make_c_identifier(self.export_yaw_name)
    if self.export_yaw_name != c_identifier:
        self.export_yaw_name = c_identifier


class DragExObjectOoTEmptyProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description="Type of OoT empty object",
        default="NONE",
        items=(("NONE", "None", "No type. A regular empty object"),),
    )

    export_pos: bpy.props.BoolProperty(
        name="Export Position",
        description=(
            "On export, write the location of this empty to a positions.h file"
        ),
    )
    export_pos_name: bpy.props.StringProperty(
        name="Export Position Name",
        description="The name of the macro to name the exported location as",
        default="POS_",
        update=validate_export_pos_name,
    )

    export_rot_yxz: bpy.props.BoolProperty(
        name="Export Rotation",
        description=(
            "On export, write the rotation (as Euler YXZ, as used by Actor_Draw)"
            " of this empty to a positions.h file"
        ),
    )
    export_rot_yxz_name: bpy.props.StringProperty(
        name="Export Rotation Name",
        description="The name of the macro to name the exported rotation as",
        default="ROT_",
        update=validate_export_rot_yxz_name,
    )

    export_yaw: bpy.props.BoolProperty(
        name="Export Yaw",
        description=(
            "On export, write the yaw (rotation around the vertical axis)"
            " of this empty to a positions.h file"
        ),
    )
    export_yaw_name: bpy.props.StringProperty(
        name="Export Yaw Name",
        description="The name of the macro to name the exported yaw as",
        default="YAW_",
        update=validate_export_yaw_name,
    )


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
        dragex: DragExSceneProperties = scene.dragex  # type: ignore
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

    def execute(self, context):  # type: ignore
        map_name: str = self.map_name
        scene_name = f"{map_name} Scene"
        room_names = [f"Room {_i}" for _i in range(self.n_rooms)]

        def are_names_taken(scene_name: str, room_names: list[str]):
            return scene_name in bpy.data.collections or any(
                _room_name in bpy.data.collections for _room_name in room_names
            )

        if are_names_taken(scene_name, room_names):
            cont = True
            i = 0
            while cont:
                scene_name = f"{map_name} Scene"
                room_names = [f"{map_name} Room {_i}" for _i in range(self.n_rooms)]
                cont = are_names_taken(scene_name, room_names)
                if cont:
                    i += 1
                    map_name = self.map_name + f".{i:03}"

        scene = context.scene
        assert scene is not None
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore

        scene_coll = bpy.data.collections.new(scene_name)
        scene_coll_dragex: DragExCollectionProperties = scene_coll.dragex  # type: ignore
        scene_coll_dragex.oot.type = "SCENE"

        scale = scene_dragex.oot.scale
        room_colls = list[bpy.types.Collection]()
        for room_number, room_name in enumerate(room_names):
            room_coll = bpy.data.collections.new(room_name)
            room_colls.append(room_coll)
            room_coll_dragex: DragExCollectionProperties = room_coll.dragex  # type: ignore
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

        spawn_empty_obj = bpy.data.objects.new(f"{map_name} Spawn", None)
        spawn_empty_obj_dragex: DragExObjectProperties = spawn_empty_obj.dragex  # type: ignore
        spawn_empty_obj.location = (0, 0, 0)
        spawn_empty_obj.empty_display_type = "ARROWS"
        spawn_empty_obj_dragex.oot.empty.export_pos = True
        spawn_empty_obj_dragex.oot.empty.export_pos_name = (
            f"POS_{make_c_identifier(scene_name).upper()}_SPAWN"
        )
        scene_coll.objects.link(spawn_empty_obj)

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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        assert self.layout is not None
        scene = context.scene
        assert scene is not None
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        coll = context.collection
        assert coll is not None
        coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL" and obj.type == "EMPTY"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        obj = context.object
        assert obj is not None
        obj_dragex: DragExObjectProperties = obj.dragex  # type: ignore
        layout.prop(obj_dragex.oot.empty, "type")

        layout.prop(obj_dragex.oot.empty, "export_pos")
        if obj_dragex.oot.empty.export_pos:
            layout.prop(obj_dragex.oot.empty, "export_pos_name")

        layout.prop(obj_dragex.oot.empty, "export_rot_yxz")
        if obj_dragex.oot.empty.export_rot_yxz:
            layout.prop(obj_dragex.oot.empty, "export_rot_yxz_name")

        layout.prop(obj_dragex.oot.empty, "export_yaw")
        if obj_dragex.oot.empty.export_yaw:
            layout.prop(obj_dragex.oot.empty, "export_yaw_name")

        if (
            obj_dragex.oot.empty.export_pos
            or obj_dragex.oot.empty.export_rot_yxz_name
            or obj_dragex.oot.empty.export_yaw_name
        ):
            is_part_of_a_scene = False
            for coll in bpy.data.collections.values():
                assert coll is not None
                coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
                if coll_dragex.oot.type == "SCENE" and obj in coll.all_objects.values():
                    is_part_of_a_scene = True
            if not is_part_of_a_scene:
                layout.label(
                    text=(
                        "This empty is not part of any scene,"
                        " so it will be ignored on export"
                    ),
                    icon="ERROR",
                )


classes = (
    rsp_props.DragExMaterialRSPProperties,
    other_mode_props.DragExMaterialOtherModesProperties,
    tiles_props.DragExMaterialTileProperties,
    tiles_props.DragExMaterialTilesProperties,
    combiner_props.DragExMaterialCombinerProperties,
    vals_props.DragExMaterialValsProperties,
    DragExMaterialModesBasicProperties,
    DragExMaterialModesProperties,
    DragExMaterialRDPProperties,
    DragExMaterialProperties,
    DragExMaterialPanel,
    DragExMaterialOoTCollisionPanel,
    DragExCollectionOoTSceneProperties,
    DragExCollectionOoTRoomProperties,
    DragExCollectionOoTProperties,
    DragExCollectionProperties,
    DragExSceneOoTProperties,
    DragExSceneProperties,
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
    DragExSetMaterialModeOperator,
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

    assert __package__ is not None
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

    bpy.types.Scene.dragex = bpy.props.PointerProperty(type=DragExSceneProperties)  # type: ignore
    bpy.types.Collection.dragex = bpy.props.PointerProperty(  # type: ignore
        type=DragExCollectionProperties
    )
    bpy.types.Object.dragex = bpy.props.PointerProperty(type=DragExObjectProperties)  # type: ignore
    bpy.types.Material.dragex = bpy.props.PointerProperty(type=DragExMaterialProperties)  # type: ignore

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
