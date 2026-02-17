import abc
from collections.abc import Sequence
import dataclasses
import math
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import numpy as np

import bpy
import mathutils

from . import meshstuff
from . import util

if TYPE_CHECKING:
    from ..dragex_backend import dragex_backend
else:
    try:
        import dragex_backend
    except ModuleNotFoundError:
        dragex_backend = None


def mesh_to_OoTCollisionMesh(
    obj: bpy.types.Object,
    mesh: bpy.types.Mesh,
    transform: mathutils.Matrix,
):
    # TODO test more with different matrix_world
    transform = transform.to_4x4() @ obj.matrix_world
    print(f"{transform=}")
    if transform[3] != mathutils.Vector((0, 0, 0, 1)):
        raise Exception("Unexpected transform", transform)
    transform3 = transform.to_3x3()
    transform3_np = np.array(transform3)
    transform_translation = transform.translation
    transform_translation_np = np.array(transform_translation)

    buf_vertices_co = util.new_float_buf(3 * len(mesh.vertices))
    mesh.vertices.foreach_get("co", buf_vertices_co)
    mesh.calc_loop_triangles()
    buf_triangles_loops = util.new_uint_buf(3 * len(mesh.loop_triangles))
    buf_triangles_material_index = util.new_uint_buf(len(mesh.loop_triangles))
    mesh.loop_triangles.foreach_get("loops", buf_triangles_loops)
    mesh.loop_triangles.foreach_get("material_index", buf_triangles_material_index)
    buf_loops_vertex_index = util.new_uint_buf(len(mesh.loops))
    mesh.loops.foreach_get("vertex_index", buf_loops_vertex_index)

    buf_vertices_co_Nx3 = buf_vertices_co.reshape((len(mesh.vertices), 3))
    np.matmul(transform3_np, buf_vertices_co_Nx3.T, out=buf_vertices_co_Nx3.T)
    buf_vertices_co_Nx3 += transform_translation_np

    materials = list[dragex_backend.OoTCollisionMaterial | None]()
    for mat_index in range(len(obj.material_slots)):
        mat = obj.material_slots[mat_index].material
        if mat is None:
            colmat = None
        else:
            mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
            polytype_name = mat_dragex.polytype_name
            if polytype_name:
                colmat = dragex_backend.OoTCollisionMaterial(name=polytype_name)
            else:
                colmat = None
        materials.append(colmat)

    default_material = dragex_backend.OoTCollisionMaterial(name="DEFAULT")

    collision_mesh = dragex_backend.create_OoTCollisionMesh(
        buf_vertices_co,
        buf_triangles_loops,
        buf_triangles_material_index,
        buf_loops_vertex_index,
        materials,
        default_material,
    )

    return collision_mesh


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
        scene_dragex: DragExSceneProperties = context.scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL" and context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
        self.layout.prop(mat_dragex, "polytype_name")


@dataclasses.dataclass(eq=False)
class OoTRoomShape(abc.ABC):
    image_infos: meshstuff.ImageInfos


@dataclasses.dataclass(eq=False)  # Use id-based equality and hashing
class OoTRoom:
    c_identifier: str
    shape: OoTRoomShape


@dataclasses.dataclass(eq=False)
class OoTRoomShapeNormal(OoTRoomShape):
    entries_opa: Sequence["dragex_backend.MeshInfo"]
    entries_xlu: Sequence["dragex_backend.MeshInfo"]


@dataclasses.dataclass(eq=False)
class OoTScene:
    c_identifier: str
    rooms: list[OoTRoom]
    collision: "dragex_backend.OoTCollisionMesh"
    positions: dict[str, tuple[int, int, int]]
    rotations_yxz: dict[str, mathutils.Euler]
    yaws: dict[str, float]  # radians


