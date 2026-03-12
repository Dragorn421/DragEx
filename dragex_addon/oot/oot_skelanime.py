import dataclasses
import math
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Iterable

import bpy
import mathutils

import numpy as np

from .. import mesh
from .. import util

if TYPE_CHECKING:
    from ...dragex_backend import dragex_backend
else:
    try:
        import dragex_backend
    except ModuleNotFoundError:
        dragex_backend = None


def find_root_bone(bones: Iterable[bpy.types.Bone]):

    root_bones: set[bpy.types.Bone] = set()
    for bone in bones:
        if not bone.use_deform:
            continue
        if bone.parent is None:
            root_bones.add(bone)
        else:
            root_bones.add(bone.parent_recursive[-1])
    if len(root_bones) != 1:
        raise Exception(
            f"Found {len(root_bones)} root bones instead of exactly 1: "
            + ", ".join(_b.name for _b in root_bones)
        )
    (root_bone,) = root_bones
    return root_bone


@dataclasses.dataclass
class BoneHierarchy:
    bone: bpy.types.Bone
    child: "BoneHierarchy | None"
    sibling: "BoneHierarchy | None"


def build_hierarchy(b: bpy.types.Bone, siblings: list[bpy.types.Bone]):
    children_b = sorted(b.children, key=lambda _b: _b.name.lower())
    if children_b:
        child_h = build_hierarchy(children_b[0], children_b[1:])
    else:
        child_h = None
    if siblings:
        sibling_h = build_hierarchy(siblings[0], siblings[1:])
    else:
        sibling_h = None
    return BoneHierarchy(b, child_h, sibling_h)


def get_all_bones(bh: BoneHierarchy):
    bones = [bh]
    if bh.child is not None:
        bones.extend(get_all_bones(bh.child))
    if bh.sibling is not None:
        bones.extend(get_all_bones(bh.sibling))
    return bones


