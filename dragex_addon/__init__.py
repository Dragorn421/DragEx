from collections.abc import Sequence

import numpy as np

import bpy

from .build_id import BUILD_ID


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
        else:
            if active_color_attribute.domain == "CORNER":
                if active_color_attribute.data_type in {"FLOAT_COLOR", "BYTE_COLOR"}:
                    assert isinstance(
                        active_color_attribute,
                        (
                            bpy.types.FloatColorAttribute,
                            bpy.types.ByteColorAttribute,
                        ),
                    )
                    # Note: for ByteColorAttribute too the color uses floats
                    buf_corners_color = new_float_buf(4 * len(mesh.loops))
                    active_color_attribute.data.foreach_get("color", buf_corners_color)
                else:
                    raise NotImplementedError(active_color_attribute.data_type)
            else:
                # TODO at least POINT (vertex) colors?
                raise NotImplementedError(active_color_attribute.domain)

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
            buf_loops_uv,
            material_infos,
            default_material_info,
        )
        mesh_info.write_c("/home/dragorn421/Documents/dragex/dragex_attempt2/output.c")
        end = time.time()
        print("dragex_backend_demo took", end - start, "seconds")
        return {"FINISHED"}


class DragExMaterialGeometryModeProperties(bpy.types.PropertyGroup):
    lighting: bpy.props.BoolProperty(
        name="G_LIGHTING",
        description=(
            "When on, G_LIGHTING causes the vertex shading to be computed based on"
            " vertex normals and current lights.\n"
            "When off, the vertex shading is simply taken from vertex colors."
        ),
    )


blender_P_M_inputs_items = (
    (
        "INPUT",
        "Input",
        "First cycle: output color from Color Combiner final stage; Second cycle: output color from first blender cycle",
    ),
    ("MEMORY", "Memory", "Memory color from framebuffer"),
    ("BLEND_COLOR", "Blend Color", "Blend color register RGB"),
    ("FOG_COLOR", "Fog Color", "Fog color register RGB "),
)
blender_A_inputs_items = (
    ("INPUT_ALPHA", "Input Alpha", "Output alpha from Color Combiner final stage"),
    ("FOG_ALPHA", "Fog Alpha", "Fog color register Alpha"),
    ("SHADE_ALPHA", "Shade Alpha", "Shade Alpha (interpolated per-pixel)"),
    ("0", "0", "Fixed 0.0"),
)
blender_B_inputs_items = (
    ("1_MINUS_A", "1 - A", "1.0 - A, where A is the other alpha input"),
    ("MEMORY_COVERAGE", "Memory Coverage", "Memory coverage from framebuffer"),
    ("1", "1", "Fixed 1.0"),
    ("0", "0", "Fixed 0.0"),
)