class CollectMapException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def collect_map(coll_scene: bpy.types.Collection, export_options: "ExportOptions"):
    scene_c_identifier = util.make_c_identifier(coll_scene.name)

    transform_inverted = export_options.transform.inverted()

    room_colls = dict[int, bpy.types.Collection]()
    for coll in coll_scene.children_recursive:
        coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
        if coll_dragex.oot.type == "ROOM":
            room_number = coll_dragex.oot.room.number
            if room_number in room_colls:
                raise CollectMapException(
                    f"Duplicate room number {room_number}: used by "
                    f"{room_colls[room_number].name} and {coll.name}"
                )
            room_colls[room_number] = coll

    n_rooms = max(room_colls.keys()) + 1
    expected_room_numbers = set(range(n_rooms))
    assert expected_room_numbers.issuperset(room_colls.keys())
    if room_colls.keys() != expected_room_numbers:
        raise CollectMapException(
            "The following room numbers are missing: "
            + ", ".join(map(str, sorted(expected_room_numbers - room_colls.keys())))
        )

    rooms = list[OoTRoom]()

    for i in range(n_rooms):
        room_coll = room_colls[i]
        room_c_identifier = util.make_c_identifier(room_coll.name)
        room_coll_dragex: DragExCollectionProperties = room_coll.dragex  # type: ignore
        entries_opa = list[dragex_backend.MeshInfo]()
        entries_xlu = list[dragex_backend.MeshInfo]()
        image_infos = meshstuff.ImageInfos()
        for obj in room_coll.all_objects:
            if obj.type == "EMPTY":
                obj_dragex: DragExObjectProperties = obj.dragex  # type: ignore
                ...
            if obj.type == "MESH":
                assert isinstance(obj.data, bpy.types.Mesh)
                # TODO this is inefficient if mesh is shared between rooms
                mesh_info = meshstuff.mesh_to_mesh_info(
                    obj,
                    obj.data,
                    export_options.transform,
                    image_infos,
                    f"{scene_c_identifier}_{room_c_identifier}_",
                )
                # TODO prop to set draw layer opa/xlu
                entries_opa.append(mesh_info)

        shape = OoTRoomShapeNormal(
            image_infos=image_infos,
            entries_opa=entries_opa,
            entries_xlu=entries_xlu,
        )

        room = OoTRoom(
            c_identifier=room_c_identifier,
            shape=shape,
        )
        rooms.append(room)

    collision_meshes = list[dragex_backend.OoTCollisionMesh]()
    for obj in coll_scene.all_objects:
        if obj.type == "MESH":
            assert isinstance(obj.data, bpy.types.Mesh)
            collision_mesh = mesh_to_OoTCollisionMesh(
                obj,
                obj.data,
                export_options.transform,
            )
            collision_meshes.append(collision_mesh)
    collision = dragex_backend.join_OoTCollisionMeshes(collision_meshes)

    positions = dict[str, tuple[int, int, int]]()
    rotations_yxz = dict[str, mathutils.Euler]()
    yaws = dict[str, float]()
    for obj in coll_scene.all_objects:
        if obj.type == "EMPTY":
            obj_dragex: DragExObjectProperties = obj.dragex  # type: ignore

            if obj_dragex.oot.empty.export_pos:
                pos = export_options.transform @ obj.location
                positions[obj_dragex.oot.empty.export_pos_name] = (
                    round(pos.x),
                    round(pos.y),
                    round(pos.z),
                )

            saved_rotation_mode = obj.rotation_mode
            try:
                obj.rotation_mode = "QUATERNION"
                obj_rot_quaternion = obj.rotation_quaternion.copy()
            finally:
                obj.rotation_mode = saved_rotation_mode

            # TODO check this is correct
            # 1) check transform @ rot @ 1/transform is correct
            # 2) check Euler ZXY does correspond to oot's YXZ
            obj_transformed_rot_matrix = (
                export_options.transform
                @ obj_rot_quaternion.to_matrix()
                @ transform_inverted
            )

            if obj_dragex.oot.empty.export_rot_yxz:
                rotations_yxz[obj_dragex.oot.empty.export_rot_yxz_name] = (
                    obj_transformed_rot_matrix.to_euler("ZXY")
                )

            if obj_dragex.oot.empty.export_yaw:
                yaws[obj_dragex.oot.empty.export_yaw_name] = (
                    obj_transformed_rot_matrix.to_euler("ZXY").y
                )

    oot_scene = OoTScene(
        c_identifier=scene_c_identifier,
        rooms=rooms,
        collision=collision,
        positions=positions,
        rotations_yxz=rotations_yxz,
        yaws=yaws,
    )
    return oot_scene


