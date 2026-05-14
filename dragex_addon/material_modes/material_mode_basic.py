import bpy

from .. import util

from . import material_modes_defs
from .material_modes_defs import TMEM_SIZE, intlog2


class BasicMaterialMode(material_modes_defs.MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        BasicMaterialMode.apply_mode_props(material)

    @staticmethod
    def draw(layout, material):
        material_dragex = util.DRAGEX(material)
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
    def apply_mode_props(material: bpy.types.Material):
        material_dragex = util.DRAGEX(material)
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
            use_shade = True
        elif basic_props.shading == "VERTEX_COLORS":
            rsp_props.lighting = False
            rsp_props.vertex_colors = True
            use_shade = True
        elif basic_props.shading == "NONE":
            rsp_props.lighting = False
            rsp_props.vertex_colors = False
            use_shade = False
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
            cb.rgb_D_0 = "SHADE" if use_shade else "1"
        else:
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
                    cb.alpha_D_0 = "SHADE" if use_shade else "1"
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
            ("NONE", "None", "Vertices do not use lights nor vertex colors"),
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