# names and description from https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x2F_-_Set_Other_Modes (CC BY-SA 4.0)
# TODO cleanup descriptions, may need to turn some bool props into enum props (like tlut_type)
class DragExMaterialOtherModesProperties(bpy.types.PropertyGroup):
    atomic_prim: bpy.props.BoolProperty(
        name="Atomic Prim",
        description="Enables span buffer coherency, forces active span segments to be written to the frame buffer before reading new span segments",
    )
    cycle_type: bpy.props.EnumProperty(
        name="Cycle Type",
        description="Determines pipeline mode. Either 1-Cycle (0), 2-Cycle (1), COPY (2), FILL (3)",
        items=(
            ("1CYCLE", "1-Cycle", ""),
            ("2CYCLE", "2-Cycle", ""),
            ("COPY", "COPY", ""),
            ("FILL", "FILL", ""),
        ),
    )
    persp_tex_en: bpy.props.BoolProperty(
        name="Perspective Texture",
        description="Enables perspective correction of texture coordinates",
    )
    detail_tex_en: bpy.props.BoolProperty(
        name="Detail Texture",
        description='Enables "detail texture" mode in Texture LOD',
    )
    sharpen_tex_en: bpy.props.BoolProperty(
        name="Sharpen Texture",
        description='Enables "sharpen texture" mode in Texture LOD',
    )
    tex_lod_en: bpy.props.BoolProperty(
        name="Texture LOD",
        description="Enables Texture Level of Detail (LOD)",
    )
    tlut_en: bpy.props.BoolProperty(
        name="TLUT",
        description="Enables Texture Look-Up Table (TLUT) sampling. Texels are first fetched from low TMEM that are then used to index a palette in high TMEM to find the final color values.",
    )
    tlut_type: bpy.props.BoolProperty(
        name="TLUT Type",
        description="Determines TLUT texel format. Either RGBA16 (0) or IA16 (1)",
    )
    sample_type: bpy.props.BoolProperty(
        name="Sample Type",
        description="Determines texel sampling mode. Either point-sampled (0) or 2x2 bilinear (1)",
    )
    mid_texel: bpy.props.BoolProperty(
        name="Mid Texel",
        description="Determines bilinear filter mode. Either 3-point (0) or average mode (1)",
    )
    bi_lerp_0: bpy.props.BoolProperty(
        name="bi_lerp_0",
        description="Determines texture filter mode for the first cycle. Either YUV to RGB conversion (See Set Convert) (0) or bilinear filter (1)",
    )
    bi_lerp_1: bpy.props.BoolProperty(
        name="bi_lerp_1",
        description="Determines texture filter mode for the second cycle. Either YUV to RGB conversion (See Set Convert) (0) or bilinear filter (1)",
    )
    convert_one: bpy.props.BoolProperty(
        name="Convert One",
        description="Determines the input to the second texture filter stage. Either the sample from the second stage of texture sampling (0) or the result from the first texture filter cycle (1)",
    )
    key_en: bpy.props.BoolProperty(
        name="Key",
        description="Enables chroma keying following the Color Combiner stage",
    )
    rgb_dither_sel: bpy.props.EnumProperty(
        name="RGB Dither",
        description="Set RGB dither mode",
        items=(
            ("MAGIC_SQUARE", "Magic Square", "4x4 Magic Square dither matrix"),
            ("BAYER", "Bayer", "4x4 Bayer dither matrix"),
            (
                "RANDOM_NOISE",
                "Random Noise",
                "Random noise. Note the random sample is different per color channel, grayscale images may not remain grayscale after noise dithering.",
            ),
            ("NONE", "None", "Disabled, no dithering applied"),
        ),
    )
    alpha_dither_sel: bpy.props.EnumProperty(
        name="Alpha Dither",
        description="Set Alpha dither mode",
        items=(
            (
                "SAME_AS_RGB",
                "Same As RGB",
                "Same pattern as chosen in RGB. If noise was chosen, use magic square. If RGB dither was disabled, use bayer.",
            ),
            (
                "INVERSE_OF_RGB",
                "Inverse Of RGB",
                "Inverse of the same pattern as chosen in RGB. Same rules as above if RGB was noise or disabled.",
            ),
            ("RANDOM_NOISE", "Random Noise", "Random noise"),
            ("NONE", "None", "Disabled, no dithering applied"),
        ),
    )
    bl_m1a_0: bpy.props.EnumProperty(
        name="P1",
        description="Blender input P (first cycle)",
        items=blender_P_M_inputs_items,
    )
    bl_m1a_1: bpy.props.EnumProperty(
        name="P2",
        description="Blender input P (second cycle)",
        items=blender_P_M_inputs_items,
    )
    bl_m1b_0: bpy.props.EnumProperty(
        name="A1",
        description="Blender input A (first cycle)",
        items=blender_A_inputs_items,
    )
    bl_m1b_1: bpy.props.EnumProperty(
        name="A2",
        description="Blender input A (second cycle)",
        items=blender_A_inputs_items,
    )
    bl_m2a_0: bpy.props.EnumProperty(
        name="M1",
        description="Blender input M (first cycle)",
        items=blender_P_M_inputs_items,
    )
    bl_m2a_1: bpy.props.EnumProperty(
        name="M2",
        description="Blender input M (second cycle)",
        items=blender_P_M_inputs_items,
    )
    bl_m2b_0: bpy.props.EnumProperty(
        name="B1",
        description="Blender input B (first cycle)",
        items=blender_B_inputs_items,
    )
    bl_m2b_1: bpy.props.EnumProperty(
        name="B2",
        description="Blender input B (second cycle)",
        items=blender_B_inputs_items,
    )
    force_blend: bpy.props.BoolProperty(
        name="Force Blend",
        description="Enables blending for all pixels rather than only edge pixels",
    )
    alpha_cvg_select: bpy.props.BoolProperty(
        name="Alpha Coverage Select",
        description="Use coverage (or coverage multiplied by CC alpha) for alpha input to blender rather than alpha output from CC",
    )
    cvg_x_alpha: bpy.props.BoolProperty(
        name="Coverage x Alpha",
        description="Multiply coverage and alpha from CC (used in conjunction with alpha_cvg_sel)",
    )
    z_mode: bpy.props.EnumProperty(
        name="Z Mode",
        description="Determines z-buffer comparator mode",
        items=(
            ("OPAQUE", "Opaque", "Opaque surface mode."),
            ("INTERPENETRATING", "Interpenetrating", "Interpenetrating surface mode."),
            ("TRANSPARENT", "Transparent", "Transparent surface mode."),
            ("DECAL", "Decal", "Decal surface mode."),
        ),
    )
    cvg_dest: bpy.props.EnumProperty(
        name="Coverage Dest",
        description="Determines coverage output mode",
        items=(
            (
                "CLAMP",
                "Clamp",
                "Clamp. Sums new and old coverage, clamps to full if there is an overflow.",
            ),
            (
                "WRAP",
                "Wrap",
                "Wrap. Sums new and old coverage, writes this sum modulo 8.",
            ),
            ("FULL", "Full", "Full. Always write full coverage."),
            (
                "SAVE",
                "Save",
                "Save. Always write old coverage, discard new coverage. Requires image_read_en, otherwise it will behave like Full.",
            ),
        ),
    )
    color_on_cvg: bpy.props.BoolProperty(
        name="Color On Coverage",
        description="If enabled, writes the blender output only if coverage overflowed, otherwise write the 2B input verbatim",
    )
    image_read_en: bpy.props.BoolProperty(
        name="Image Read",
        description="Enable color image reading",
    )
    z_update_en: bpy.props.BoolProperty(
        name="Z Update",
        description="Enable z-buffer writing",
    )
    z_compare_en: bpy.props.BoolProperty(
        name="Z Compare",
        description="Enable z-buffer reading and depth comparison",
    )
    antialias_en: bpy.props.BoolProperty(
        name="Antialias",
        description="Enable anti-aliasing, which may enable blending on edge pixels",
    )
    z_source_sel: bpy.props.BoolProperty(
        name="Z Source",
        description="Selects either per-pixel (0) or primitive (1) depth as depth source to compare against the z-buffer",
    )
    dither_alpha_en: bpy.props.BoolProperty(
        name="Dither Alpha",
        description="Determines alpha compare threshold source. (0 blend color register alpha, 1 random)",
    )
    alpha_compare_en: bpy.props.BoolProperty(
        name="Alpha Compare",
        description="Enables alpha compare, pixels below the alpha threshold (compared against CC alpha output) are not written",
    )


