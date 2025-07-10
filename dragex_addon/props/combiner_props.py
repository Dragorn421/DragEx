import bpy


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
