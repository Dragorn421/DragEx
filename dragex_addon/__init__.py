import bpy

# TODO catch ImportError
import dragex_backend


class DragExBackendDemoOperator(bpy.types.Operator):
    bl_idname = "dragex.dragex_backend_demo"
    bl_label = "DragEx backend demo"

    def execute(self, context):
        print("Hello World")
        mesh = context.object.data
        assert isinstance(mesh, bpy.types.Mesh)
        buf = dragex_backend.FloatBufferThing(3 * len(mesh.vertices))
        mesh.vertices.foreach_get("co", buf)
        print(memoryview(buf)[0])
        print(memoryview(buf)[1])
        print(memoryview(buf)[2])
        return {"FINISHED"}


classes = (DragExBackendDemoOperator,)


def register():
    print("Hi from", __package__)

    print(dir(dragex_backend))

    try:
        print(dragex_backend.get_value())
    except:
        import traceback

        traceback.print_exc()

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
