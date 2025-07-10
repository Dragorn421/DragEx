import bpy


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
