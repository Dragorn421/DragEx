import bpy


class QADProps(bpy.types.PropertyGroup):

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
        layout.prop(self, "prim_color")
        layout.prop(self, "env_color")


classes = (QADProps,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
