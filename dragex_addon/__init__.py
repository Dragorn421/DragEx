import datetime
import os
from pathlib import Path

import numpy as np

import bpy

from .build_id import BUILD_ID
from .props import other_mode_props
from .props import tiles_props
from .props import combiner_props
from .props import vals_props
from .props import geometry_mode_props


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


class DragExBackendDemoOperator(bpy.types.Operator):
    bl_idname = "dragex.dragex_backend_demo"
    bl_label = "DragEx backend demo"

    def execute(self, context):
        import time

        start = time.time()

        # TODO trying to not import at the module level, see if this is less jank this way
        # TODO catch ImportError
        import dragex_backend

        print("Hello World")
        assert context.object is not None
        mesh = context.object.data
        assert isinstance(mesh, bpy.types.Mesh)
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
        for mat_index in range(len(context.object.material_slots)):
            mat = context.object.material_slots[mat_index].material
            if mat is None:
                mat_info = None
            else:
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
        mesh_info.write_c("/home/dragorn421/Documents/dragex/dragex_attempt2/output.c")
        end = time.time()
        print("dragex_backend_demo took", end - start, "seconds")
        dragex_backend.logging.flush()  # TODO wrap in try: (code) finally: flush()
        return {"FINISHED"}


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
        return context.material is not None

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


classes = (
    geometry_mode_props.DragExMaterialGeometryModeProperties,
    other_mode_props.DragExMaterialOtherModesProperties,
    tiles_props.DragExMaterialTileProperties,
    tiles_props.DragExMaterialTilesProperties,
    combiner_props.DragExMaterialCombinerProperties,
    vals_props.DragExMaterialValsProperties,
    DragExMaterialProperties,
    DragExMaterialPanel,
    DragExBackendDemoOperator,
)


def register():
    print("Hi from", __package__)

    # TODO trying to not import at the module level, see if this is less jank this way
    # TODO catch ImportError
    import dragex_backend

    print(dir(dragex_backend))

    print(f"{BUILD_ID=}")
    print(f"{dragex_backend.get_build_id()=}")

    assert dragex_backend.get_build_id() == BUILD_ID

    logs_folder_p = Path(
        bpy.utils.extension_path_user(__package__, path="logs", create=True)
    )
    # TODO automatic cleanup of logs_folder_p?
    log_file_p = (
        logs_folder_p
        / f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}.txt"
    )

    dragex_backend.logging.set_log_file(log_file_p)

    print("Now logging to", log_file_p)

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Material.dragex = bpy.props.PointerProperty(type=DragExMaterialProperties)

    from . import f64render_dragex

    f64render_dragex.register()


def unregister():
    try:
        unregister_impl()
    finally:
        import dragex_backend

        dragex_backend.logging.clear_log_file()


def unregister_impl():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    from . import f64render_dragex

    f64render_dragex.unregister()

    print("Bye from", __package__)
