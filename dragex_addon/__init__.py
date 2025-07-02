import bpy

from .build_id import BUILD_ID


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
        buf = dragex_backend.FloatBufferThing(3 * len(mesh.vertices))
        mesh.vertices.foreach_get("co", memoryview(buf))
        print(memoryview(buf)[0])
        print(memoryview(buf)[1])
        print(memoryview(buf)[2])
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