tile_format_items = (
    ("RGBA", "RGBA", "RGBA"),
    ("YUV", "YUV", "YUV"),
    ("CI", "CI", "Color-Indexed (CI)"),
    ("IA", "IA", "Intensity-Alpha (IA)"),
    ("I", "I", "Intensity (I)"),
)

tile_size_items = (
    ("4", "4", "4"),
    ("8", "8", "8"),
    ("16", "16", "16"),
    ("32", "32", "32"),
)


# https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x35_-_Set_Tile
# and https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x32_-_Set_Tile_Size
# TODO improve names/descriptions
class DragExMaterialTileProperties(bpy.types.PropertyGroup):
    image: bpy.props.PointerProperty(
        name="Image",
        description="Tile data to be loaded",
        type=bpy.types.Image,
    )

    format: bpy.props.EnumProperty(
        name="format",
        description="Tile texel format",
        items=tile_format_items,
    )
    size: bpy.props.EnumProperty(
        name="size",
        description="Tile texel size",
        items=tile_size_items,
    )
    line: bpy.props.IntProperty(
        name="line",
        description="Tile line length in TMEM words",
    )
    address: bpy.props.IntProperty(
        name="address",
        description="TMEM address in TMEM words",
    )
    palette: bpy.props.IntProperty(
        name="palette",
        description="Palette index",
    )
    clamp_T: bpy.props.BoolProperty(
        name="clamp_T",
        description="Clamp enable (T-axis)",
    )
    mirror_T: bpy.props.BoolProperty(
        name="mirror_T",
        description="Mirror enable (T-axis)",
    )
    mask_T: bpy.props.IntProperty(
        name="mask_T",
        description="Mask (T-axis)",
    )
    shift_T: bpy.props.IntProperty(
        name="shift_T",
        description="Shift (T-axis)",
    )
    clamp_S: bpy.props.BoolProperty(
        name="clamp_S",
        description="Clamp enable (S-axis)",
    )
    mirror_S: bpy.props.BoolProperty(
        name="mirror_S",
        description="Mirror enable (S-axis)",
    )
    mask_S: bpy.props.IntProperty(
        name="mask_S",
        description="Mask (S-axis)",
    )
    shift_S: bpy.props.IntProperty(
        name="shift_S",
        description="Shift (S-axis)",
    )

    upper_left_S: bpy.props.FloatProperty(
        name="upper_left_S",
        description="Upper-left s coordinate (u10.2 format)",
    )
    upper_left_T: bpy.props.FloatProperty(
        name="upper_left_T",
        description="Upper-left t coordinate (u10.2 format)",
    )
    lower_right_S: bpy.props.FloatProperty(
        name="lower_right_S",
        description="Lower-right s coordinate (u10.2 format)",
    )
    lower_right_T: bpy.props.FloatProperty(
        name="lower_right_T",
        description="Lower-right t coordinate (u10.2 format)",
    )


