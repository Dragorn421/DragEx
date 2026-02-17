from pathlib import Path
from typing import TYPE_CHECKING

import bpy
import mathutils

from . import oot_export_map
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
        scene_dragex = util.DRAGEX(scene)

        # TODO pass in the decomp repo path as a prop or something instead
        candidate_decomp_repo_p = export_directory.parent
        while not (candidate_decomp_repo_p / "spec").exists():
            parent_p = candidate_decomp_repo_p.parent
            if parent_p == candidate_decomp_repo_p:
                self.report(
                    {"ERROR"},
                    (
                        "Cannot find decomp repo (a folder with spec)"
                        f" in parents of {export_directory}"
                    ),
                )
                return {"CANCELLED"}
            candidate_decomp_repo_p = parent_p
        decomp_repo_p = candidate_decomp_repo_p

        oot_export_map.export_coll_scene(
            coll_scene_to_export,
            export_directory,
            oot_export_map.ExportOptions(
                transform=(
                    util.transform_zup_to_yup
                    @ mathutils.Matrix.Scale(1 / scene_dragex.oot.scale, 3)
                ),
                decomp_repo_p=decomp_repo_p,
            ),
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
        scene_coll.objects.link(spawn_empty_obj)

        scene.collection.children.link(scene_coll)
        return {"FINISHED"}
