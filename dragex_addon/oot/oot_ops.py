from pathlib import Path

import bpy
import mathutils

from . import oot_export_map
from . import oot_skelanime
from . import oot_util
from .. import util


class DragExOoTExportSceneOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_export_scene"
    bl_label = "DragEx OoT Export Scene"

    def scene_coll_name_search(self, context: bpy.types.Context, edit_text: str):
        edit_text = edit_text.lower()
        scene = context.scene
        assert scene is not None
        for coll in scene.collection.children_recursive:
            coll_dragex = util.DRAGEX(coll)
            if coll_dragex.oot.type == "SCENE":
                if edit_text in coll.name.lower():
                    yield coll.name

    scene_coll_name: bpy.props.StringProperty(
        name="Scene",
        description="OoT scene collection to export",
        search=scene_coll_name_search,  # type: ignore
        search_options=set(),
    )

    directory: bpy.props.StringProperty(subtype="DIR_PATH", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def execute(self, context):  # type: ignore
        import time

        start = time.time()

        if self.scene_coll_name == "":
            self.report({"ERROR_INVALID_INPUT"}, "No scene given")
            return {"CANCELLED"}
        coll_scene_to_export = bpy.data.collections[self.scene_coll_name]
        export_directory = Path(self.directory)

        scene = context.scene
        assert scene is not None

        try:
            # TODO pass in the decomp repo path as a prop or something instead
            decomp_repo_p = oot_util.find_decomp_repo(export_directory)
        except oot_util.CannotFindDecompRepoError:
            self.report(
                {"ERROR"},
                (
                    "Cannot find decomp repo (a folder with spec)"
                    f" in parents of {export_directory}"
                ),
            )
            return {"CANCELLED"}

        oot_export_map.export_coll_scene(
            coll_scene_to_export,
            export_directory,
            scene,
            decomp_repo_p,
        )

        end = time.time()
        print("export time:", end - start, "s")

        return {"FINISHED"}

    def invoke(self, context, event):  # type: ignore
        assert context.window_manager is not None
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class DragExOoTExportSkeletonOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_export_skeleton"
    bl_label = "DragEx OoT Export Skeleton"

    directory: bpy.props.StringProperty(subtype="DIR_PATH", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return (
            scene_dragex.target == "OOT_F3DEX2_PL"
            and context.active_object is not None
            and context.active_object.type == "ARMATURE"
        )

    def execute(self, context):  # type: ignore
        import time

        start = time.time()

        scene = context.scene
        assert scene is not None

        armature_object = context.active_object
        assert armature_object is not None
        armature_data = armature_object.data
        assert isinstance(armature_data, bpy.types.Armature)

        export_directory = Path(self.directory)

        try:
            # TODO pass in the decomp repo path as a prop or something instead
            decomp_repo_p = oot_util.find_decomp_repo(export_directory)
        except oot_util.CannotFindDecompRepoError:
            self.report(
                {"ERROR"},
                (
                    "Cannot find decomp repo (a folder with spec)"
                    f" in parents of {export_directory}"
                ),
            )
            return {"CANCELLED"}

        oot_skelanime.export_skeleton(
            armature_object,
            armature_data,
            scene,
            export_directory,
            decomp_repo_p,
        )

        end = time.time()
        print("export time:", end - start, "s")

        return {"FINISHED"}

    def invoke(self, context, event):  # type: ignore
        assert context.window_manager is not None
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def find_armature_parent(obj: bpy.types.Object):
    while obj.parent is not None:
        obj = obj.parent
        if obj.type == "ARMATURE":
            return obj
    return None


class DragExOoTFindNotSingleBindVerticesOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_find_not_single_bind_vertices"
    bl_label = "DragEx OoT Find not-single-bind Vertices"

    select: bpy.props.EnumProperty(
        items=(
            ("UNASSIGNED", "Unassigned", ""),
            ("MULTIASSIGNED", "Multiassigned", ""),
        )
    )

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return (
            scene_dragex.target == "OOT_F3DEX2_PL"
            and context.active_object is not None
            and context.active_object.type == "MESH"
            and find_armature_parent(context.active_object) is not None
        )

    def execute(self, context):  # type: ignore
        mesh_obj = context.active_object
        assert mesh_obj is not None
        mesh = mesh_obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        armature_obj = find_armature_parent(mesh_obj)
        assert armature_obj is not None
        armature = armature_obj.data
        assert isinstance(armature, bpy.types.Armature)
        bones_group_indices = {
            mesh_obj.vertex_groups[bone.name].index
            for bone in armature.bones
            if bone.name in mesh_obj.vertex_groups
        }
        n = 0
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        for v in mesh.vertices:
            v_groups = sorted(
                (_g for _g in v.groups if _g.group in bones_group_indices),
                key=lambda _g: _g.weight,
                reverse=True,
            )
            is_unassigned = (
                len(v_groups) == 0
                or v_groups[0].weight < 1 - oot_skelanime.WEIGHT_EPSILON
            )
            is_multiassigned = (
                len(v_groups) >= 2 and v_groups[1].weight > oot_skelanime.WEIGHT_EPSILON
            )
            if self.select == "UNASSIGNED":
                v.select = is_unassigned
                if is_unassigned:
                    n += 1
            if self.select == "MULTIASSIGNED":
                v.select = is_multiassigned
                if is_multiassigned:
                    n += 1
        bpy.ops.object.mode_set(mode="EDIT")
        self.report({"INFO"}, f"Found {n} {self.select.lower()} vertices")
        return {"FINISHED"}


class DragExOoTExportAnimationOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_export_animation"
    bl_label = "DragEx OoT Export Animation"

    directory: bpy.props.StringProperty(subtype="DIR_PATH", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None:
            return False
        scene_dragex = util.DRAGEX(scene)
        return (
            scene_dragex.target == "OOT_F3DEX2_PL"
            and context.active_object is not None
            and context.active_object.type == "ARMATURE"
            and context.active_object.animation_data is not None
            and context.active_object.animation_data.action is not None
        )

    def execute(self, context):  # type: ignore
        import time

        start = time.time()

        scene = context.scene
        assert scene is not None

        armature_object = context.active_object
        assert armature_object is not None
        armature_data = armature_object.data
        assert isinstance(armature_data, bpy.types.Armature)

        export_directory = Path(self.directory)

        assert armature_object.animation_data is not None
        action = armature_object.animation_data.action
        assert action is not None

        oot_skelanime.export_anim(
            armature_object,
            armature_data,
            scene,
            export_directory,
            action,
        )

        end = time.time()
        print("export time:", end - start, "s")

        return {"FINISHED"}

    def invoke(self, context, event):  # type: ignore
        assert context.window_manager is not None
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class DragExOoTNewSceneOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_new_scene"
    bl_label = "New OoT Scene"
    bl_options = {"REGISTER", "UNDO"}

    map_name: bpy.props.StringProperty(
        name="Map Name",
        description="Map name to name the added items from",
        default="My map",
    )
    n_rooms: bpy.props.IntProperty(
        name="Rooms",
        description="Amount of rooms in the map",
        min=1,
        default=1,
    )

    def execute(self, context):  # type: ignore
        map_name: str = self.map_name
        scene_name = f"{map_name} Scene"
        room_names = [f"Room {_i}" for _i in range(self.n_rooms)]

        def are_names_taken(scene_name: str, room_names: list[str]):
            return scene_name in bpy.data.collections or any(
                _room_name in bpy.data.collections for _room_name in room_names
            )

        if are_names_taken(scene_name, room_names):
            cont = True
            i = 0
            while cont:
                scene_name = f"{map_name} Scene"
                room_names = [f"{map_name} Room {_i}" for _i in range(self.n_rooms)]
                cont = are_names_taken(scene_name, room_names)
                if cont:
                    i += 1
                    map_name = self.map_name + f".{i:03}"

        scene = context.scene
        assert scene is not None
        scene_dragex = util.DRAGEX(scene)

        scene_coll = bpy.data.collections.new(scene_name)
        scene_coll_dragex = util.DRAGEX(scene_coll)
        scene_coll_dragex.oot.type = "SCENE"

        scale = scene_dragex.oot.scale
        room_colls = list[bpy.types.Collection]()
        for room_number, room_name in enumerate(room_names):
            room_coll = bpy.data.collections.new(room_name)
            room_colls.append(room_coll)
            room_coll_dragex = util.DRAGEX(room_coll)
            room_coll_dragex.oot.type = "ROOM"
            room_coll_dragex.oot.room.number = room_number
            scene_coll.children.link(room_coll)
            room_mesh = bpy.data.meshes.new(f"{room_name} Mesh")
            x = (room_number * 1000 - 400) * scale
            y = -400 * scale
            w = 800 * scale
            h = 800 * scale
            room_mesh.from_pydata(
                (
                    (x, y, 0),
                    (x + w, y, 0),
                    (x + w, y + h, 0),
                    (x, y + h, 0),
                ),
                (),
                ((0, 1, 2, 3),),
            )
            room_mesh_obj = bpy.data.objects.new(f"{room_name} Mesh", room_mesh)
            room_coll.objects.link(room_mesh_obj)

        spawn_empty_obj = bpy.data.objects.new(f"{map_name} Spawn", None)
        spawn_empty_obj_dragex = util.DRAGEX(spawn_empty_obj)
        spawn_empty_obj.location = (0, 0, 0)
        spawn_empty_obj.empty_display_type = "ARROWS"
        spawn_empty_obj_dragex.oot.empty.export_pos = True
        spawn_empty_obj_dragex.oot.empty.export_pos_name = (
            f"POS_{util.make_c_identifier(scene_name).upper()}_SPAWN"
        )
        spawn_empty_obj_dragex.oot.empty.export_yaw = True
        spawn_empty_obj_dragex.oot.empty.export_yaw_name = (
            f"YAW_{util.make_c_identifier(scene_name).upper()}_SPAWN"
        )
        scene_coll.objects.link(spawn_empty_obj)

        scene.collection.children.link(scene_coll)
        return {"FINISHED"}