def do_work(
    armature_object: bpy.types.Object,
    armature_data: bpy.types.Armature,
    mesh_objects: list[bpy.types.Object],
    global_transform: mathutils.Matrix,
    weight_epsilon: float,
    export_directory: Path,
    decomp_repo_p: Path,
):
    root_bone = find_root_bone(armature_data.bones)

    rbh = build_hierarchy(root_bone, [])

    dragex_backend.logging.debug(f"{rbh=}")

    def print_hierarchy(bh: BoneHierarchy, indent=""):
        dragex_backend.logging.debug(f"{indent}{bh.bone.name}")
        if bh.child is not None:
            print_hierarchy(bh.child, indent + "  ")
        if bh.sibling is not None:
            print_hierarchy(bh.sibling, indent)

    print_hierarchy(rbh)

    all_bones = get_all_bones(rbh)

    vertex_transforms_per_limb: list[mathutils.Matrix] = []
    for bh in all_bones:
        vertex_transforms_per_limb.append(
            mathutils.Matrix.Translation(-bh.bone.head_local)
        )

    dragex_backend.logging.debug(
        "\n".join(
            f"{_i:3} {_mtx.translation}"
            for _i, _mtx in enumerate(vertex_transforms_per_limb)
        )
    )

    limb_index_by_bone_name = {_bh.bone.name: _i for _i, _bh in enumerate(all_bones)}

    dragex_backend.logging.debug(f"{limb_index_by_bone_name=}")

    corner_material_infos = [
        dragex_backend.CornerMaterialInfo(_limb_index)
        for _limb_index in range(len(all_bones))
    ]
    default_corner_material_info = dragex_backend.CornerMaterialInfo(len(all_bones))
    limb_to_matrix_map = [
        f"0x{0x0D00_0000 + _limb_index * 0x40:08X}"
        for _limb_index in range(len(all_bones))
    ]

    skeleton_c_identifier = util.make_c_identifier(armature_object.name)

    image_infos = mesh.ImageInfos()
    mesh_infos_by_limb: dict[int, list[dragex_backend.MeshInfo]] = {}
    for mesh_obj in mesh_objects:
        dragex_backend.logging.debug(f"{mesh_obj}")
        limb_index_by_group_index = {
            _g.index: limb_index_by_bone_name[_g.name]
            for _g in mesh_obj.vertex_groups
            if _g.name in limb_index_by_bone_name
        }
        dragex_backend.logging.debug(f"{limb_index_by_group_index=}")
        assert isinstance(mesh_obj.data, bpy.types.Mesh)

        limb_index_per_vertex = np.empty(len(mesh_obj.data.vertices), dtype=np.uint)
        for v in mesh_obj.data.vertices:
            v_groups = sorted(
                (_g for _g in v.groups if _g.group in limb_index_by_group_index),
                key=lambda _g: _g.weight,
                reverse=True,
            )
            is_unassigned = (
                len(v_groups) == 0 or v_groups[0].weight < 1 - weight_epsilon
            )
            is_multiassigned = (
                len(v_groups) >= 2 and v_groups[1].weight > weight_epsilon
            )
            assert not is_unassigned, "unassigned vertex"
            assert not is_multiassigned, "multi-assigned vertex"
            limb_index_per_vertex[v.index] = limb_index_by_group_index[
                v_groups[0].group
            ]

        buf_corners_material_index = util.new_uint_buf(len(mesh_obj.data.loops))
        for l in mesh_obj.data.loops:
            buf_corners_material_index[l.index] = limb_index_per_vertex[l.vertex_index]

        mesh_obj.data.calc_loop_triangles()  # TODO is this costly? we call it twice
        submeshes_masks = [
            np.zeros(len(mesh_obj.data.loop_triangles), dtype=bool) for _bh in all_bones
        ]
        # TODO this probably can be written with numpy for speed:
        for tri in mesh_obj.data.loop_triangles:
            submeshes_masks[max(buf_corners_material_index[_l] for _l in tri.loops)][
                tri.index
            ] = True

        transform_per_vertex = limb_index_per_vertex
        transforms = [
            # TODO should mesh_obj.matrix_world be before or after _mtx ?
            global_transform @ _mtx @ mesh_obj.matrix_world
            for _mtx in vertex_transforms_per_limb
        ]

        mesh_infos_list = mesh.mesh_to_mesh_infos_general(
            mesh_obj,
            mesh_obj.data,
            transform_per_vertex,
            transforms,
            image_infos,
            skeleton_c_identifier + "_",
            [
                mesh.SubMeshInfo(
                    submeshes_masks[_i],
                    f"_limb_{_i}",
                )
                for _i in range(len(all_bones))
            ],
            buf_corners_material_index,
            corner_material_infos,
            default_corner_material_info,
        )
        for i, mesh_info in enumerate(mesh_infos_list):
            mesh_infos_by_limb.setdefault(i, []).append(mesh_info)

    import os

    with util.FDManager() as fdm:
        fd = fdm.open_w(export_directory / f"{skeleton_c_identifier}.c")
        with os.fdopen(fd, "w", closefd=False) as f:
            f.write('#include "ultra64.h"\n')
            f.write('#include "animation.h"\n')
            f.write('#include "array_count.h"\n')

            # TODO copypasted from export_coll_scene in oot_export_map.py, consolidate
            for (
                c_identifier,
                image_key,
            ) in image_infos.key_by_c_identifier.items():
                image_file_stem = (
                    f"{c_identifier}.{image_key.format.lower()}{image_key.size}"
                )
                # TODO save() may set the image's filepath as a side-effect?
                # (not in 4.2.11 at least, but recent versions (which?) have a save_copy argument to save())
                # if so, need to copy() the datablock before save to avoid modifying it
                image_key.image.save(
                    filepath=str(export_directory / f"{image_file_stem}.png"),
                )
                image_inc_c_p = (
                    PurePosixPath(*export_directory.relative_to(decomp_repo_p).parts)
                    / f"{image_file_stem}.inc.c"
                )
                f.write(
                    f"u64 {c_identifier}[] = "
                    "{\n"
                    f'#include "{image_inc_c_p}"\n'
                    "};\n"
                    "\n"
                )

        limb_dl_name_by_limb: dict[int, str] = {}
        for limb, mesh_infos in mesh_infos_by_limb.items():
            with os.fdopen(fd, "w", closefd=False) as f:
                f.write(f"// limb {limb}\n")
            limb_dl_name = None
            for mi in mesh_infos:
                assert (
                    limb_dl_name is None
                ), "notimplemented: several meshes parented to armature"
                limb_dl_name = mi.write_c(fd, limb_to_matrix_map)
            assert limb_dl_name is not None, "no mesh parented to armature?"
            limb_dl_name_by_limb[limb] = limb_dl_name
        limb_names = [
            (skeleton_c_identifier + "_" + util.make_c_identifier(_bh.bone.name))
            for _bh in all_bones
        ]
        limb_enum_names = [_ln.upper() for _ln in limb_names]
        with os.fdopen(fd, "w", closefd=False) as f:
            f.write(f"typedef enum {skeleton_c_identifier}Limb " "{\n")
            f.write(f"    {skeleton_c_identifier.upper()}_NONE,\n")
            for limben in limb_enum_names:
                f.write(f"    {limben},\n")
            f.write(f"    {skeleton_c_identifier.upper()}_MAX\n")
            f.write("} " f"{skeleton_c_identifier}Limb;\n")
            for limb, bh in enumerate(all_bones):
                if bh.bone.parent is None:
                    # the jointPos of the root limb is unused
                    # (see e.g. SkelAnime_DrawFlex)
                    # A root bone that is not located at 0,0,0 relative to the armature
                    # is still supported by encoding that position as part of animations
                    jointPos = mathutils.Vector((0, 0, 0))
                else:
                    jointPos = global_transform @ (
                        bh.bone.head_local - bh.bone.parent.head_local
                    )
                jointPos_x = round(jointPos.x)
                jointPos_y = round(jointPos.y)
                jointPos_z = round(jointPos.z)
                f.write(f"StandardLimb {limb_names[limb]} = " "{\n")
                f.write("    { " f"{jointPos_x}, {jointPos_y}, {jointPos_z}" " },\n")
                if bh.child is not None:
                    f.write(f"    {limb_enum_names[all_bones.index(bh.child)]} - 1,\n")
                else:
                    f.write(f"    LIMB_DONE,\n")
                if bh.sibling is not None:
                    f.write(
                        f"    {limb_enum_names[all_bones.index(bh.sibling)]} - 1,\n"
                    )
                else:
                    f.write(f"    LIMB_DONE,\n")
                f.write(f"    {limb_dl_name_by_limb[limb]},\n")
                f.write("};\n")
            limbs_table_sym_name = f"{skeleton_c_identifier}Limbs"
            f.write(f"void* {limbs_table_sym_name}[] = " "{\n")
            for ln in limb_names:
                f.write(f"    &{ln},\n")
            f.write("};\n")
            f.write(f"FlexSkeletonHeader {skeleton_c_identifier} = " "{\n")
            f.write("    {\n")
            f.write(f"        {limbs_table_sym_name},\n")
            f.write(f"        ARRAY_COUNT({limbs_table_sym_name}),\n")
            f.write("    },\n")
            f.write(f"    {len(all_bones)},\n")
            f.write("};\n")


