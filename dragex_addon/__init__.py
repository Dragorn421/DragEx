import numpy as np

import bpy

from .build_id import BUILD_ID


def new_float_buf(len):
    return np.empty(
        shape=len,
        dtype=np.float32,
        order="C",
    )


def new_uint_buf(len):
    return np.empty(
        shape=len,
        dtype=np.uint32,  # np.uint leads to L format (unsigned long)
        order="C",
    )


C_IDENTIFIER_ALLOWED = frozenset(
    "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_" "0123456789"
)
C_IDENTIFIER_START_ALLOWED = frozenset(
    "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_"
)


def make_c_identifier(s: str):
    if s == "":
        return "_"
    s = "".join(c if c in C_IDENTIFIER_ALLOWED else "_" for c in s)
    if s[0] not in C_IDENTIFIER_START_ALLOWED:
        s = "_" + s
    return s


class DragExBackendDemoOperator(bpy.types.Operator):
    bl_idname = "dragex.dragex_backend_demo"
    bl_label = "DragEx backend demo"

    def execute(self, context):
        import time

        start = time.time()

        # TODO trying to not import at the module level, see if this is less jank this way
        # TODO catch ImportError
        import dragex_backend

        print("Hello World")
        assert context.object is not None
        mesh = context.object.data
        assert isinstance(mesh, bpy.types.Mesh)
        # note: if size is too small, error is undescriptive:
        # "RuntimeError: internal error setting the array"
        buf_vertices_co = new_float_buf(3 * len(mesh.vertices))
        mesh.vertices.foreach_get("co", buf_vertices_co)
        mesh.calc_loop_triangles()
        buf_triangles_loops = new_uint_buf(3 * len(mesh.loop_triangles))
        buf_triangles_material_index = new_uint_buf(len(mesh.loop_triangles))
        mesh.loop_triangles[0].loops
        mesh.loop_triangles[0].material_index
        mesh.loop_triangles.foreach_get("loops", buf_triangles_loops)
        mesh.loop_triangles.foreach_get("material_index", buf_triangles_material_index)
        mesh.loops[0].vertex_index
        mesh.loops[0].normal
        buf_loops_vertex_index = new_uint_buf(len(mesh.loops))
        buf_loops_normal = new_float_buf(3 * len(mesh.loops))
        mesh.loops.foreach_get("vertex_index", buf_loops_vertex_index)
        mesh.loops.foreach_get("normal", buf_loops_normal)

        active_color_attribute = mesh.color_attributes.active_color
        if active_color_attribute is None:
            buf_corners_color = None
        else:
            if active_color_attribute.domain == "CORNER":
                if active_color_attribute.data_type in {"FLOAT_COLOR", "BYTE_COLOR"}:
                    assert isinstance(
                        active_color_attribute,
                        (
                            bpy.types.FloatColorAttribute,
                            bpy.types.ByteColorAttribute,
                        ),
                    )
                    # Note: for ByteColorAttribute too the color uses floats
                    buf_corners_color = new_float_buf(4 * len(mesh.loops))
                    active_color_attribute.data.foreach_get("color", buf_corners_color)
                else:
                    raise NotImplementedError(active_color_attribute.data_type)
            else:
                # TODO at least POINT (vertex) colors?
                raise NotImplementedError(active_color_attribute.domain)

        active_uv_layer = mesh.uv_layers.active
        if active_uv_layer is None:
            buf_loops_uv = None
        else:
            buf_loops_uv = new_float_buf(2 * len(mesh.loops))
            active_uv_layer.uv.foreach_get("vector", buf_loops_uv)

        material_infos = list[dragex_backend.MaterialInfo | None]()
        for mat_index in range(len(context.object.material_slots)):
            mat = context.object.material_slots[mat_index].material
            if mat is None:
                mat_info = None
            else:
                mat_dragex: DragExMaterialProperties = mat.dragex
                mat_geomode = mat_dragex.geometry_mode
                mat_info = dragex_backend.MaterialInfo(
                    name=make_c_identifier(mat.name),
                    uv_basis_s=mat_dragex.uv_basis_s,
                    uv_basis_t=mat_dragex.uv_basis_t,
                    lighting=mat_geomode.lighting,
                )
            material_infos.append(mat_info)
        default_material_info = dragex_backend.MaterialInfo(
            name="DEFAULT_MATERIAL",
            uv_basis_s=1,
            uv_basis_t=1,
            lighting=True,
        )
        mesh_info = dragex_backend.create_MeshInfo(
            buf_vertices_co,
            buf_triangles_loops,
            buf_triangles_material_index,
            buf_loops_vertex_index,
            buf_loops_normal,
            buf_corners_color,
            buf_loops_uv,
            material_infos,
            default_material_info,
        )
        mesh_info.write_c("/home/dragorn421/Documents/dragex/dragex_attempt2/output.c")
        end = time.time()
        print("dragex_backend_demo took", end - start, "seconds")
        return {"FINISHED"}


class DragExMaterialGeometryModeProperties(bpy.types.PropertyGroup):
    lighting: bpy.props.BoolProperty(
        name="G_LIGHTING",
        description=(
            "When on, G_LIGHTING causes the vertex shading to be computed based on"
            " vertex normals and current lights.\n"
            "When off, the vertex shading is simply taken from vertex colors."
        ),
    )


class DragExMaterialProperties(bpy.types.PropertyGroup):
    uv_basis_s: bpy.props.IntProperty(name="UV Basis S", min=1, default=1)
    uv_basis_t: bpy.props.IntProperty(name="UV Basis T", min=1, default=1)

    geometry_mode_: bpy.props.PointerProperty(type=DragExMaterialGeometryModeProperties)

    @property
    def geometry_mode(self) -> DragExMaterialGeometryModeProperties:
        return self.geometry_mode_


class DragExMaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_dragex"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex: DragExMaterialProperties = mat.dragex
        mat_geomode = mat_dragex.geometry_mode
        self.layout.prop(mat_geomode, "lighting")
        self.layout.prop(mat_dragex, "uv_basis_s")
        self.layout.prop(mat_dragex, "uv_basis_t")


classes = (
    DragExMaterialGeometryModeProperties,
    DragExMaterialProperties,
    DragExMaterialPanel,
    DragExBackendDemoOperator,
)


def register():
    print("Hi from", __package__)

    # TODO trying to not import at the module level, see if this is less jank this way
    # TODO catch ImportError
    import dragex_backend

    print(dir(dragex_backend))

    print(f"{BUILD_ID=}")
    print(f"{dragex_backend.get_build_id()=}")

    assert dragex_backend.get_build_id() == BUILD_ID

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Material.dragex = bpy.props.PointerProperty(type=DragExMaterialProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Bye from", __package__)
