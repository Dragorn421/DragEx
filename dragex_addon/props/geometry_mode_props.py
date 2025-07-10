import bpy


class DragExMaterialGeometryModeProperties(bpy.types.PropertyGroup):
    lighting: bpy.props.BoolProperty(
        name="G_LIGHTING",
        description=(
            "When on, G_LIGHTING causes the vertex shading to be computed based on"
            " vertex normals and current lights.\n"
            "When off, the vertex shading is simply taken from vertex colors."
        ),
    )