def rad2bin(rad: float):
    binang = round(rad / math.pi * 0x8000) % 0x1_0000
    if binang >= 0x8000:
        binang -= 0x1_0000
    return binang


def HEx(v: int, n_digits: int = 0):
    return f"{v:#0{n_digits + 2 + (1 if v < 0 else 0)}X}".replace("0X", "0x")


def export_anim(
    armature_obj: bpy.types.Object,
    armature_data: bpy.types.Armature,
    frame_start: int,
    frame_count: int,
    global_transform: mathutils.Matrix,
    export_directory: Path,
    anim_c_identifier: str,
):
    scene = bpy.context.scene
    assert scene is not None

    root_bone = find_root_bone(armature_data.bones)
    rbh = build_hierarchy(root_bone, [])
    all_bones = get_all_bones(rbh)

    saved_frame_current = scene.frame_current
    saved_frame_subframe = scene.frame_subframe

    global_transform3 = global_transform.to_3x3()
    global_transform3_inv = global_transform3.inverted()

    joint_tables: list[tuple[tuple[int, int, int], ...]] = []

    try:
        for frame in range(frame_start, frame_start + frame_count):
            scene.frame_set(frame)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            armature_obj_eval = armature_obj.evaluated_get(depsgraph)
            assert armature_obj_eval.pose is not None
            pose_bones = armature_obj_eval.pose.bones
            root_pose_bone = pose_bones[root_bone.name]
            # Note the pose bone head location includes the bone rest pose location,
            # plus the animated location. This allows the root bone to not have to be
            # at 0,0,0 relative to the armature in the rest pose
            root_loc = global_transform @ root_pose_bone.head
            root_rot = (
                global_transform3
                @ root_pose_bone.matrix_channel.to_3x3()
                @ global_transform3_inv
            ).to_euler("XYZ")

            rots: list[mathutils.Euler] = [root_rot]

            for bh in all_bones[1:]:
                pb = pose_bones[bh.bone.name]
                assert pb.parent is not None
                rot = (
                    global_transform3
                    @ pb.parent.matrix_channel.to_3x3().transposed()
                    @ pb.matrix_channel.to_3x3()
                    @ global_transform3_inv
                ).to_euler("XYZ")
                rots.append(rot)

            joint_table = (
                (round(root_loc.x), round(root_loc.y), round(root_loc.z)),
                *((rad2bin(rot.x), rad2bin(rot.y), rad2bin(rot.z)) for rot in rots),
            )

            dragex_backend.logging.debug(
                f"Vec3s {anim_c_identifier}JointTable{frame}[] = "
                "{\n"
                + "".join(
                    "    { " f"{HEx(x, 4)}, {HEx(y, 4)}, {HEx(z, 4)}" " },\n"
                    for x, y, z in joint_table
                )
                + "};"
            )

            joint_tables.append(joint_table)
    finally:
        scene.frame_set(saved_frame_current, subframe=saved_frame_subframe)

    len_joint_table = 1 + len(all_bones)

    joint_indices: dict[tuple[int, int], int] = {}
    frame_data: list[int] = []
    dynamic_channels: list[tuple[int, int]] = []

    for i in range(len_joint_table):
        for j in range(3):
            if len({_joint_table[i][j] for _joint_table in joint_tables}) == 1:
                static_value = joint_tables[0][i][j]
                try:
                    index = frame_data.index(static_value)
                except ValueError:
                    index = None
                if index is None:
                    index = len(frame_data)
                    frame_data.append(static_value)
                joint_indices[(i, j)] = index
            else:
                dynamic_channels.append((i, j))

    static_index_max = len(frame_data)

    for i, j in dynamic_channels:
        joint_indices[(i, j)] = len(frame_data)
        frame_data.extend(_joint_table[i][j] for _joint_table in joint_tables)

    with (export_directory / f"{anim_c_identifier}.c").open("w") as f:
        f.write('#include "ultra64.h"\n')
        f.write('#include "animation.h"\n')

        f.write(f"s16 {anim_c_identifier}FrameData[] = " "{\n")
        i = 0
        while i < len(frame_data):
            j = min(i + 50, len(frame_data))
            f.write(
                "    " + ", ".join(HEx(frame_data[_k], 4) for _k in range(i, j)) + ",\n"
            )
            i = j
        f.write("};\n")

        f.write(f"JointIndex {anim_c_identifier}JointIndices[] = " "{\n")
        for i in range(len_joint_table):
            f.write(
                "    { "
                + ", ".join(str(joint_indices[(i, _j)]) for _j in range(3))
                + " },\n"
            )
        f.write("};\n")

        f.write(f"AnimationHeader {anim_c_identifier} = " "{\n")
        f.write("    { " f"{len(joint_tables)}" " },\n")
        f.write(f"    {anim_c_identifier}FrameData,\n")
        f.write(f"    {anim_c_identifier}JointIndices,\n")
        f.write(f"    {static_index_max},\n")
        f.write("};\n")