@dataclasses.dataclass
class ExportOptions:
    transform: mathutils.Matrix
    decomp_repo_p: Path


def export_coll_scene(
    coll_scene: bpy.types.Collection, out_dir_p: Path, export_options: ExportOptions
):
    oot_scene = collect_map(coll_scene, export_options)

    from pprint import pprint

    pprint(oot_scene)

    map_prefix_lower = oot_scene.c_identifier.lower()
    map_prefix_upper = oot_scene.c_identifier.upper()

    exported_dir_p = out_dir_p / "exported"
    exported_dir_p.mkdir(exist_ok=True)

    with util.FDManager() as fd_manager:
        collision_inc_c_fd = fd_manager.open_w(exported_dir_p / f"collision.inc.c")

        col_header_name = f"{map_prefix_lower}_Col"

        col_vtx_list_name = f"{map_prefix_lower}_VtxList"
        col_poly_list_name = f"{map_prefix_lower}_PolyList"
        col_surface_types_name = f"{map_prefix_lower}_SurfaceTypes"
        col_bg_cam_list_name = f"{map_prefix_lower}_BgCamList"

        with open(collision_inc_c_fd, "w", closefd=False) as f:
            f.write(
                """\
#include "collision.h"

#include "stddef.h"
#include "array_count.h"
#include "bgcheck.h"
#include "z_math.h"

"""
            )

        collision_bounds = oot_scene.collision.write_c(
            collision_inc_c_fd,
            map_prefix_upper,
            col_vtx_list_name,
            col_poly_list_name,
            col_surface_types_name,
        )

        with open(collision_inc_c_fd, "w", closefd=False) as f:
            collision_bounds_min = collision_bounds.min
            collision_bounds_max = collision_bounds.max
            f.write(
                f"CollisionHeader {col_header_name} = "
                "{\n"
                "    {"
                f" {collision_bounds_min[0]},"
                f" {collision_bounds_min[1]},"
                f" {collision_bounds_min[2]} "
                "},\n"
                "    {"
                f" {collision_bounds_max[0]},"
                f" {collision_bounds_max[1]},"
                f" {collision_bounds_max[2]} "
                "},\n"
                f"    ARRAY_COUNT({col_vtx_list_name}),\n"
                f"    {col_vtx_list_name},\n"
                f"    ARRAY_COUNT({col_poly_list_name}),\n"
                f"    {col_poly_list_name},\n"
                f"    {col_surface_types_name},\n"
                f"    {col_bg_cam_list_name},\n"
                f"    0,\n"  # TODO waterboxes
                f"    NULL,\n"
                "};\n"
                "\n"
            )

        (exported_dir_p / "collision.h").write_text(
            f"""\
#include "bgcheck.h"

extern CollisionHeader {col_header_name};
"""
        )

    for i, room in enumerate(oot_scene.rooms):
        with util.FDManager() as fd_manager:
            room_fd = fd_manager.open_w(exported_dir_p / f"room_{i}_shape.inc.c")

            room_shape = room.shape

            room_shape_name = f"{map_prefix_lower}_room_{i}_RoomShape"

            if isinstance(room.shape, OoTRoomShapeNormal):
                (exported_dir_p / f"room_{i}_shape.h").write_text(
                    f"""\
#include "room.h"

extern RoomShapeNormal {room_shape_name};
"""
                )
            else:
                raise NotImplementedError(type(room.shape))

            with open(room_fd, "w", closefd=False) as f:
                f.write(
                    f"""\
#include "room_{i}_shape.h"

#include "ultra64.h"
#include "array_count.h"
#include "room.h"

"""
                )

                for (
                    c_identifier,
                    image_key,
                ) in room_shape.image_infos.key_by_c_identifier.items():
                    image_file_stem = (
                        f"{c_identifier}.{image_key.format.lower()}{image_key.size}"
                    )
                    # TODO save() may set the image's filepath as a side-effect?
                    # (not in 4.2.11 at least, but recent versions (which?) have a save_copy argument to save())
                    # if so, need to copy() the datablock before save to avoid modifying it
                    image_key.image.save(
                        filepath=str(exported_dir_p / f"{image_file_stem}.png"),
                    )
                    image_inc_c_p = (
                        PurePosixPath(
                            *exported_dir_p.relative_to(
                                export_options.decomp_repo_p
                            ).parts
                        )
                        / f"{image_file_stem}.inc.c"
                    )
                    f.write(
                        f"u64 {c_identifier}[] = "
                        "{\n"
                        f'#include "{image_inc_c_p}"\n'
                        "};\n"
                        "\n"
                    )

            if isinstance(room_shape, OoTRoomShapeNormal):
                opa_dlists_names = list[str]()
                xlu_dlists_names = list[str]()
                for mi in room_shape.entries_opa:
                    # TODO batch the fopen() inside write_c by passing a list of MeshInfo to dragex_backend instead
                    dl_name = mi.write_c(room_fd)
                    opa_dlists_names.append(dl_name)
                for mi in room_shape.entries_xlu:
                    dl_name = mi.write_c(room_fd)
                    xlu_dlists_names.append(dl_name)

                if len(opa_dlists_names) < len(xlu_dlists_names):
                    opa_dlists_names += ["NULL"] * (
                        len(xlu_dlists_names) - len(opa_dlists_names)
                    )
                else:
                    xlu_dlists_names += ["NULL"] * (
                        len(opa_dlists_names) - len(xlu_dlists_names)
                    )

                with open(room_fd, "w", closefd=False) as f:
                    dlists_entries_name = (
                        f"{map_prefix_lower}_{room.c_identifier}_DListsEntries"
                    )
                    f.write(f"RoomShapeDListsEntry {dlists_entries_name}[] = " "{\n")
                    for opa_dl_name, xlu_dl_name in zip(
                        opa_dlists_names, xlu_dlists_names
                    ):
                        f.write(
                            "    {\n"
                            f"        {opa_dl_name},\n"
                            f"        {xlu_dl_name},\n"
                            "    },\n"
                        )
                    f.write("};\n" "\n")

                    f.write(
                        f"RoomShapeNormal {room_shape_name} = "
                        "{\n"
                        "    { ROOM_SHAPE_TYPE_NORMAL },\n"
                        f"    ARRAY_COUNT({dlists_entries_name}),\n"
                        f"    {dlists_entries_name},\n"
                        f"    {dlists_entries_name} + ARRAY_COUNT({dlists_entries_name}),\n"
                        "};\n"
                        "\n"
                    )
            else:
                raise NotImplementedError(type(room_shape))

    with (exported_dir_p / "positions.h").open("w") as f:
        f.write(
            f"#ifndef {map_prefix_upper}_POSITIONS_H\n"
            f"#define {map_prefix_upper}_POSITIONS_H\n"
            "\n"
        )
        for name, (x, y, z) in oot_scene.positions.items():
            f.write(f"#define {name} {x}, {y}, {z}\n")
        f.write("\n")
        for name, rot in oot_scene.rotations_yxz.items():
            f.write(f"#define {name} ")
            f.write(", ".join(f"DEG_TO_BINANG({math.degrees(_v)})" for _v in rot))
            f.write("\n")
        f.write("\n")
        for name, yaw in oot_scene.yaws.items():
            f.write(f"#define {name} DEG_TO_BINANG({math.degrees(yaw)})\n")
        f.write("\n")
        f.write("\n" "#endif\n")

    replacements = {
        "map_prefix_lower": map_prefix_lower,
        "MAP_PREFIX_UPPER": map_prefix_upper,
    }

    def apply_replacements(text: str):
        for repl_from, repl_to in replacements.items():
            text = text.replace(repl_from, repl_to)
        return text

    map_template_dir_p = Path(__file__).parent / "map_template"

    (out_dir_p / "glue").mkdir(exist_ok=True)

    def write_if_missing(p: Path, text: str):
        if not p.exists():
            p.write_text(text)

    for p in (
        Path("glue/glue_scene.c"),
        Path("glue/glue_scene.h"),
        Path("header_scene.inc.c"),
        Path("table_cameras.h"),
        Path("table_envlightsettings.h"),
        Path("table_polytypes.h"),
        Path("table_spawns.h"),
    ):
        write_if_missing(
            out_dir_p / p,
            apply_replacements((map_template_dir_p / p).read_text()),
        )

    spec_frags = []
    spec_frags.append(
        apply_replacements((map_template_dir_p / "frag_spec_scene.inc").read_text())
    )

    frag_table_rooms_h_template = (
        map_template_dir_p / "frag_table_rooms.h"
    ).read_text()
    glue_room_c_template = (map_template_dir_p / "glue/glue_room_0.c").read_text()
    glue_room_h_template = (map_template_dir_p / "glue/glue_room_0.h").read_text()
    header_room_inc_c_template = (
        map_template_dir_p / "header_room_0.inc.c"
    ).read_text()
    table_actors_room_h_template = (
        map_template_dir_p / "table_actors_room_0.h"
    ).read_text()
    table_objects_room_h_template = (
        map_template_dir_p / "table_objects_room_0.h"
    ).read_text()
    frag_spec_room_inc_template = (
        map_template_dir_p / "frag_spec_room.inc"
    ).read_text()

    table_rooms_frags = []
    for i, room in enumerate(oot_scene.rooms):
        replacements_room = replacements.copy()
        replacements_room.update(
            {
                "ROOM_NAME": room.c_identifier.upper(),
                "ROOM_NUMBER": f"{i}",
            }
        )

        def apply_replacements_room(text: str):
            for repl_from, repl_to in replacements_room.items():
                text = text.replace(repl_from, repl_to)
            return text

        table_rooms_frags.append(apply_replacements_room(frag_table_rooms_h_template))

        write_if_missing(
            out_dir_p / f"glue/glue_room_{i}.c",
            apply_replacements_room(glue_room_c_template),
        )
        write_if_missing(
            out_dir_p / f"glue/glue_room_{i}.h",
            apply_replacements_room(glue_room_h_template),
        )
        write_if_missing(
            out_dir_p / f"header_room_{i}.inc.c",
            apply_replacements_room(header_room_inc_c_template),
        )
        write_if_missing(
            out_dir_p / f"table_actors_room_{i}.h",
            apply_replacements_room(table_actors_room_h_template),
        )
        write_if_missing(
            out_dir_p / f"table_objects_room_{i}.h",
            apply_replacements_room(table_objects_room_h_template),
        )

        spec_frags.append(apply_replacements_room(frag_spec_room_inc_template))

    write_if_missing(
        out_dir_p / "table_rooms.h",
        "".join(table_rooms_frags),
    )

    write_if_missing(
        out_dir_p / "spec.inc",
        "\n".join(spec_frags),
    )


