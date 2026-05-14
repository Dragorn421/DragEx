import bpy

from .. import util

from . import material_modes_defs
from .material_modes_defs import TMEM_SIZE, intlog2, encode_shift


class MultitextureMaterialMode(material_modes_defs.MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        MultitextureMaterialMode.apply_mode_props(material)

    @staticmethod
    def draw(layout, material):
        material_dragex = util.DRAGEX(material)
        mode_basic = material_dragex.modes.multitexture
        box = layout.box()
        box.template_ID(mode_basic, "texture1", new="image.new", open="image.open")
        texture1 = mode_basic.texture1
        if texture1 is not None and tuple(texture1.size) != (0, 0):
            texture1_w, texture1_h = texture1.size
            if texture1_w * texture1_h * 2 > TMEM_SIZE:
                box.label(text="Texture too big: max 32x64 or 64x32", icon="ERROR")
            if texture1_w * 2 % 8 != 0:
                box.label(text="Texture width must be a multiple of 4", icon="ERROR")
            if intlog2(texture1_w) is None:
                box.label(
                    text="Texture width must be a power of 2 for wrapping", icon="INFO"
                )
            if intlog2(texture1_h) is None:
                box.label(
                    text="Texture height must be a power of 2 for wrapping", icon="INFO"
                )
        box.prop(mode_basic, "shift_u1")
        box.prop(mode_basic, "shift_v1")
        box = layout.box()
        box.template_ID(mode_basic, "texture2", new="image.new", open="image.open")
        texture2 = mode_basic.texture2
        if texture2 is not None and tuple(texture2.size) != (0, 0):
            texture2_w, texture2_h = texture2.size
            if texture2_w * texture2_h * 2 > TMEM_SIZE:
                box.label(text="Texture too big: max 32x64 or 64x32", icon="ERROR")
            if texture2_w * 2 % 8 != 0:
                box.label(text="Texture width must be a multiple of 4", icon="ERROR")
            if intlog2(texture2_w) is None:
                box.label(
                    text="Texture width must be a power of 2 for wrapping", icon="INFO"
                )
            if intlog2(texture2_h) is None:
                box.label(
                    text="Texture height must be a power of 2 for wrapping", icon="INFO"
                )
        box.prop(mode_basic, "shift_u2")
        box.prop(mode_basic, "shift_v2")
        if texture1 is not None and texture2 is not None and texture1 != texture2:
            texture1_w, texture1_h = texture1.size
            texture2_w, texture2_h = texture2.size
            if texture1_w * texture1_h * 2 + texture2_w * texture2_h * 2 > TMEM_SIZE:
                box.label(
                    text="Textures too big: max 32x64 total pixels (e.g. 32x32 each)",
                    icon="ERROR",
                )
        layout.prop(mode_basic, "factor")
        layout.prop(mode_basic, "shading")
        layout.prop(mode_basic, "alpha_blend")
        layout.prop(mode_basic, "fog")

    @staticmethod
    def apply_mode_props(material: bpy.types.Material):
        material_dragex = util.DRAGEX(material)
        multitexture_props = material_dragex.modes.multitexture
        texture1: bpy.types.Image | None = multitexture_props.texture1
        texture2: bpy.types.Image | None = multitexture_props.texture2

        # TODO check if both textures together fit in TMEM

        tile0 = material_dragex.rdp.tiles.tiles[0]
        tile0.image = texture1
        tile0.format = "RGBA"
        tile0.size = "16"
        tile0.address = 0
        tile0.palette = 0
        if texture1 is not None and tuple(texture1.size) != (0, 0):
            # TODO check if s=width, t=height (test with non-square texture)
            texture1_w, texture1_h = texture1.size
            if texture1_w * texture1_h * 2 > TMEM_SIZE:
                tile0.image = None
            material_dragex.uv_basis_s = texture1_w
            material_dragex.uv_basis_t = texture1_h
            if texture1_w * 2 % 8 != 0:
                tile0.image = None
            tile0.line = texture1_w * 2 // 8
            mask_S = intlog2(texture1_w)
            mask_T = intlog2(texture1_h)
            if mask_S is None:
                tile0.clamp_S = True
                tile0.mask_S = 0
            else:
                tile0.clamp_S = False
                tile0.mask_S = mask_S
            tile0.mirror_S = False
            tile0.shift_S = encode_shift(multitexture_props.shift_u1)
            if mask_T is None:
                tile0.clamp_T = True
                tile0.mask_T = 0
            else:
                tile0.clamp_T = False
                tile0.mask_T = mask_T
            tile0.mirror_T = False
            tile0.shift_T = encode_shift(multitexture_props.shift_v1)
            tile0.upper_left_S = 0
            tile0.upper_left_T = 0
            tile0.lower_right_S = texture1_w - 1
            tile0.lower_right_T = texture1_h - 1

        tile1 = material_dragex.rdp.tiles.tiles[1]
        tile1.image = texture2
        tile1.format = "RGBA"
        tile1.size = "16"
        if tile0.image is None or texture1 == texture2:
            tile1.address = 0
        else:
            assert texture1 is not None
            texture1_w, texture1_h = texture1.size
            assert texture1_w * 2 % 8 == 0
            tile1.address = texture1_w * texture1_h * 2 // 8
        tile1.palette = 0
        if texture2 is not None and tuple(texture2.size) != (0, 0):
            # TODO check if s=width, t=height (test with non-square texture)
            texture2_w, texture2_h = texture2.size
            if texture2_w * texture2_h * 2 > TMEM_SIZE:
                tile1.image = None
            if tile0.image is None:
                material_dragex.uv_basis_s = texture2_w
                material_dragex.uv_basis_t = texture2_h
            if texture2_w * 2 % 8 != 0:
                tile1.image = None
            tile1.line = texture2_w * 2 // 8
            mask_S = intlog2(texture2_w)
            mask_T = intlog2(texture2_h)
            if mask_S is None:
                tile1.clamp_S = True
                tile1.mask_S = 0
            else:
                tile1.clamp_S = False
                tile1.mask_S = mask_S
            tile1.mirror_S = False
            tile1.shift_S = encode_shift(multitexture_props.shift_u2)
            if mask_T is None:
                tile1.clamp_T = True
                tile1.mask_T = 0
            else:
                tile1.clamp_T = False
                tile1.mask_T = mask_T
            tile1.mirror_T = False
            tile1.shift_T = encode_shift(multitexture_props.shift_v2)
            tile1.upper_left_S = 0
            tile1.upper_left_T = 0
            tile1.lower_right_S = texture2_w - 1
            tile1.lower_right_T = texture2_h - 1

        rsp_props = material_dragex.rsp

        rsp_props.zbuffer = True
        if multitexture_props.shading == "LIGHTING":
            rsp_props.lighting = True
            rsp_props.vertex_colors = False
            use_shade = True
        elif multitexture_props.shading == "VERTEX_COLORS":
            rsp_props.lighting = False
            rsp_props.vertex_colors = True
            use_shade = True
        elif multitexture_props.shading == "NONE":
            rsp_props.lighting = False
            rsp_props.vertex_colors = False
            use_shade = False
        else:
            assert False, multitexture_props.shading
        rsp_props.cull_front = False
        rsp_props.cull_back = True
        rsp_props.fog = multitexture_props.fog
        rsp_props.uv_gen_spherical = False
        rsp_props.uv_gen_linear = False
        rsp_props.shade_smooth = True

        om = material_dragex.rdp.other_modes
        om.atomic_prim = False
        om.cycle_type = "2CYCLE"
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
            om.bl_m1a_0 = "FOG_COLOR"
            om.bl_m1b_0 = "SHADE_ALPHA"
            om.bl_m2a_0 = "INPUT"
            om.bl_m2b_0 = "1_MINUS_A"
            om.bl_m1a_1 = "INPUT"
            om.bl_m1b_1 = "INPUT_ALPHA"
            om.bl_m2a_1 = "MEMORY"
            om.bl_m2b_1 = (
                "1_MINUS_A"
                if multitexture_props.alpha_blend == "TRANSPARENT"
                else "MEMORY_COVERAGE"
            )
        else:
            om.bl_m1a_0 = "INPUT"
            om.bl_m1b_0 = "INPUT_ALPHA"
            om.bl_m2a_0 = "MEMORY"
            om.bl_m2b_0 = (
                "1_MINUS_A"
                if multitexture_props.alpha_blend == "TRANSPARENT"
                else "MEMORY_COVERAGE"
            )
            om.bl_m1a_1 = "INPUT"
            om.bl_m1b_1 = "0"
            om.bl_m2a_1 = "INPUT"
            om.bl_m2b_1 = "1"
        if multitexture_props.alpha_blend in {"OPAQUE", "CUTOUT"}:
            om.force_blend = False
            om.alpha_cvg_select = True
            om.cvg_x_alpha = multitexture_props.alpha_blend == "CUTOUT"
            om.z_mode = "OPAQUE"
            om.cvg_dest = "CLAMP"
            om.color_on_cvg = False
            om.z_update_en = True
        elif multitexture_props.alpha_blend == "TRANSPARENT":
            om.force_blend = True
            om.alpha_cvg_select = False
            om.cvg_x_alpha = False
            om.z_mode = "TRANSPARENT"
            om.cvg_dest = "WRAP"
            om.color_on_cvg = True
            om.z_update_en = False
        else:
            assert False, multitexture_props.alpha_blend
        om.image_read_en = True
        om.z_compare_en = True
        om.antialias_en = True
        om.z_source_sel = False
        om.dither_alpha_en = False
        om.alpha_compare_en = False

        cb = material_dragex.rdp.combiner
        if tile0.image is None and tile1.image is None:
            cb.rgb_A_0 = "0"
            cb.rgb_B_0 = "0"
            cb.rgb_C_0 = "0"
            cb.rgb_D_0 = "SHADE" if use_shade else "1"
            cb.rgb_A_1 = "0"
            cb.rgb_B_1 = "0"
            cb.rgb_C_1 = "0"
            cb.rgb_D_1 = "COMBINED"
            if multitexture_props.alpha_blend in {"CUTOUT", "TRANSPARENT"}:
                if multitexture_props.fog:
                    cb.alpha_A_0 = "0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "0"
                    cb.alpha_D_0 = "1"
                else:
                    cb.alpha_A_0 = "0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "0"
                    cb.alpha_D_0 = "SHADE" if use_shade else "1"
            else:
                cb.alpha_A_0 = "0"
                cb.alpha_B_0 = "0"
                cb.alpha_C_0 = "0"
                cb.alpha_D_0 = "1"
            cb.alpha_A_1 = "0"
            cb.alpha_B_1 = "0"
            cb.alpha_C_1 = "0"
            cb.alpha_D_1 = "COMBINED"
        elif tile1.image is None:
            assert tile0.image is not None
            if use_shade:
                cb.rgb_A_0 = "TEX0"
                cb.rgb_B_0 = "0"
                cb.rgb_C_0 = "SHADE"
                cb.rgb_D_0 = "0"
            else:
                cb.rgb_A_0 = "0"
                cb.rgb_B_0 = "0"
                cb.rgb_C_0 = "0"
                cb.rgb_D_0 = "TEX0"
            cb.rgb_A_1 = "0"
            cb.rgb_B_1 = "0"
            cb.rgb_C_1 = "0"
            cb.rgb_D_1 = "COMBINED"
            if multitexture_props.alpha_blend in {"CUTOUT", "TRANSPARENT"}:
                if multitexture_props.fog:
                    cb.alpha_A_0 = "0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "0"
                    cb.alpha_D_0 = "TEX0"
                else:
                    if use_shade:
                        cb.alpha_A_0 = "TEX0"
                        cb.alpha_B_0 = "0"
                        cb.alpha_C_0 = "SHADE"
                        cb.alpha_D_0 = "0"
                    else:
                        cb.alpha_A_0 = "0"
                        cb.alpha_B_0 = "0"
                        cb.alpha_C_0 = "0"
                        cb.alpha_D_0 = "TEX0"
            else:
                cb.alpha_A_0 = "0"
                cb.alpha_B_0 = "0"
                cb.alpha_C_0 = "0"
                cb.alpha_D_0 = "1"
            cb.alpha_A_1 = "0"
            cb.alpha_B_1 = "0"
            cb.alpha_C_1 = "0"
            cb.alpha_D_1 = "COMBINED"
        elif tile0.image is None:
            assert tile1.image is not None
            if use_shade:
                cb.rgb_A_0 = "TEX1"
                cb.rgb_B_0 = "0"
                cb.rgb_C_0 = "SHADE"
                cb.rgb_D_0 = "0"
            else:
                cb.rgb_A_0 = "0"
                cb.rgb_B_0 = "0"
                cb.rgb_C_0 = "0"
                cb.rgb_D_0 = "TEX1"
            cb.rgb_A_1 = "0"
            cb.rgb_B_1 = "0"
            cb.rgb_C_1 = "0"
            cb.rgb_D_1 = "COMBINED"
            if multitexture_props.alpha_blend in {"CUTOUT", "TRANSPARENT"}:
                if multitexture_props.fog:
                    cb.alpha_A_0 = "0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "0"
                    cb.alpha_D_0 = "TEX1"
                else:
                    if use_shade:
                        cb.alpha_A_0 = "TEX1"
                        cb.alpha_B_0 = "0"
                        cb.alpha_C_0 = "SHADE"
                        cb.alpha_D_0 = "0"
                    else:
                        cb.alpha_A_0 = "0"
                        cb.alpha_B_0 = "0"
                        cb.alpha_C_0 = "0"
                        cb.alpha_D_0 = "TEX1"
            else:
                cb.alpha_A_0 = "0"
                cb.alpha_B_0 = "0"
                cb.alpha_C_0 = "0"
                cb.alpha_D_0 = "1"
            cb.alpha_A_1 = "0"
            cb.alpha_B_1 = "0"
            cb.alpha_C_1 = "0"
            cb.alpha_D_1 = "COMBINED"
        else:
            assert tile0.image is not None and tile1.image is not None
            material_dragex.rdp.vals.environment_color = (
                *material_dragex.rdp.vals.environment_color[:3],
                multitexture_props.factor / 100,
            )
            cb.rgb_A_0 = "TEX1"
            cb.rgb_B_0 = "TEX0"
            cb.rgb_C_0 = "ENVIRONMENT_ALPHA"
            cb.rgb_D_0 = "TEX0"
            if use_shade:
                cb.rgb_A_1 = "COMBINED"
                cb.rgb_B_1 = "0"
                cb.rgb_C_1 = "SHADE"
                cb.rgb_D_1 = "0"
            else:
                cb.rgb_A_1 = "0"
                cb.rgb_B_1 = "0"
                cb.rgb_C_1 = "0"
                cb.rgb_D_1 = "COMBINED"
            if multitexture_props.alpha_blend in {"CUTOUT", "TRANSPARENT"}:
                cb.alpha_A_0 = "TEX1"
                cb.alpha_B_0 = "TEX0"
                cb.alpha_C_0 = "ENVIRONMENT"
                cb.alpha_D_0 = "TEX0"
                if multitexture_props.fog:
                    cb.alpha_A_1 = "0"
                    cb.alpha_B_1 = "0"
                    cb.alpha_C_1 = "0"
                    cb.alpha_D_1 = "COMBINED"
                else:
                    if use_shade:
                        cb.alpha_A_1 = "COMBINED"
                        cb.alpha_B_1 = "0"
                        cb.alpha_C_1 = "SHADE"
                        cb.alpha_D_1 = "0"
                    else:
                        cb.alpha_A_1 = "0"
                        cb.alpha_B_1 = "0"
                        cb.alpha_C_1 = "0"
                        cb.alpha_D_1 = "COMBINED"
            else:
                cb.alpha_A_0 = "0"
                cb.alpha_B_0 = "0"
                cb.alpha_C_0 = "0"
                cb.alpha_D_0 = "1"
                cb.alpha_A_1 = "0"
                cb.alpha_B_1 = "0"
                cb.alpha_C_1 = "0"
                cb.alpha_D_1 = "COMBINED"

    @staticmethod
    def on_mode_prop_update(_self, context: bpy.types.Context):
        material = context.material
        assert material is not None
        MultitextureMaterialMode.apply_mode_props(material)


class DragExMaterialModesMultitextureProperties(bpy.types.PropertyGroup):
    texture1: bpy.props.PointerProperty(
        name="Texture 1",
        type=bpy.types.Image,
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
    shift_u1: bpy.props.IntProperty(
        name="Shift U 1",
        description="U shift of the UV coordinates for texture 1",
        default=0,
        min=-5,
        max=10,
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
    shift_v1: bpy.props.IntProperty(
        name="Shift V 1",
        description="V shift of the UV coordinates for texture 1",
        default=0,
        min=-5,
        max=10,
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
    texture2: bpy.props.PointerProperty(
        name="Texture 2",
        type=bpy.types.Image,
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
    shift_u2: bpy.props.IntProperty(
        name="Shift U 2",
        description="U shift of the UV coordinates for texture 2",
        default=0,
        min=-5,
        max=10,
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
    shift_v2: bpy.props.IntProperty(
        name="Shift V 2",
        description="V shift of the UV coordinates for texture 2",
        default=0,
        min=-5,
        max=10,
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
    factor: bpy.props.FloatProperty(
        name="Factor",
        description=(
            "The factor for blending the two textures together.\n"
            "0% is fully texture 1 and 100% is fully texture 2"
        ),
        default=50,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        update=MultitextureMaterialMode.on_mode_prop_update,
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
            ("NONE", "None", "Vertices do not use lights nor vertex colors"),
        ),
        default="LIGHTING",
        update=MultitextureMaterialMode.on_mode_prop_update,
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
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
    fog: bpy.props.BoolProperty(
        name="Fog",
        description=(
            "Whether this material is affected by fog"
            " (blend with the fog color as the geometry is further from the camera)"
        ),
        default=True,
        update=MultitextureMaterialMode.on_mode_prop_update,
    )
