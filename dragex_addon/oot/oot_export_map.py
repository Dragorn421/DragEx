import abc
from collections.abc import Sequence
import dataclasses
import math
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import numpy as np

import bpy
import mathutils

from .. import mesh
from .. import util

if TYPE_CHECKING:
    from ...dragex_backend import dragex_backend
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
            mat_dragex = util.DRAGEX(mat)
            polytype_name = mat_dragex.oot.polytype_name
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


@dataclasses.dataclass(eq=False)
class OoTRoomShape(abc.ABC):
    image_infos: mesh.ImageInfos


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

    transform3 = export_options.transform.to_3x3()
    transform3_inverted = transform3.inverted()

    room_colls = dict[int, bpy.types.Collection]()
    for coll in coll_scene.children_recursive:
        coll_dragex = util.DRAGEX(coll)
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
        room_coll_dragex = util.DRAGEX(room_coll)
        entries_opa = list[dragex_backend.MeshInfo]()
        entries_xlu = list[dragex_backend.MeshInfo]()
        image_infos = mesh.ImageInfos()
        for obj in room_coll.all_objects:
            if obj.type == "EMPTY":
                obj_dragex = util.DRAGEX(obj)
                ...
            if obj.type == "MESH":
                assert isinstance(obj.data, bpy.types.Mesh)
                # TODO this is inefficient if mesh is shared between rooms
                mesh_info = mesh.mesh_to_mesh_info(
                    obj,
                    obj.data,
                    # TODO test more with different matrix_world
                    export_options.transform @ obj.matrix_world,
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
                # TODO test more with different matrix_world
                export_options.transform @ obj.matrix_world,
            )
            collision_meshes.append(collision_mesh)
    collision = dragex_backend.join_OoTCollisionMeshes(collision_meshes)

    positions = dict[str, tuple[int, int, int]]()
    rotations_yxz = dict[str, mathutils.Euler]()
    yaws = dict[str, float]()
    for obj in coll_scene.all_objects:
        if obj.type == "EMPTY":
            obj_dragex = util.DRAGEX(obj)

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
                transform3
                @ obj_rot_quaternion.to_matrix()
                @ transform3_inverted
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
                    dl_name = mi.write_c(room_fd, ())
                    opa_dlists_names.append(dl_name)
                for mi in room_shape.entries_xlu:
                    dl_name = mi.write_c(room_fd, ())
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