class DragExOoTExportSceneOperator(bpy.types.Operator):
    bl_idname = "dragex.oot_export_scene"
    bl_label = "DragEx OoT Export Scene"

    def scene_coll_name_search(self, context: bpy.types.Context, edit_text: str):
        edit_text = edit_text.lower()
        scene = context.scene
        assert scene is not None
        for coll in scene.collection.children_recursive:
            coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore

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

        export_coll_scene(
            coll_scene_to_export,
            export_directory,
            ExportOptions(
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


class DragExCollectionOoTSceneProperties(bpy.types.PropertyGroup):
    pass


class DragExCollectionOoTRoomProperties(bpy.types.PropertyGroup):
    number: bpy.props.IntProperty(
        name="Room Number",
        description="Number/ID for this room",
        min=0,
    )


class DragExCollectionOoTProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description="OoT collection type",
        items=(
            ("NONE", "None", "No type. A regular collection"),
            ("SCENE", "Scene", "Collection represents an OoT scene"),
            ("ROOM", "Room", "Collection represents an OoT room"),
        ),
        default="NONE",
    )

    scene_: bpy.props.PointerProperty(type=DragExCollectionOoTSceneProperties)
    room_: bpy.props.PointerProperty(type=DragExCollectionOoTRoomProperties)

    @property
    def scene(self) -> DragExCollectionOoTSceneProperties:
        return self.scene_

    @property
    def room(self) -> DragExCollectionOoTRoomProperties:
        return self.room_


class DragExSceneOoTProperties(bpy.types.PropertyGroup):
    scale: bpy.props.FloatProperty(
        name="Scale",
        description=(
            "OoT to Blender scaling factor. "
            "For example the default value of 0.01 means 1 Blender centimeter "
            "corresponds to 1 OoT unit"
        ),
        default=0.01,
    )


def validate_export_pos_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = util.make_c_identifier(self.export_pos_name)
    if self.export_pos_name != c_identifier:
        self.export_pos_name = c_identifier


def validate_export_rot_yxz_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = util.make_c_identifier(self.export_rot_yxz_name)
    if self.export_rot_yxz_name != c_identifier:
        self.export_rot_yxz_name = c_identifier


def validate_export_yaw_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = util.make_c_identifier(self.export_yaw_name)
    if self.export_yaw_name != c_identifier:
        self.export_yaw_name = c_identifier


class DragExObjectOoTEmptyProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description="Type of OoT empty object",
        default="NONE",
        items=(("NONE", "None", "No type. A regular empty object"),),
    )

    export_pos: bpy.props.BoolProperty(
        name="Export Position",
        description=(
            "On export, write the location of this empty to a positions.h file"
        ),
    )
    export_pos_name: bpy.props.StringProperty(
        name="Export Position Name",
        description="The name of the macro to name the exported location as",
        default="POS_",
        update=validate_export_pos_name,
    )

    export_rot_yxz: bpy.props.BoolProperty(
        name="Export Rotation",
        description=(
            "On export, write the rotation (as Euler YXZ, as used by Actor_Draw)"
            " of this empty to a positions.h file"
        ),
    )
    export_rot_yxz_name: bpy.props.StringProperty(
        name="Export Rotation Name",
        description="The name of the macro to name the exported rotation as",
        default="ROT_",
        update=validate_export_rot_yxz_name,
    )

    export_yaw: bpy.props.BoolProperty(
        name="Export Yaw",
        description=(
            "On export, write the yaw (rotation around the vertical axis)"
            " of this empty to a positions.h file"
        ),
    )
    export_yaw_name: bpy.props.StringProperty(
        name="Export Yaw Name",
        description="The name of the macro to name the exported yaw as",
        default="YAW_",
        update=validate_export_yaw_name,
    )