class DragExMaterialTilesProperties(bpy.types.PropertyGroup):
    tile_0: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_1: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_2: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_3: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_4: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_5: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_6: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_7: bpy.props.PointerProperty(type=DragExMaterialTileProperties)

    @property
    def tiles(self) -> Sequence[DragExMaterialTileProperties]:
        return (
            self.tile_0,
            self.tile_1,
            self.tile_2,
            self.tile_3,
            self.tile_4,
            self.tile_5,
            self.tile_6,
            self.tile_7,
        )


# TODO cleanup names and descriptions of items

rgb_A_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("1", "1", "Fixed 1"),
    (
        "NOISE",
        "NOISE",
        "Per-pixel noise. This is a 9-bit value whose top 3 bits are random, while the bottom 6 are fixed to 0b100000 (0x20).",
    ),
    ("0", "0", "Fixed 0"),
)
rgb_B_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("CENTER", "CENTER", "Chroma key center (see Set Key R and Set Key GB)"),
    ("K4", "K4", "K4 value (see Set Convert)"),
    ("0", "0", "Fixed 0"),
)
rgb_C_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("SCALE", "SCALE", "Chroma key scale (see Set Key R and Set Key GB)"),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", "Combined alpha from first cycle"),
    (
        "TEX0_ALPHA",
        "TEX0_ALPHA",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1_ALPHA",
        "TEX1_ALPHA",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one",
    ),
    ("PRIMITIVE_ALPHA", "PRIMITIVE_ALPHA", "Primitive color register (alpha)"),
    (
        "SHADE_ALPHA",
        "SHADE_ALPHA",
        "Shade alpha interpolated per-pixel from shade coefficients",
    ),
    ("ENVIRONMENT_ALPHA", "ENVIRONMENT_ALPHA", "Environment color register (alpha)"),
    ("LOD_FRACTION", "LOD_FRACTION", "LOD Fraction computed as part of Texture LOD"),
    (
        "PRIM_LOD_FRAC",
        "PRIM_LOD_FRAC",
        "Primitive LOD Fraction (see Set Primitive Color)",
    ),
    ("K5", "K5", "K5 value (see Set Convert)"),
    ("0", "0", "Fixed 0"),
)
rgb_D_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)

