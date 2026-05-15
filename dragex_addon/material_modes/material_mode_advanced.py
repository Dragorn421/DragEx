import bpy

from .. import util

from . import material_modes_defs
from .material_modes_defs import TMEM_SIZE, intlog2, encode_shift


def get_used_sources(self: "DragExMaterialModesAdvancedProperties") -> set[str]:
    if self.template_1_color == "SINGLE":
        color_set_1 = {self.template_1_color_single_src}

    elif self.template_1_color == "LERP":
        color_set_1 = {
            self.template_1_color_lerp_src_1,
            self.template_1_color_lerp_src_2,
            self.template_1_color_lerp_factor,
        }

    elif self.template_1_color == "ADD":
        color_set_1 = {
            self.template_1_color_add_src1,
            self.template_1_color_add_src2,
            self.template_1_color_add_factor,
        }

    elif self.template_1_color == "MULT":
        color_set_1 = {
            self.template_1_color_mult_src_1,
            self.template_1_color_mult_src_2,
        }
    else:
        assert False

    if self.template_1_alpha == "SINGLE":
        alpha_set_1 = {self.template_1_alpha_single_src}

    elif self.template_1_alpha == "LERP":
        alpha_set_1 = {
            self.template_1_alpha_lerp_src_1,
            self.template_1_alpha_lerp_src_2,
            self.template_1_alpha_lerp_factor,
        }

    elif self.template_1_alpha == "ADD":
        alpha_set_1 = {
            self.template_1_alpha_add_src1,
            self.template_1_alpha_add_src2,
            self.template_1_alpha_add_factor,
        }

    elif self.template_1_alpha == "MULT":
        alpha_set_1 = {
            self.template_1_alpha_mult_src_1,
            self.template_1_alpha_mult_src_2,
        }
    else:
        assert False

    if self.template_color_two_cycle:
        if self.template_2_color == "SINGLE":
            color_set_2 = {self.template_2_color_single_src}

        elif self.template_2_color == "LERP":
            color_set_2 = {
                self.template_2_color_lerp_src_1,
                self.template_2_color_lerp_src_2,
                self.template_2_color_lerp_factor,
            }

        elif self.template_2_color == "ADD":
            color_set_2 = {
                self.template_2_color_add_src1,
                self.template_2_color_add_src2,
                self.template_2_color_add_factor,
            }

        elif self.template_2_color == "MULT":
            color_set_2 = {
                self.template_2_color_mult_src_1,
                self.template_2_color_mult_src_2,
            }
        else:
            assert False
    else:
        color_set_2 = set()

    if self.template_alpha_two_cycle:
        if self.template_2_alpha == "SINGLE":
            alpha_set_2 = {self.template_2_alpha_single_src}

        elif self.template_2_alpha == "LERP":
            alpha_set_2 = {
                self.template_2_alpha_lerp_src_1,
                self.template_2_alpha_lerp_src_2,
                self.template_2_alpha_lerp_factor,
            }

        elif self.template_2_alpha == "ADD":
            alpha_set_2 = {
                self.template_2_alpha_add_src1,
                self.template_2_alpha_add_src2,
                self.template_2_alpha_add_factor,
            }

        elif self.template_2_alpha == "MULT":
            alpha_set_2 = {
                self.template_2_alpha_mult_src_1,
                self.template_2_alpha_mult_src_2,
            }
        else:
            assert False
    else:
        alpha_set_2 = set()

    return color_set_1 | color_set_2 | alpha_set_1 | alpha_set_2


def draw_cycle(
    self: "DragExMaterialModesAdvancedProperties", layout: bpy.types.UILayout, type: str
):
    col = layout.column(align=True)

    row = col.row(align=True)
    row.prop(self, f"template_{type}", expand=True)

    template = getattr(self, f"template_{type}")

    if template == "SINGLE":
        row = col.row(align=True)
        row.label(text=" ")
        row.prop(self, f"template_{type}_single_src", text="")
    elif template == "LERP":
        row = col.row(align=True)
        row.prop(self, f"template_{type}_lerp_src_1", text="")
        row.prop(self, f"template_{type}_lerp_src_2", text="")
        col.prop(self, f"template_{type}_lerp_factor", text="")
    elif template == "ADD":
        row = col.row(align=True)
        row.prop(self, f"template_{type}_add_src1", text="")
        row.label(text="")
        row = col.row(align=True)
        row.prop(self, f"template_{type}_add_src2", text="")
        row.prop(self, f"template_{type}_add_factor", text="")
    elif template == "MULT":
        row = col.row(align=True)
        row.prop(self, f"template_{type}_mult_src_1", text="")
        row.prop(self, f"template_{type}_mult_src_2", text="")
    else:
        assert False


def draw_combiner_panels(
    self: "DragExMaterialModesAdvancedProperties", layout: bpy.types.UILayout
):
    for type in ("color", "alpha"):
        header, body = layout.panel(f"{type}_combiner")
        header.label(text=type.capitalize() + " Combiner")

        if body is not None:
            draw_cycle(self, body, f"1_{type}")

            if getattr(self, f"template_{type}_two_cycle"):
                body.separator()
                draw_cycle(self, body, f"2_{type}")
                body.prop(
                    self,
                    f"template_{type}_two_cycle",
                    text="",
                    icon="REMOVE",
                    expand=True,
                    emboss=False,
                )
            else:
                body.prop(
                    self,
                    f"template_{type}_two_cycle",
                    text="",
                    icon="ADD",
                    expand=True,
                    emboss=False,
                )


