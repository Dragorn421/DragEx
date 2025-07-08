import bpy

# copied from fast64
combiner_enums = {
    "Case A": (
        ("COMBINED", "Combined Color", "Combined Color"),
        ("TEXEL0", "Texture 0 Color", "Texture 0 Color"),
        ("TEXEL1", "Texture 1 Color", "Texture 1 Color"),
        ("PRIMITIVE", "Primitive Color", "Primitive Color"),
        ("SHADE", "Shade Color", "Shade Color"),
        ("ENVIRONMENT", "Environment Color", "Environment Color"),
        ("1", "1", "1"),
        ("NOISE", "Noise", "Noise"),
        ("0", "0", "0"),
    ),
    "Case B": (
        ("COMBINED", "Combined Color", "Combined Color"),
        ("TEXEL0", "Texture 0 Color", "Texture 0 Color"),
        ("TEXEL1", "Texture 1 Color", "Texture 1 Color"),
        ("PRIMITIVE", "Primitive Color", "Primitive Color"),
        ("SHADE", "Shade Color", "Shade Color"),
        ("ENVIRONMENT", "Environment Color", "Environment Color"),
        ("CENTER", "Chroma Key Center", "Chroma Key Center"),
        ("K4", "YUV Convert K4", "YUV Convert K4"),
        ("0", "0", "0"),
    ),
    "Case C": (
        ("COMBINED", "Combined Color", "Combined Color"),
        ("TEXEL0", "Texture 0 Color", "Texture 0 Color"),
        ("TEXEL1", "Texture 1 Color", "Texture 1 Color"),
        ("PRIMITIVE", "Primitive Color", "Primitive Color"),
        ("SHADE", "Shade Color", "Shade Color"),
        ("ENVIRONMENT", "Environment Color", "Environment Color"),
        ("SCALE", "Chroma Key Scale", "Chroma Key Scale"),
        ("COMBINED_ALPHA", "Combined Color Alpha", "Combined Color Alpha"),
        ("TEXEL0_ALPHA", "Texture 0 Alpha", "Texture 0 Alpha"),
        ("TEXEL1_ALPHA", "Texture 1 Alpha", "Texture 1 Alpha"),
        ("PRIMITIVE_ALPHA", "Primitive Color Alpha", "Primitive Color Alpha"),
        ("SHADE_ALPHA", "Shade Color Alpha", "Shade Color Alpha"),
        ("ENV_ALPHA", "Environment Color Alpha", "Environment Color Alpha"),
        ("LOD_FRACTION", "LOD Fraction", "LOD Fraction"),
        ("PRIM_LOD_FRAC", "Primitive LOD Fraction", "Primitive LOD Fraction"),
        ("K5", "YUV Convert K5", "YUV Convert K5"),
        ("0", "0", "0"),
    ),
    "Case D": (
        ("COMBINED", "Combined Color", "Combined Color"),
        ("TEXEL0", "Texture 0 Color", "Texture 0 Color"),
        ("TEXEL1", "Texture 1 Color", "Texture 1 Color"),
        ("PRIMITIVE", "Primitive Color", "Primitive Color"),
        ("SHADE", "Shade Color", "Shade Color"),
        ("ENVIRONMENT", "Environment Color", "Environment Color"),
        ("1", "1", "1"),
        ("0", "0", "0"),
    ),
    "Case A Alpha": (
        ("COMBINED", "Combined Color Alpha", "Combined Color Alpha"),
        ("TEXEL0", "Texture 0 Alpha", "Texture 0 Alpha"),
        ("TEXEL1", "Texture 1 Alpha", "Texture 1 Alpha"),
        ("PRIMITIVE", "Primitive Color Alpha", "Primitive Color Alpha"),
        ("SHADE", "Shade Color Alpha", "Shade Color Alpha"),
        ("ENVIRONMENT", "Environment Color Alpha", "Environment Color Alpha"),
        ("1", "1", "1"),
        ("0", "0", "0"),
    ),
    "Case B Alpha": (
        ("COMBINED", "Combined Color Alpha", "Combined Color Alpha"),
        ("TEXEL0", "Texture 0 Alpha", "Texture 0 Alpha"),
        ("TEXEL1", "Texture 1 Alpha", "Texture 1 Alpha"),
        ("PRIMITIVE", "Primitive Color Alpha", "Primitive Color Alpha"),
        ("SHADE", "Shade Color Alpha", "Shade Color Alpha"),
        ("ENVIRONMENT", "Environment Color Alpha", "Environment Color Alpha"),
        ("1", "1", "1"),
        ("0", "0", "0"),
    ),
    "Case C Alpha": (
        ("LOD_FRACTION", "LOD Fraction", "LOD Fraction"),
        ("TEXEL0", "Texture 0 Alpha", "Texture 0 Alpha"),
        ("TEXEL1", "Texture 1 Alpha", "Texture 1 Alpha"),
        ("PRIMITIVE", "Primitive Color Alpha", "Primitive Color Alpha"),
        ("SHADE", "Shade Color Alpha", "Shade Color Alpha"),
        ("ENVIRONMENT", "Environment Color Alpha", "Environment Color Alpha"),
        ("PRIM_LOD_FRAC", "Primitive LOD Fraction", "Primitive LOD Fraction"),
        ("0", "0", "0"),
    ),
    "Case D Alpha": (
        ("COMBINED", "Combined Color Alpha", "Combined Color Alpha"),
        ("TEXEL0", "Texture 0 Alpha", "Texture 0 Alpha"),
        ("TEXEL1", "Texture 1 Alpha", "Texture 1 Alpha"),
        ("PRIMITIVE", "Primitive Color Alpha", "Primitive Color Alpha"),
        ("SHADE", "Shade Color Alpha", "Shade Color Alpha"),
        ("ENVIRONMENT", "Environment Color Alpha", "Environment Color Alpha"),
        ("1", "1", "1"),
        ("0", "0", "0"),
    ),
}
enumTexFormat = [
    ("I4", "Intensity 4-bit", "Intensity 4-bit"),
    ("I8", "Intensity 8-bit", "Intensity 8-bit"),
    ("IA4", "Intensity Alpha 4-bit", "Intensity Alpha 4-bit"),
    ("IA8", "Intensity Alpha 8-bit", "Intensity Alpha 8-bit"),
    ("IA16", "Intensity Alpha 16-bit", "Intensity Alpha 16-bit"),
    ("CI4", "Color Index 4-bit", "Color Index 4-bit"),
    ("CI8", "Color Index 8-bit", "Color Index 8-bit"),
    ("RGBA16", "RGBA 16-bit", "RGBA 16-bit"),
    ("RGBA32", "RGBA 32-bit", "RGBA 32-bit"),
    # ('YUV16','YUV 16-bit', 'YUV 16-bit'),
]
enumCIFormat = [
    ("RGBA16", "RGBA 16-bit", "RGBA 16-bit"),
    ("IA16", "Intensity Alpha 16-bit", "Intensity Alpha 16-bit"),
]


