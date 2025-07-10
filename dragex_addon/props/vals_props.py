import bpy


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