class AdvancedMaterialMode(material_modes_defs.MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        AdvancedMaterialMode.apply_mode_props(material)

    @staticmethod
    def draw(layout, material):
        material_dragex = util.DRAGEX(material)
        mode_advanced = material_dragex.modes.advanced

        draw_combiner_panels(mode_advanced, layout)

        header, body = layout.panel("combiner_template_sources")
        header.label(text="Sources")
        if body is not None:
            used_sources = get_used_sources(mode_advanced)

            for id in (0, 1):
                if {f"TEX{id}", f"TEX{id}_ALPHA"} & used_sources:
                    lheader, lbody = body.panel(
                        f"combiner_template_source_texture_{id}"
                    )

                    col = lheader.column(align=True)
                    col.use_property_split = True
                    col.use_property_decorate = False

                    col.template_ID(
                        mode_advanced,
                        f"texel_{id}_image",
                        text=f"Texture {id}",
                        open="image.open",
                        live_icon=True,
                    )

                    # TODO check and error/warn about tmem usage, texture line alignment, dimensions for wrapping

                    if lbody is not None:
                        col = lbody.column(align=True)
                        col.use_property_split = True
                        col.use_property_decorate = False

                        row = col.row()
                        row.prop(
                            mode_advanced, f"texel_{id}_segment_address", text="Segment"
                        )
                        row.enabled = False  # TODO implement texel_[01]_segment_address
                        col.prop(mode_advanced, f"texel_{id}_format", text="Format")

                        row = col.row(align=True)
                        row.prop(
                            mode_advanced,
                            f"texel_{id}_repeat_mode_x",
                            text="Repeat Mode",
                        )
                        row.prop(mode_advanced, f"texel_{id}_repeat_mode_y", text="")
                        row = col.row(align=True)
                        row.prop(
                            mode_advanced,
                            f"texel_{id}_shift_x",
                            text="Shift",
                            slider=True,
                        )
                        row.prop(
                            mode_advanced, f"texel_{id}_shift_y", text="", slider=True
                        )
                        row = col.row(align=True)
                        row.prop(mode_advanced, f"texel_{id}_offset_x", text="Offset")
                        row.prop(mode_advanced, f"texel_{id}_offset_y", text="")

                    body.separator(type="LINE")

            if {"ENVIRONMENT", "ENVIRONMENT_ALPHA"} & used_sources:
                col = body.column(align=True)
                col.use_property_split = True
                col.use_property_decorate = False
                col.prop(mode_advanced, "src_env_color", text="Environment Color")
                col.prop(mode_advanced, "src_env_alpha", text="Alpha", slider=True)
                row = col.row()
                row.prop(mode_advanced, "src_env_write", text="Write", toggle=True)
                row.enabled = False  # TODO implement src_env_write
                body.separator(type="LINE")

            if {"PRIMITIVE", "PRIMITIVE_ALPHA", "PRIM_LOD_FRAC"} & used_sources:
                col = body.column(align=True)
                col.use_property_split = True
                col.use_property_decorate = False
                col.prop(mode_advanced, "src_prim_color", text="Primitive Color")
                col.prop(mode_advanced, "src_prim_alpha", text="Alpha", slider=True)
                col.prop(
                    mode_advanced,
                    "src_prim_lod_frac",
                    text="Prim Lod Frac",
                    slider=True,
                )
                row = col.row()
                row.prop(mode_advanced, "src_prim_write", text="Write", toggle=True)
                row.enabled = False  # TODO implement src_prim_write
                body.separator(type="LINE")

            if {"SHADE", "SHADE_ALPHA"} & used_sources:
                col = body.column(align=True)
                col.use_property_split = True
                col.use_property_decorate = False
                col.prop(mode_advanced, "shading")
                body.separator(type="LINE")

            if mode_advanced.alpha_compare:
                col = body.column(align=True)
                col.use_property_split = True
                col.use_property_decorate = False
                col.prop(
                    mode_advanced,
                    "src_threshold_alpha",
                    text="Alpha Threshold",
                    slider=True,
                )
                row = col.row()
                row.prop(
                    mode_advanced, "src_threshold_write", text="Write", toggle=True
                )
                row.enabled = False  # TODO implement src_threshold_write
                body.separator(type="LINE")

        header, body = layout.panel("display_properties")
        header.label(text="Properties")
        if body is not None:
            col = body.column(align=True)

            col.prop(mode_advanced, "alpha_blend_type", text="")
            row = col.row(align=True)
            row.prop(
                mode_advanced, "backface_culling", text="Backface Culling", toggle=True
            )
            row.prop(mode_advanced, "fog", text="Fog", toggle=True)
            row = col.row(align=True)
            row.prop(mode_advanced, "decal", text="Decal", toggle=True)
            row2 = row.row()
            row2.prop(
                mode_advanced, "enable_pointlights", text="Pointlight", toggle=True
            )
            row2.enabled = False  # TODO implement enable_pointlights ?
            row = col.row(align=True)
            row.prop(mode_advanced, "z_read", text="Z Read", toggle=True)

            if mode_advanced.alpha_blend_type == "TRANSPARENT":
                yes = row.row(align=True)
                yes.enabled = False
                yes.prop(
                    mode_advanced,
                    "z_write",
                    text="Z Write",
                    toggle=True,
                    # just to always display "z_write" as disabled
                    # TODO instead of this, set z_write to false somewhere in a callback
                    invert_checkbox=mode_advanced.z_write,
                )
            else:
                row.prop(mode_advanced, "z_write", text="Z Write", toggle=True)

            row = col.row(align=True)
            # TODO implement alpha_noise, and then merge alpha_noise and alpha_compare into a three-state enum
            row2 = row.row()
            row2.prop(mode_advanced, "alpha_noise", text="Alpha Noise", toggle=True)
            row2.enabled = False  # TODO implement alpha_noise
            row.prop(mode_advanced, "alpha_compare", text="Alpha Compare", toggle=True)

            row = col.row()
            row.use_property_split = True
            row.use_property_decorate = False
            row.prop(mode_advanced, "dlist_call")
            row.enabled = False  # TODO implement dlist_call

    @staticmethod
    def apply_mode_props(material: bpy.types.Material):
        material_dragex = util.DRAGEX(material)
        advanced_props = material_dragex.modes.advanced

        used_sources = get_used_sources(advanced_props)

        texture1: bpy.types.Image | None = advanced_props.texel_0_image
        if not ({"TEX0", "TEX0_ALPHA"} & used_sources):
            texture1 = None
        texture2: bpy.types.Image | None = advanced_props.texel_1_image
        if not ({"TEX1", "TEX1_ALPHA"} & used_sources):
            texture2 = None

        # TODO check if both textures together fit in TMEM

        tile0 = material_dragex.rdp.tiles.tiles[0]
        tile0.image = texture1
        tile0.format, tile0.size = split_texformat(advanced_props.texel_0_format)
        tile0.address = 0
        if tile0.format == "CI":
            raise NotImplementedError("CI formats")  # TODO CI formats
        tile0.palette = 0
        if texture1 is not None and tuple(texture1.size) != (0, 0):
            # TODO check if s=width, t=height (test with non-square texture)
            texture1_w, texture1_h = texture1.size
            texture1_bpp = int(tile0.size)
            if texture1_w * texture1_h * texture1_bpp > TMEM_SIZE * 8:
                tile0.image = None
            material_dragex.uv_basis_s = texture1_w
            material_dragex.uv_basis_t = texture1_h
            if texture1_w * texture1_bpp % 64 != 0:
                tile0.image = None
            tile0.line = texture1_w * texture1_bpp // 64
            mask_S = intlog2(texture1_w)
            mask_T = intlog2(texture1_h)
            if mask_S is None:
                # TODO set texel_[01]_repeat_mode_[xy] to clamp/book if corresponding dim isn't a power of two
                tile0.clamp_S = True
                tile0.mask_S = 0
            else:
                tile0.clamp_S = advanced_props.texel_0_repeat_mode_x in {
                    "CLAMP",
                    "BOOK",
                }
                tile0.mask_S = mask_S
            tile0.mirror_S = advanced_props.texel_0_repeat_mode_x in {"MIRROR", "BOOK"}
            tile0.shift_S = encode_shift(advanced_props.texel_0_shift_x)
            if mask_T is None:
                tile0.clamp_T = True
                tile0.mask_T = 0
            else:
                tile0.clamp_T = advanced_props.texel_0_repeat_mode_y in {
                    "CLAMP",
                    "BOOK",
                }
                tile0.mask_T = mask_T
            tile0.mirror_T = advanced_props.texel_0_repeat_mode_y in {"MIRROR", "BOOK"}
            tile0.shift_T = encode_shift(advanced_props.texel_0_shift_y)
            tile0.upper_left_S = 0 + advanced_props.texel_0_offset_x
            tile0.upper_left_T = 0 + advanced_props.texel_0_offset_y
            tile0.lower_right_S = texture1_w - 1 + advanced_props.texel_0_offset_x
            tile0.lower_right_T = texture1_h - 1 + advanced_props.texel_0_offset_y

        tile1 = material_dragex.rdp.tiles.tiles[1]
        tile1.image = texture2
        tile1.format, tile1.size = split_texformat(advanced_props.texel_1_format)
        if tile1.format == "CI":
            raise NotImplementedError("CI formats")  # TODO CI formats
        if tile0.image is None or texture1 == texture2:
            tile1.address = 0
        else:
            assert texture1 is not None
            texture1_w, texture1_h = texture1.size
            texture1_bpp = int(tile0.size)
            assert texture1_w * texture1_bpp % 64 == 0
            tile1.address = texture1_w * texture1_h * texture1_bpp // 64
        tile1.palette = 0
        if texture2 is not None and tuple(texture2.size) != (0, 0):
            # TODO check if s=width, t=height (test with non-square texture)
            texture2_w, texture2_h = texture2.size
            texture2_bpp = int(tile1.size)
            if texture2_w * texture2_h * texture2_bpp > TMEM_SIZE * 8:
                tile1.image = None
            if tile0.image is None:
                material_dragex.uv_basis_s = texture2_w
                material_dragex.uv_basis_t = texture2_h
            if texture2_w * texture2_bpp % 64 != 0:
                tile1.image = None
            tile1.line = texture2_w * texture2_bpp // 64
            mask_S = intlog2(texture2_w)
            mask_T = intlog2(texture2_h)
            if mask_S is None:
                tile1.clamp_S = True
                tile1.mask_S = 0
            else:
                tile1.clamp_S = advanced_props.texel_1_repeat_mode_x in {
                    "CLAMP",
                    "BOOK",
                }
                tile1.mask_S = mask_S
            tile1.mirror_S = advanced_props.texel_1_repeat_mode_x in {"MIRROR", "BOOK"}
            tile1.shift_S = encode_shift(advanced_props.texel_1_shift_x)
            if mask_T is None:
                tile1.clamp_T = True
                tile1.mask_T = 0
            else:
                tile1.clamp_T = advanced_props.texel_1_repeat_mode_y in {
                    "CLAMP",
                    "BOOK",
                }
                tile1.mask_T = mask_T
            tile1.mirror_T = advanced_props.texel_1_repeat_mode_y in {"MIRROR", "BOOK"}
            tile1.shift_T = encode_shift(advanced_props.texel_1_shift_y)
            tile1.upper_left_S = 0 + advanced_props.texel_1_offset_x
            tile1.upper_left_T = 0 + advanced_props.texel_1_offset_y
            tile1.lower_right_S = texture2_w - 1 + advanced_props.texel_1_offset_x
            tile1.lower_right_T = texture2_h - 1 + advanced_props.texel_1_offset_y

        rdp_vals = material_dragex.rdp.vals
        rdp_vals.environment_color = (
            *advanced_props.src_env_color,
            advanced_props.src_env_alpha / 255,
        )
        # TODO implement advanced_props.src_env_write
        rdp_vals.primitive_color = (
            *advanced_props.src_prim_color,
            advanced_props.src_prim_alpha / 255,
        )
        rdp_vals.min_level = 0
        rdp_vals.prim_lod_frac = advanced_props.src_prim_lod_frac
        # TODO implement advanced_props.src_prim_write

        rsp_props = material_dragex.rsp

        rsp_props.zbuffer = advanced_props.z_read or advanced_props.z_write
        shading = advanced_props.shading
        if not ({"SHADE", "SHADE_ALPHA"} & used_sources):
            shading = "NONE"
        if shading == "LIGHTING":
            rsp_props.lighting = True
            rsp_props.vertex_colors = False
        elif shading == "VERTEX_COLORS":
            rsp_props.lighting = False
            rsp_props.vertex_colors = True
        elif shading == "NONE":
            rsp_props.lighting = False
            rsp_props.vertex_colors = False
        else:
            assert False, shading
        rsp_props.cull_front = False
        rsp_props.cull_back = advanced_props.backface_culling
        rsp_props.fog = advanced_props.fog
        # TODO texgen props
        rsp_props.uv_gen_spherical = False
        rsp_props.uv_gen_linear = False
        rsp_props.shade_smooth = True

        one_cycle = True
        if texture2 is not None:
            one_cycle = False
        if advanced_props.fog:
            one_cycle = False
        if advanced_props.template_color_two_cycle:
            one_cycle = False
        if advanced_props.template_alpha_two_cycle:
            one_cycle = False

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
                if advanced_props.alpha_blend_type == "TRANSPARENT"
                else "MEMORY_COVERAGE"
            )
        else:
            om.bl_m1a_0 = "INPUT"
            om.bl_m1b_0 = "INPUT_ALPHA"
            om.bl_m2a_0 = "MEMORY"
            om.bl_m2b_0 = (
                "1_MINUS_A"
                if advanced_props.alpha_blend_type == "TRANSPARENT"
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
        if advanced_props.alpha_blend_type in {"OPAQUE", "CUTOUT"}:
            om.force_blend = False
            om.alpha_cvg_select = True
            om.cvg_x_alpha = advanced_props.alpha_blend_type == "CUTOUT"
            om.z_mode = "DECAL" if advanced_props.decal else "OPAQUE"
            om.cvg_dest = "CLAMP"
            om.color_on_cvg = False
            om.z_update_en = advanced_props.z_write
        elif advanced_props.alpha_blend_type == "TRANSPARENT":
            om.force_blend = True
            om.alpha_cvg_select = False
            om.cvg_x_alpha = False
            # TODO what if advanced_props.decal ?
            om.z_mode = "TRANSPARENT"
            om.cvg_dest = "WRAP"
            om.color_on_cvg = True
            assert not advanced_props.z_write  # TODO
            om.z_update_en = False
        else:
            assert False, advanced_props.alpha_blend_type
        om.image_read_en = True
        om.z_compare_en = advanced_props.z_read
        om.antialias_en = True
        om.z_source_sel = False
        # TODO use advanced_props.alpha_noise
        om.dither_alpha_en = False
        om.alpha_compare_en = advanced_props.alpha_compare
        if advanced_props.alpha_compare:
            rdp_vals.blend_color = (
                *rdp_vals.blend_color[:3],
                advanced_props.src_threshold_alpha / 255,
            )
            if not advanced_props.src_threshold_write:
                # TODO implement src_threshold_write
                raise NotImplementedError("!src_threshold_write yes")

        cb = material_dragex.rdp.combiner
        if advanced_props.template_1_color == "SINGLE":
            if advanced_props.template_1_color_single_src.endswith("_ALPHA"):
                cb.rgb_A_0 = "1"
                cb.rgb_B_0 = "0"
                cb.rgb_C_0 = advanced_props.template_1_color_single_src
                cb.rgb_D_0 = "0"
            else:
                cb.rgb_A_0 = "0"
                cb.rgb_B_0 = "0"
                cb.rgb_C_0 = "0"
                cb.rgb_D_0 = advanced_props.template_1_color_single_src
        elif advanced_props.template_1_color == "LERP":
            cb.rgb_A_0 = advanced_props.template_1_color_lerp_src_2
            cb.rgb_B_0 = advanced_props.template_1_color_lerp_src_1
            cb.rgb_C_0 = advanced_props.template_1_color_lerp_factor
            cb.rgb_D_0 = advanced_props.template_1_color_lerp_src_1
        elif advanced_props.template_1_color == "ADD":
            cb.rgb_A_0 = advanced_props.template_1_color_add_src2
            cb.rgb_B_0 = "0"
            cb.rgb_C_0 = advanced_props.template_1_color_add_factor
            cb.rgb_D_0 = advanced_props.template_1_color_add_src1
        elif advanced_props.template_1_color == "MULT":
            cb.rgb_A_0 = advanced_props.template_1_color_mult_src_1
            cb.rgb_B_0 = "0"
            cb.rgb_C_0 = advanced_props.template_1_color_mult_src_2
            cb.rgb_D_0 = "0"
        else:
            assert False, advanced_props.template_1_color
        if advanced_props.template_color_two_cycle:
            assert not one_cycle
            if advanced_props.template_2_color == "SINGLE":
                if advanced_props.template_2_color_single_src.endswith("_ALPHA"):
                    cb.rgb_A_0 = "1"
                    cb.rgb_B_0 = "0"
                    cb.rgb_C_0 = advanced_props.template_2_color_single_src
                    cb.rgb_D_0 = "0"
                else:
                    cb.rgb_A_0 = "0"
                    cb.rgb_B_0 = "0"
                    cb.rgb_C_0 = "0"
                    cb.rgb_D_0 = advanced_props.template_2_color_single_src
            elif advanced_props.template_2_color == "LERP":
                cb.rgb_A_1 = advanced_props.template_2_color_lerp_src_2
                cb.rgb_B_1 = advanced_props.template_2_color_lerp_src_1
                cb.rgb_C_1 = advanced_props.template_2_color_lerp_factor
                cb.rgb_D_1 = advanced_props.template_2_color_lerp_src_1
            elif advanced_props.template_2_color == "ADD":
                cb.rgb_A_1 = advanced_props.template_2_color_add_src2
                cb.rgb_B_1 = "0"
                cb.rgb_C_1 = advanced_props.template_2_color_add_factor
                cb.rgb_D_1 = advanced_props.template_2_color_add_src1
            elif advanced_props.template_2_color == "MULT":
                cb.rgb_A_1 = advanced_props.template_2_color_mult_src_1
                cb.rgb_B_1 = "0"
                cb.rgb_C_1 = advanced_props.template_2_color_mult_src_2
                cb.rgb_D_1 = "0"
            else:
                assert False, advanced_props.template_2_color
        else:
            if one_cycle:
                cb.rgb_A_1 = cb.rgb_A_0
                cb.rgb_B_1 = cb.rgb_B_0
                cb.rgb_C_1 = cb.rgb_C_0
                cb.rgb_D_1 = cb.rgb_D_0
            else:
                cb.rgb_A_1 = "0"
                cb.rgb_B_1 = "0"
                cb.rgb_C_1 = "0"
                cb.rgb_D_1 = "COMBINED"

        if advanced_props.template_1_alpha == "SINGLE":
            cb.alpha_A_0 = "0"
            cb.alpha_B_0 = "0"
            cb.alpha_C_0 = "0"
            cb.alpha_D_0 = advanced_props.template_1_alpha_single_src
        elif advanced_props.template_1_alpha == "LERP":
            cb.alpha_A_0 = advanced_props.template_1_alpha_lerp_src_2
            cb.alpha_B_0 = advanced_props.template_1_alpha_lerp_src_1
            cb.alpha_C_0 = advanced_props.template_1_alpha_lerp_factor
            cb.alpha_D_0 = advanced_props.template_1_alpha_lerp_src_1
        elif advanced_props.template_1_alpha == "ADD":
            cb.alpha_A_0 = advanced_props.template_1_alpha_add_src2
            cb.alpha_B_0 = "0"
            cb.alpha_C_0 = advanced_props.template_1_alpha_add_factor
            cb.alpha_D_0 = advanced_props.template_1_alpha_add_src1
        elif advanced_props.template_1_alpha == "MULT":
            cb.alpha_A_0 = advanced_props.template_1_alpha_mult_src_1
            cb.alpha_B_0 = "0"
            cb.alpha_C_0 = advanced_props.template_1_alpha_mult_src_2
            cb.alpha_D_0 = "0"
        else:
            assert False, advanced_props.template_1_alpha
        if advanced_props.template_alpha_two_cycle:
            assert not one_cycle
            if advanced_props.template_2_alpha == "SINGLE":
                cb.alpha_A_1 = "0"
                cb.alpha_B_1 = "0"
                cb.alpha_C_1 = "0"
                cb.alpha_D_1 = advanced_props.template_2_alpha_single_src
            elif advanced_props.template_2_alpha == "LERP":
                cb.alpha_A_1 = advanced_props.template_2_alpha_lerp_src_2
                cb.alpha_B_1 = advanced_props.template_2_alpha_lerp_src_1
                cb.alpha_C_1 = advanced_props.template_2_alpha_lerp_factor
                cb.alpha_D_1 = advanced_props.template_2_alpha_lerp_src_1
            elif advanced_props.template_2_alpha == "ADD":
                cb.alpha_A_1 = advanced_props.template_2_alpha_add_src2
                cb.alpha_B_1 = "0"
                cb.alpha_C_1 = advanced_props.template_2_alpha_add_factor
                cb.alpha_D_1 = advanced_props.template_2_alpha_add_src1
            elif advanced_props.template_2_alpha == "MULT":
                cb.alpha_A_1 = advanced_props.template_2_alpha_mult_src_1
                cb.alpha_B_1 = "0"
                cb.alpha_C_1 = advanced_props.template_2_alpha_mult_src_2
                cb.alpha_D_1 = "0"
            else:
                assert False, advanced_props.template_2_alpha
        else:
            if one_cycle:
                cb.alpha_A_1 = cb.alpha_A_0
                cb.alpha_B_1 = cb.alpha_B_0
                cb.alpha_C_1 = cb.alpha_C_0
                cb.alpha_D_1 = cb.alpha_D_0
            else:
                cb.alpha_A_1 = "0"
                cb.alpha_B_1 = "0"
                cb.alpha_C_1 = "0"
                cb.alpha_D_1 = "COMBINED"

    @staticmethod
    def on_mode_prop_update(_self, context: bpy.types.Context):
        material = context.material
        assert material is not None
        AdvancedMaterialMode.apply_mode_props(material)


COMBINER_PASS_SOURCE_COLOR1_SINGLE_SRC = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENVIRONMENT_ALPHA", "ENV_ALPHA", ""),
    ("PRIMITIVE_ALPHA", "PRIM_ALPHA", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
]
COMBINER_PASS_SOURCE_COLOR1_LERP_SRC1 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("0", "ZERO", ""),
]
COMBINER_PASS_SOURCE_COLOR1_LERP_SRC2 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("0", "ZERO", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_COLOR1_LERP_FACTOR = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENVIRONMENT_ALPHA", "ENV_ALPHA", ""),
    ("PRIMITIVE_ALPHA", "PRIM_ALPHA", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
]
COMBINER_PASS_SOURCE_COLOR1_ADD_SRC1 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_COLOR1_ADD_SRC2 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_COLOR1_ADD_FACTOR = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENVIRONMENT_ALPHA", "ENV_ALPHA", ""),
    ("PRIMITIVE_ALPHA", "PRIM_ALPHA", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
]
COMBINER_PASS_SOURCE_COLOR1_MULT_SRC1 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
]
COMBINER_PASS_SOURCE_COLOR1_MULT_SRC2 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENVIRONMENT_ALPHA", "ENV_ALPHA", ""),
    ("PRIMITIVE_ALPHA", "PRIM_ALPHA", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
]