# copied from fast64
class CombinerProperty(bpy.types.PropertyGroup):
    A: bpy.props.EnumProperty(
        name="A",
        description="A",
        items=combiner_enums["Case A"],
        default="TEXEL0",
    )

    B: bpy.props.EnumProperty(
        name="B",
        description="B",
        items=combiner_enums["Case B"],
        default="0",
    )

    C: bpy.props.EnumProperty(
        name="C",
        description="C",
        items=combiner_enums["Case C"],
        default="SHADE",
    )

    D: bpy.props.EnumProperty(
        name="D",
        description="D",
        items=combiner_enums["Case D"],
        default="0",
    )

    A_alpha: bpy.props.EnumProperty(
        name="A Alpha",
        description="A Alpha",
        items=combiner_enums["Case A Alpha"],
        default="0",
    )

    B_alpha: bpy.props.EnumProperty(
        name="B Alpha",
        description="B Alpha",
        items=combiner_enums["Case B Alpha"],
        default="0",
    )

    C_alpha: bpy.props.EnumProperty(
        name="C Alpha",
        description="C Alpha",
        items=combiner_enums["Case C Alpha"],
        default="0",
    )

    D_alpha: bpy.props.EnumProperty(
        name="D Alpha",
        description="D Alpha",
        items=combiner_enums["Case D Alpha"],
        default="ENVIRONMENT",
    )

    def draw(self, layout: bpy.types.UILayout):
        layout.prop(self, "A")
        layout.prop(self, "B")
        layout.prop(self, "C")
        layout.prop(self, "D")
        layout.prop(self, "A_alpha")
        layout.prop(self, "B_alpha")
        layout.prop(self, "C_alpha")
        layout.prop(self, "D_alpha")


