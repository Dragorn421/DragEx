import bpy


class DragExMaterialRSPProperties(bpy.types.PropertyGroup):
    zbuffer: bpy.props.BoolProperty(
        name="Z Buffer",
        description="Whether emitted triangles have depth information",
    )
    lighting: bpy.props.BoolProperty(
        name="Lighting",
        description="Whether vertices are shaded according to the active lights",
    )
    vertex_colors: bpy.props.BoolProperty(
        name="Vertex colors",
        description="Whether vertices are shaded using their provided colors",
    )
    cull_front: bpy.props.BoolProperty(
        name="Cull front",
        description="Whether triangles are invisible from their front side",
    )
    cull_back: bpy.props.BoolProperty(
        name="Cull back",
        description="Whether triangles are invisible from their back side",
    )
    fog: bpy.props.BoolProperty(
        name="Fog",
        description="Compute vertex shade alpha based on distance to camera",
    )
    uv_gen_spherical: bpy.props.BoolProperty(
        name="UV Gen Spherical",
        description='Compute vertex UVs from normals ("spherical")',
    )
    uv_gen_linear: bpy.props.BoolProperty(
        name="UV Gen Linear",
        description='Compute vertex UVs from normals ("linear")',
    )
    shade_smooth: bpy.props.BoolProperty(
        name="Shade Smooth",
        description=(
            "Use smooth shading, meaning the color across a triangle is"
            " interpolated from the color of its vertices"
        ),
    )