COMBINER_PASS_SOURCE_COLOR2_SINGLE_SRC = COMBINER_PASS_SOURCE_COLOR1_SINGLE_SRC + [
    ("COMBINED", "COMBINED", ""),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", ""),
]
COMBINER_PASS_SOURCE_COLOR2_LERP_SRC1 = COMBINER_PASS_SOURCE_COLOR1_LERP_SRC1 + [
    ("COMBINED", "COMBINED", ""),
]
COMBINER_PASS_SOURCE_COLOR2_LERP_SRC2 = COMBINER_PASS_SOURCE_COLOR1_LERP_SRC2 + [
    ("COMBINED", "COMBINED", ""),
]
COMBINER_PASS_SOURCE_COLOR2_LERP_FACTOR = COMBINER_PASS_SOURCE_COLOR1_LERP_FACTOR + [
    ("COMBINED", "COMBINED", ""),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", ""),
]
COMBINER_PASS_SOURCE_COLOR2_ADD_SRC1 = COMBINER_PASS_SOURCE_COLOR1_ADD_SRC1 + [
    ("COMBINED", "COMBINED", ""),
]
COMBINER_PASS_SOURCE_COLOR2_ADD_SRC2 = COMBINER_PASS_SOURCE_COLOR1_ADD_SRC2 + [
    ("COMBINED", "COMBINED", ""),
]
COMBINER_PASS_SOURCE_COLOR2_ADD_FACTOR = COMBINER_PASS_SOURCE_COLOR1_ADD_FACTOR + [
    ("COMBINED", "COMBINED", ""),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", ""),
]
COMBINER_PASS_SOURCE_COLOR2_MULT_SRC1 = COMBINER_PASS_SOURCE_COLOR1_MULT_SRC1 + [
    ("COMBINED", "COMBINED", ""),
]
COMBINER_PASS_SOURCE_COLOR2_MULT_SRC2 = COMBINER_PASS_SOURCE_COLOR1_MULT_SRC2 + [
    ("COMBINED", "COMBINED", ""),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", ""),
]