alpha_A_inputs_items = (
    ("COMBINED", "COMBINED", "Combined alpha from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)
alpha_B_inputs_items = (
    ("COMBINED", "COMBINED", "Combined alpha from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)
alpha_C_inputs_items = (
    ("LOD_FRACTION", "LOD_FRACTION", "LOD Fraction computed as part of Texture LOD"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    (
        "PRIM_LOD_FRAC",
        "PRIM_LOD_FRAC",
        "Primitive LOD Fraction (see Set Primitive Color)",
    ),
    ("0", "0", "Fixed 0"),
)
alpha_D_inputs_items = (
    ("COMBINED", "COMBINED", "Combined alpha from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)


# https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x3C_-_Set_Combine_Mode
class DragExMaterialCombinerProperties(bpy.types.PropertyGroup):
    rgb_A_0: bpy.props.EnumProperty(
        name="RGB A 1",
        description="RGB A Input (First Cycle)",
        items=rgb_A_inputs_items,
    )
    rgb_B_0: bpy.props.EnumProperty(
        name="RGB B 1",
        description="RGB B Input (First Cycle)",
        items=rgb_B_inputs_items,
    )
    rgb_C_0: bpy.props.EnumProperty(
        name="RGB C 1",
        description="RGB C Input (First Cycle)",
        items=rgb_C_inputs_items,
    )
    rgb_D_0: bpy.props.EnumProperty(
        name="RGB D 1",
        description="RGB D Input (First Cycle)",
        items=rgb_D_inputs_items,
    )

    alpha_A_0: bpy.props.EnumProperty(
        name="Alpha A 1",
        description="RGB A Input (First Cycle)",
        items=alpha_A_inputs_items,
    )
    alpha_B_0: bpy.props.EnumProperty(
        name="Alpha B 1",
        description="RGB B Input (First Cycle)",
        items=alpha_B_inputs_items,
    )
    alpha_C_0: bpy.props.EnumProperty(
        name="Alpha C 1",
        description="RGB C Input (First Cycle)",
        items=alpha_C_inputs_items,
    )
    alpha_D_0: bpy.props.EnumProperty(
        name="Alpha D 1",
        description="RGB D Input (First Cycle)",
        items=alpha_D_inputs_items,
    )

    rgb_A_1: bpy.props.EnumProperty(
        name="RGB A 2",
        description="RGB A Input (Second Cycle)",
        items=rgb_A_inputs_items,
    )
    rgb_B_1: bpy.props.EnumProperty(
        name="RGB B 2",
        description="RGB B Input (Second Cycle)",
        items=rgb_B_inputs_items,
    )
    rgb_C_1: bpy.props.EnumProperty(
        name="RGB C 2",
        description="RGB C Input (Second Cycle)",
        items=rgb_C_inputs_items,
    )
    rgb_D_1: bpy.props.EnumProperty(
        name="RGB D 2",
        description="RGB D Input (Second Cycle)",
        items=rgb_D_inputs_items,
    )

    alpha_A_1: bpy.props.EnumProperty(
        name="Alpha A 2",
        description="RGB A Input (Second Cycle)",
        items=alpha_A_inputs_items,
    )
    alpha_B_1: bpy.props.EnumProperty(
        name="Alpha B 2",
        description="RGB B Input (Second Cycle)",
        items=alpha_B_inputs_items,
    )
    alpha_C_1: bpy.props.EnumProperty(
        name="Alpha C 2",
        description="RGB C Input (Second Cycle)",
        items=alpha_C_inputs_items,
    )
    alpha_D_1: bpy.props.EnumProperty(
        name="Alpha D 2",
        description="RGB D Input (Second Cycle)",
        items=alpha_D_inputs_items,
    )


class DragExMaterialValsProperties(bpy.types.PropertyGroup):
    # TODO Key GB, Key R, Convert
    primitive_depth_z: bpy.props.IntProperty(
        name="Primitive Depth z",
        description="Primitive depth value",
    )
    primitive_depth_dz: bpy.props.IntProperty(
        name="Primitive Depth dz",
        description="Primitive dz value",
    )
    fog_color: bpy.props.FloatVectorProperty(
        name="Fog Color",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
    )
    blend_color: bpy.props.FloatVectorProperty(
        name="Blend Color",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
    )
    min_level: bpy.props.IntProperty(
        name="Min LOD Level",
        description="Minimum LOD level",
    )
    prim_lod_frac: bpy.props.IntProperty(
        name="Prim LOD Frac",
        description="Primitive LOD Fraction Color Combiner input",
    )
    primitive_color: bpy.props.FloatVectorProperty(
        name="Primitive Color",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
    )
    environment_color: bpy.props.FloatVectorProperty(
        name="Environment Color",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
    )


class DragExMaterialProperties(bpy.types.PropertyGroup):
    uv_basis_s: bpy.props.IntProperty(name="UV Basis S", min=1, default=1)
    uv_basis_t: bpy.props.IntProperty(name="UV Basis T", min=1, default=1)

    other_modes_: bpy.props.PointerProperty(type=DragExMaterialOtherModesProperties)
    tiles_: bpy.props.PointerProperty(type=DragExMaterialTilesProperties)
    combiner_: bpy.props.PointerProperty(type=DragExMaterialCombinerProperties)
    vals_: bpy.props.PointerProperty(type=DragExMaterialValsProperties)
    geometry_mode_: bpy.props.PointerProperty(type=DragExMaterialGeometryModeProperties)

    @property
    def other_modes(self) -> DragExMaterialOtherModesProperties:
        return self.other_modes_

    @property
    def tiles(self) -> DragExMaterialTilesProperties:
        return self.tiles_

    @property
    def combiner(self) -> DragExMaterialCombinerProperties:
        return self.combiner_

    @property
    def vals(self) -> DragExMaterialValsProperties:
        return self.vals_

    @property
    def geometry_mode(self) -> DragExMaterialGeometryModeProperties:
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
    DragExMaterialGeometryModeProperties,
    DragExMaterialOtherModesProperties,
    DragExMaterialTileProperties,
    DragExMaterialTilesProperties,
    DragExMaterialCombinerProperties,
    DragExMaterialValsProperties,
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

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Material.dragex = bpy.props.PointerProperty(type=DragExMaterialProperties)

    from . import f64render_dragex

    f64render_dragex.register()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    from . import f64render_dragex

    f64render_dragex.unregister()

    print("Bye from", __package__)
