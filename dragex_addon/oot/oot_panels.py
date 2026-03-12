import bpy

from .. import util
from . import oot_ops


class DragExMaterialOoTCollisionPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_dragex_oot_collision"
    bl_label = "DragEx OoT Collision"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        scene_dragex = util.DRAGEX(context.scene)
        return scene_dragex.target == "OOT_F3DEX2_PL" and context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex = util.DRAGEX(mat)
        self.layout.prop(mat_dragex.oot, "polytype_name")


class DragExOoTPanel(bpy.types.Panel):
    bl_idname = "DRAGEX_PT_oot"
    bl_label = "OoT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DragEx"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        assert self.layout is not None
        scene = context.scene
        assert scene is not None
        scene_dragex = util.DRAGEX(scene)
        self.layout.prop(scene_dragex.oot, "scale")
        self.layout.operator(oot_ops.DragExOoTNewSceneOperator.bl_idname)
        self.layout.operator(oot_ops.DragExOoTExportSceneOperator.bl_idname)
        self.layout.operator(oot_ops.DragExOoTExportSkeletonOperator.bl_idname)
        self.layout.operator(
            oot_ops.DragExOoTFindNotSingleBindVerticesOperator.bl_idname,
            text="Find unassigned vertices",
        ).select = "UNASSIGNED"
        self.layout.operator(
            oot_ops.DragExOoTFindNotSingleBindVerticesOperator.bl_idname,
            text="Find multi-assigned vertices",
        ).select = "MULTIASSIGNED"
        self.layout.operator(oot_ops.DragExOoTExportAnimationOperator.bl_idname)


class DragExCollectionOoTPanel(bpy.types.Panel):
    bl_idname = "COLLECTION_PT_dragex_oot"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "collection"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        coll = context.collection
        assert coll is not None
        coll_dragex = util.DRAGEX(coll)
        layout.prop(coll_dragex.oot, "type")
        if coll_dragex.oot.type == "ROOM":
            layout.prop(coll_dragex.oot.room, "number")


class DragExObjectOoTEmptyPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_dragex_oot_empty"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        obj = context.object
        if scene is None or obj is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return scene_dragex.target == "OOT_F3DEX2_PL" and obj.type == "EMPTY"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        obj = context.object
        assert obj is not None
        obj_dragex = util.DRAGEX(obj)
        layout.prop(obj_dragex.oot.empty, "type")

        layout.prop(obj_dragex.oot.empty, "export_pos")
        if obj_dragex.oot.empty.export_pos:
            layout.prop(obj_dragex.oot.empty, "export_pos_name")

        layout.prop(obj_dragex.oot.empty, "export_rot_yxz")
        if obj_dragex.oot.empty.export_rot_yxz:
            layout.prop(obj_dragex.oot.empty, "export_rot_yxz_name")

        layout.prop(obj_dragex.oot.empty, "export_yaw")
        if obj_dragex.oot.empty.export_yaw:
            layout.prop(obj_dragex.oot.empty, "export_yaw_name")

        if (
            obj_dragex.oot.empty.export_pos
            or obj_dragex.oot.empty.export_rot_yxz_name
            or obj_dragex.oot.empty.export_yaw_name
        ):
            is_part_of_a_scene = False
            for coll in bpy.data.collections.values():
                assert coll is not None
                coll_dragex = util.DRAGEX(coll)
                if coll_dragex.oot.type == "SCENE" and obj in coll.all_objects.values():
                    is_part_of_a_scene = True
            if not is_part_of_a_scene:
                layout.label(
                    text=(
                        "This empty is not part of any scene,"
                        " so it will be ignored on export"
                    ),
                    icon="ERROR",
                )


class DragExMeshOoTPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_dragex_oot_mesh"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        obj = context.object
        if scene is None or obj is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return scene_dragex.target == "OOT_F3DEX2_PL" and obj.type == "MESH"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        obj = context.object
        assert obj is not None
        assert isinstance(obj.data, bpy.types.Mesh)
        mesh_dragex = util.DRAGEX(obj.data)
        layout.prop(mesh_dragex.oot, "draw_layer")