COMBINER_PASS_SOURCE_ALPHA1_SINGLE_SRC = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_LERP_SRC1 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("0", "ZERO", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_LERP_SRC2 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("0", "ZERO", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_LERP_FACTOR = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_ADD_SRC1 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_ADD_SRC2 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("1", "ONE", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_ADD_FACTOR = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_MULT_SRC1 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
]
COMBINER_PASS_SOURCE_ALPHA1_MULT_SRC2 = [
    ("SHADE", "SHADE", ""),
    ("ENVIRONMENT", "ENVIRONMENT", ""),
    ("PRIMITIVE", "PRIMITIVE", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
]

COMBINER_PASS_SOURCE_ALPHA2_SINGLE_SRC = COMBINER_PASS_SOURCE_ALPHA1_SINGLE_SRC + [
    ("COMBINED", "COMBINED", "")
]
COMBINER_PASS_SOURCE_ALPHA2_LERP_SRC1 = COMBINER_PASS_SOURCE_ALPHA1_LERP_SRC1 + [
    ("COMBINED", "COMBINED", "")
]
COMBINER_PASS_SOURCE_ALPHA2_LERP_SRC2 = COMBINER_PASS_SOURCE_ALPHA1_LERP_SRC2 + [
    ("COMBINED", "COMBINED", "")
]
COMBINER_PASS_SOURCE_ALPHA2_LERP_FACTOR = COMBINER_PASS_SOURCE_ALPHA1_LERP_FACTOR
COMBINER_PASS_SOURCE_ALPHA2_ADD_SRC1 = COMBINER_PASS_SOURCE_ALPHA1_ADD_SRC1 + [
    ("COMBINED", "COMBINED", "")
]
COMBINER_PASS_SOURCE_ALPHA2_ADD_SRC2 = COMBINER_PASS_SOURCE_ALPHA1_ADD_SRC2 + [
    ("COMBINED", "COMBINED", "")
]
COMBINER_PASS_SOURCE_ALPHA2_ADD_FACTOR = COMBINER_PASS_SOURCE_ALPHA1_ADD_FACTOR
COMBINER_PASS_SOURCE_ALPHA2_MULT_SRC1 = COMBINER_PASS_SOURCE_ALPHA1_MULT_SRC1 + [
    ("COMBINED", "COMBINED", "")
]
COMBINER_PASS_SOURCE_ALPHA2_MULT_SRC2 = COMBINER_PASS_SOURCE_ALPHA1_MULT_SRC2

COMBINER_TEMPLATES = [
    ("SINGLE", "Single", "Evaluate to a single source"),
    # src1: D/B
    # src2: A
    # factor: C
    ("LERP", "Lerp", "Mix two sources according to a factor"),
    # src1: D
    # src2: A
    # factor: C
    ("ADD", "Add", "Add two sources, after multiplying one with a factor"),
    # src1: A
    # src2: C
    ("MULT", "Multiply", "Multiply two sources together"),
]

TEXEL_FORMATS = [
    ("RGBA32", "RGBA32", ""),
    ("RGBA16", "RGBA16", ""),
    ("IA16", "IA16", ""),
    ("IA8", "IA8", ""),
    ("IA4", "IA4", ""),
    ("I8", "I8", ""),
    ("I4", "I4", ""),
    ("CI8", "CI8", ""),
    ("CI4", "CI4", ""),
]
TEXEL_FORMATS_SPLIT = {
    "RGBA32": ("RGBA", "32"),
    "RGBA16": ("RGBA", "16"),
    "IA16": ("IA", "16"),
    "IA8": ("IA", "8"),
    "IA4": ("IA", "4"),
    "I8": ("I", "8"),
    "I4": ("I", "4"),
    "CI8": ("CI", "8"),
    "CI4": ("CI", "4"),
}


def split_texformat(format: str):
    return TEXEL_FORMATS_SPLIT[format]


ALPHA_BLEND_TYPES = [
    ("OPAQUE", "Opaque", ""),
    ("CUTOUT", "Cutout", ""),
    ("TRANSPARENT", "Transparent", ""),
]

REPEAT_MODES = [
    ("WRAP", "Wrap", ""),
    ("CLAMP", "Clamp", ""),
    ("MIRROR", "Mirror", ""),
    ("BOOK", "Book", ""),
]


class DragExMaterialModesAdvancedProperties(bpy.types.PropertyGroup):

    template_1_color: bpy.props.EnumProperty(
        items=COMBINER_TEMPLATES,
        default="MULT",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_single_src: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_SINGLE_SRC,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_lerp_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_LERP_SRC1,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_lerp_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_LERP_SRC2,
        default="TEX1",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_lerp_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_LERP_FACTOR,
        default="ENVIRONMENT_ALPHA",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_add_src1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_ADD_SRC1,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_add_src2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_ADD_SRC2,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_add_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_ADD_FACTOR,
        default="ENVIRONMENT_ALPHA",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_mult_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_MULT_SRC1,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_color_mult_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR1_MULT_SRC2,
        default="SHADE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    template_2_color: bpy.props.EnumProperty(
        items=COMBINER_TEMPLATES,
        default="MULT",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_single_src: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_SINGLE_SRC,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_lerp_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_LERP_SRC1,
        default="PRIMITIVE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_lerp_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_LERP_SRC2,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_lerp_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_LERP_FACTOR,
        default="PRIMITIVE_ALPHA",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_add_src1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_ADD_SRC1,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_add_src2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_ADD_SRC2,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_add_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_ADD_FACTOR,
        default="PRIMITIVE_ALPHA",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_mult_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_MULT_SRC1,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_color_mult_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_COLOR2_MULT_SRC2,
        default="PRIMITIVE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    template_1_alpha: bpy.props.EnumProperty(
        items=COMBINER_TEMPLATES,
        default="MULT",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_single_src: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_SINGLE_SRC,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_lerp_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_LERP_SRC1,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_lerp_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_LERP_SRC2,
        default="TEX1",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_lerp_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_LERP_FACTOR,
        default="ENVIRONMENT",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_add_src1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_ADD_SRC1,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_add_src2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_ADD_SRC2,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_add_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_ADD_FACTOR,
        default="ENVIRONMENT",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_mult_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_MULT_SRC1,
        default="TEX0",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_1_alpha_mult_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA1_MULT_SRC2,
        default="SHADE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    template_2_alpha: bpy.props.EnumProperty(
        items=COMBINER_TEMPLATES,
        default="MULT",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_single_src: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_SINGLE_SRC,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_lerp_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_LERP_SRC1,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_lerp_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_LERP_SRC2,
        default="PRIMITIVE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_lerp_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_LERP_FACTOR,
        default="ENVIRONMENT",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_add_src1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_ADD_SRC1,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_add_src2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_ADD_SRC2,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_add_factor: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_ADD_FACTOR,
        default="PRIMITIVE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_mult_src_1: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_MULT_SRC1,
        default="COMBINED",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_2_alpha_mult_src_2: bpy.props.EnumProperty(
        items=COMBINER_PASS_SOURCE_ALPHA2_MULT_SRC2,
        default="PRIMITIVE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    template_color_two_cycle: bpy.props.BoolProperty(
        default=False,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    template_alpha_two_cycle: bpy.props.BoolProperty(
        default=False,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    texel_0_image: bpy.props.PointerProperty(
        name="Texture 0",
        type=bpy.types.Image,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_0_format: bpy.props.EnumProperty(
        items=TEXEL_FORMATS,
        default="RGBA16",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_0_shift_x: bpy.props.IntProperty(
        default=0,
        min=-5,
        max=10,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_0_shift_y: bpy.props.IntProperty(
        default=0,
        min=-5,
        max=10,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    # TODO min/max for texel_[01]_offset_[xy]
    texel_0_offset_x: bpy.props.FloatProperty(
        default=0,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_0_offset_y: bpy.props.FloatProperty(
        default=0,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_0_repeat_mode_x: bpy.props.EnumProperty(
        default="WRAP",
        items=REPEAT_MODES,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_0_repeat_mode_y: bpy.props.EnumProperty(
        default="WRAP",
        items=REPEAT_MODES,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    # TODO implement texel_[01]_segment_address in the exporter
    texel_0_segment_address: bpy.props.StringProperty(
        default="",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    texel_1_image: bpy.props.PointerProperty(
        name="Texture 1",
        type=bpy.types.Image,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_format: bpy.props.EnumProperty(
        items=TEXEL_FORMATS,
        default="RGBA16",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_shift_x: bpy.props.IntProperty(
        default=0,
        min=-5,
        max=10,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_shift_y: bpy.props.IntProperty(
        default=0,
        min=-5,
        max=10,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_offset_x: bpy.props.FloatProperty(
        default=0,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_offset_y: bpy.props.FloatProperty(
        default=0,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_repeat_mode_x: bpy.props.EnumProperty(
        default="WRAP",
        items=REPEAT_MODES,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_repeat_mode_y: bpy.props.EnumProperty(
        default="WRAP",
        items=REPEAT_MODES,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    texel_1_segment_address: bpy.props.StringProperty(
        default="",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    # TODO implement src_{env,prim,threshold}_write in the exporter
    src_env_write: bpy.props.BoolProperty(
        default=True,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    src_env_color: bpy.props.FloatVectorProperty(
        subtype="COLOR",
        default=(1, 1, 1),
        min=0,
        max=1,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    src_env_alpha: bpy.props.IntProperty(
        default=127,
        min=0,
        max=0xFF,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    src_prim_write: bpy.props.BoolProperty(
        default=True,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    src_prim_color: bpy.props.FloatVectorProperty(
        subtype="COLOR",
        default=(1, 1, 1),
        min=0,
        max=1,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    src_prim_alpha: bpy.props.IntProperty(
        default=0xFF,
        min=0,
        max=0xFF,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    src_prim_lod_frac: bpy.props.IntProperty(
        min=0,
        max=0xFF,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )

    src_threshold_write: bpy.props.BoolProperty(
        default=True,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    src_threshold_alpha: bpy.props.IntProperty(
        default=0,
        min=0,
        max=0xFF,
        update=AdvancedMaterialMode.on_mode_prop_update,
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
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    alpha_blend_type: bpy.props.EnumProperty(
        name="Alpha Blend Type",
        items=ALPHA_BLEND_TYPES,
        default="OPAQUE",
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    backface_culling: bpy.props.BoolProperty(
        default=True,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    fog: bpy.props.BoolProperty(
        default=True,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    decal: bpy.props.BoolProperty(
        default=False,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    z_read: bpy.props.BoolProperty(
        default=True,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    z_write: bpy.props.BoolProperty(
        default=True,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    # TODO implement enable_pointlights in the exporter ?
    enable_pointlights: bpy.props.BoolProperty(
        default=False,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    alpha_noise: bpy.props.BoolProperty(
        default=False,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    alpha_compare: bpy.props.BoolProperty(
        default=False,
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
    # TODO implement dlist_call in the (f3dex2) exporter
    dlist_call: bpy.props.StringProperty(
        name="DList Call",
        description=(
            "Segmented address of a display list to call, "
            "as part of the material's display list"
        ),
        update=AdvancedMaterialMode.on_mode_prop_update,
    )