# copied from fast64
class TextureFieldProperty(bpy.types.PropertyGroup):
    clamp: bpy.props.BoolProperty(
        name="Clamp",
    )
    mirror: bpy.props.BoolProperty(
        name="Mirror",
    )
    low: bpy.props.FloatProperty(
        name="Low",
        min=0,
        max=1023.75,
    )
    high: bpy.props.FloatProperty(
        name="High",
        min=0,
        max=1023.75,
    )
    mask: bpy.props.IntProperty(
        name="Mask",
        min=0,
        max=15,
        default=5,
    )
    shift: bpy.props.IntProperty(
        name="Shift",
        min=-5,
        max=10,
    )

    def draw(self, layout: bpy.types.UILayout):
        layout.prop(self, "clamp")
        layout.prop(self, "mirror")
        layout.prop(self, "low")
        layout.prop(self, "high")
        layout.prop(self, "mask")
        layout.prop(self, "shift")


# copied from fast64
class TextureProperty(bpy.types.PropertyGroup):
    image: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Texture",
    )

    tex_format: bpy.props.EnumProperty(
        name="Format",
        items=enumTexFormat,
        default="RGBA16",
    )
    ci_format: bpy.props.EnumProperty(
        name="CI Format",
        items=enumCIFormat,
        default="RGBA16",
    )
    S_: bpy.props.PointerProperty(type=TextureFieldProperty)
    T_: bpy.props.PointerProperty(type=TextureFieldProperty)

    @property
    def S(self) -> TextureFieldProperty:
        return self.S_

    @property
    def T(self) -> TextureFieldProperty:
        return self.T_

    def draw(self, layout: bpy.types.UILayout):
        layout.template_ID(self, "image", new="image.new", open="image.open")
        layout.prop(self, "tex_format")
        layout.prop(self, "ci_format")

        box = layout.box()
        box.label(text="S")
        self.S.draw(box)

        box = layout.box()
        box.label(text="T")
        self.T.draw(box)


class QADProps(bpy.types.PropertyGroup):
    texture0_: bpy.props.PointerProperty(type=TextureProperty)
    texture1_: bpy.props.PointerProperty(type=TextureProperty)
    combiner1_: bpy.props.PointerProperty(type=CombinerProperty)
    combiner2_: bpy.props.PointerProperty(type=CombinerProperty)

    @property
    def texture0(self) -> TextureProperty:
        return self.texture0_

    @property
    def texture1(self) -> TextureProperty:
        return self.texture1_

    @property
    def combiner1(self) -> CombinerProperty:
        return self.combiner1_

    @property
    def combiner2(self) -> CombinerProperty:
        return self.combiner2_

    prim_color: bpy.props.FloatVectorProperty(
        name="Primitive Color",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
    )
    env_color: bpy.props.FloatVectorProperty(
        name="Environment Color",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
    )

    def draw(self, layout: bpy.types.UILayout):
        box = layout.box()
        box.label(text="Combiner 1")
        self.combiner1.draw(box)

        box = layout.box()
        box.label(text="Combiner 2")
        self.combiner2.draw(box)

        box = layout.box()
        box.label(text="Texture 0")
        self.texture0.draw(box)

        box = layout.box()
        box.label(text="Texture 1")
        self.texture1.draw(box)

        layout.prop(self, "prim_color")
        layout.prop(self, "env_color")


classes = (
    TextureFieldProperty,
    TextureProperty,
    CombinerProperty,
    QADProps,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
