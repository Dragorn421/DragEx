import numpy as np

import bpy

from .build_id import BUILD_ID


def new_uint_buf(len):
    return np.empty(
        shape=len,
        dtype=np.uint32,  # np.uint leads to L format (unsigned long)
        order="C",
    )


class DragExBackendDemoOperator(bpy.types.Operator):
    bl_idname = "dragex.dragex_backend_demo"
    bl_label = "DragEx backend demo"

    def execute(self, context):

        # TODO trying to not import at the module level, see if this is less jank this way
        # TODO catch ImportError
        import dragex_backend

        print("Hello World")
        mesh = context.object.data
        assert isinstance(mesh, bpy.types.Mesh)
        # note: if size is too small, error is undescriptive:
        # "RuntimeError: internal error setting the array"
        buf_vertices_co = dragex_backend.FloatBufferThing(3 * len(mesh.vertices))
        mesh.vertices.foreach_get("co", memoryview(buf_vertices_co))
        print(memoryview(buf_vertices_co)[0])
        print(memoryview(buf_vertices_co)[1])
        print(memoryview(buf_vertices_co)[2])
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
        buf_loops_normal = dragex_backend.FloatBufferThing(3 * len(mesh.loops))
        mesh.loops.foreach_get("vertex_index", buf_loops_vertex_index)
        mesh.loops.foreach_get("normal", memoryview(buf_loops_normal))
        mesh_info = dragex_backend.create_MeshInfo(
            buf_vertices_co,
            buf_triangles_loops,
            # buf_triangles_material_index,
            buf_loops_vertex_index,
            buf_loops_normal,
        )
        mesh_info.write_c("/home/dragorn421/Documents/dragex/dragex_attempt2/output.c")
        return {"FINISHED"}


classes = (DragExBackendDemoOperator,)


def register():
    print("Hi from", __package__)

    # TODO trying to not import at the module level, see if this is less jank this way
    # TODO catch ImportError
    import dragex_backend

    print(dir(dragex_backend))

    print(BUILD_ID)
    try:
        print(dragex_backend.get_build_id())
    except:
        import traceback

        traceback.print_exc()

    assert dragex_backend.get_build_id() == BUILD_ID

    try:
        print(bytes(dragex_backend.FloatBufferThing(1)))
    except:
        import traceback

        traceback.print_exc()

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Bye from", __package__)
