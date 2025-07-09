import bpy

# copied from fast64
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

    @property
    def texture0(self) -> TextureProperty:
        return self.texture0_

    @property
    def texture1(self) -> TextureProperty:
        return self.texture1_

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
    QADProps,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