class DragExObjectOoTProperties(bpy.types.PropertyGroup):
    empty_: bpy.props.PointerProperty(type=DragExObjectOoTEmptyProperties)

    @property
    def empty(self) -> DragExObjectOoTEmptyProperties:
        return self.empty_


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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore

        scene_coll = bpy.data.collections.new(scene_name)
        scene_coll_dragex: DragExCollectionProperties = scene_coll.dragex  # type: ignore
        scene_coll_dragex.oot.type = "SCENE"

        scale = scene_dragex.oot.scale
        room_colls = list[bpy.types.Collection]()
        for room_number, room_name in enumerate(room_names):
            room_coll = bpy.data.collections.new(room_name)
            room_colls.append(room_coll)
            room_coll_dragex: DragExCollectionProperties = room_coll.dragex  # type: ignore
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
        spawn_empty_obj_dragex: DragExObjectProperties = spawn_empty_obj.dragex  # type: ignore
        spawn_empty_obj.location = (0, 0, 0)
        spawn_empty_obj.empty_display_type = "ARROWS"
        spawn_empty_obj_dragex.oot.empty.export_pos = True
        spawn_empty_obj_dragex.oot.empty.export_pos_name = (
            f"POS_{util.make_c_identifier(scene_name).upper()}_SPAWN"
        )
        scene_coll.objects.link(spawn_empty_obj)

        scene.collection.children.link(scene_coll)
        return {"FINISHED"}


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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        assert self.layout is not None
        scene = context.scene
        assert scene is not None
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        self.layout.prop(scene_dragex.oot, "scale")
        self.layout.operator(DragExOoTNewSceneOperator.bl_idname)
        self.layout.operator(DragExOoTExportSceneOperator.bl_idname)


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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        coll = context.collection
        assert coll is not None
        coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
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
        scene_dragex: DragExSceneProperties = scene.dragex  # type: ignore
        return scene_dragex.target == "OOT_F3DEX2_PL" and obj.type == "EMPTY"

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        obj = context.object
        assert obj is not None
        obj_dragex: DragExObjectProperties = obj.dragex  # type: ignore
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
                coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
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
