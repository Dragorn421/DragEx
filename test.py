import os
from pathlib import Path
import random
import traceback

import numpy as np

import dragex_backend


dragex_backend.logging.set_log_file(Path(__file__).parent / "test_log.txt")


try:
    dragex_backend.create_MeshInfo(None, None, None, None)
except TypeError:
    traceback.print_exc()
try:
    dragex_backend.create_MeshInfo(np.zeros(3, dtype=np.float32), None, None, None)
except TypeError:
    traceback.print_exc()

buf_vertices_co = np.zeros(
    shape=3 * 3,
    dtype=np.float32,
    order="C",
)
buf_triangles_loops = np.empty(
    shape=3 * 1,
    dtype=np.uint32,
    order="C",
)
buf_triangles_loops[0] = 0
buf_triangles_loops[1] = 1
buf_triangles_loops[2] = 2
buf_triangles_material_index = np.empty(
    shape=1,
    dtype=np.uint32,
    order="C",
)
buf_triangles_material_index[0] = 0
buf_loops_vertex_index = np.empty(
    shape=3 * 1,
    dtype=np.uint32,
    order="C",
)
buf_loops_vertex_index[0] = 0
buf_loops_vertex_index[1] = 1
buf_loops_vertex_index[2] = 2
buf_loops_normal = np.zeros(
    shape=3 * 3,
    dtype=np.float32,
    order="C",
)
buf_corners_color = np.zeros(
    shape=3 * 4,
    dtype=np.float32,
    order="C",
)
buf_corners_color[1] = 1.0

buf_loops_uv = np.zeros(
    shape=3 * 2,
    dtype=np.float32,
    order="C",
)

default_mat_info = dragex_backend.MaterialInfo(
    name="mymaterial",
    uv_basis_s=1,
    uv_basis_t=1,
    other_modes=dragex_backend.MaterialInfoOtherModes(
        atomic_prim=False,
        cycle_type="1CYCLE",
        persp_tex_en=False,
        detail_tex_en=False,
        sharpen_tex_en=False,
        tex_lod_en=False,
        tlut_en=False,
        tlut_type=False,
        #
        sample_type=False,
        mid_texel=False,
        bi_lerp_0=False,
        bi_lerp_1=False,
        convert_one=False,
        key_en=False,
        rgb_dither_sel="MAGIC_SQUARE",
        alpha_dither_sel="NONE",
        #
        bl_m1a_0="INPUT",
        bl_m1a_1="INPUT",
        bl_m1b_0="0",
        bl_m1b_1="0",
        bl_m2a_0="INPUT",
        bl_m2a_1="INPUT",
        bl_m2b_0="1",
        bl_m2b_1="1",
        #
        force_blend=False,
        alpha_cvg_select=False,
        cvg_x_alpha=False,
        z_mode="OPAQUE",
        cvg_dest="CLAMP",
        color_on_cvg=False,
        #
        image_read_en=False,
        z_update_en=False,
        z_compare_en=False,
        antialias_en=False,
        z_source_sel=False,
        dither_alpha_en=False,
        alpha_compare_en=False,
    ),
    tiles=(
        [
            dragex_backend.MaterialInfoTile(
                image=dragex_backend.MaterialInfoImage(
                    c_identifier="image_c_identifier",
                    width=32,
                    height=32,
                ),
                format="RGBA",
                size="16",
                line=32 * 2,
                address=0,
                palette=0,
                clamp_T=False,
                mirror_T=False,
                mask_T=5,
                shift_T=0,
                clamp_S=False,
                mirror_S=False,
                mask_S=5,
                shift_S=0,
                upper_left_S=0,
                upper_left_T=0,
                lower_right_S=32 - 1,
                lower_right_T=32 - 1,
            )
        ]
        * 8
    ),
    combiner=dragex_backend.MaterialInfoCombiner(
        "0",
        "0",
        "0",
        "TEX0",
        "0",
        "0",
        "0",
        "1",
        "0",
        "0",
        "0",
        "TEX0",
        "0",
        "0",
        "0",
        "1",
    ),
    vals=dragex_backend.MaterialInfoVals(
        primitive_depth_z=0,
        primitive_depth_dz=0,
        fog_color=(1, 1, 1, 1),
        blend_color=(1, 1, 1, 1),
        min_level=0,
        prim_lod_frac=0,
        primitive_color=(1, 1, 1, 1),
        environment_color=(1, 1, 1, 1),
    ),
    geometry_mode=dragex_backend.MaterialInfoGeometryMode(
        lighting=False,
    ),
)

mi = dragex_backend.create_MeshInfo(
    buf_vertices_co,
    buf_triangles_loops,
    buf_triangles_material_index,
    buf_loops_vertex_index,
    buf_loops_normal,
    buf_corners_color,
    None,
    buf_loops_uv,
    [],
    default_mat_info,
)

print("del default_mat_info")
del default_mat_info
print("del default_mat_info done")

print("mi =", mi)
fd = os.open(
    Path(__file__).parent / "test_out.c", os.O_CREAT | os.O_WRONLY | os.O_TRUNC
)
dl_name = mi.write_c(fd)
print("del mi")
del mi
print("del mi done")

print(f"{dl_name=}")

dragex_backend.logging.trace("test")
dragex_backend.logging.debug("test")
dragex_backend.logging.info("test")
dragex_backend.logging.warn("test")
dragex_backend.logging.error("test")
dragex_backend.logging.fatal("test")

dragex_backend.logging.flush()  # useless here but just for testing the method
dragex_backend.logging.clear_log_file()

oot_collision_material = dragex_backend.OoTCollisionMaterial(
    "SURFTYPE0", "SURFTYPE1", "FLAGSA", "FLAGSB"
)
oot_collision_mesh = dragex_backend.create_OoTCollisionMesh(
    buf_vertices_co,
    buf_triangles_loops,
    buf_triangles_material_index,
    buf_loops_vertex_index,
    [],
    oot_collision_material,
)

os.write(fd, b"// oot_collision_mesh.write_c\n")
bounds = oot_collision_mesh.write_c(
    fd,
    "magicVtxList",
    "magicPolyList",
    "magicSurfaceTypes",
)
print(f"{bounds=}")
print(f"{bounds.min=}")
print(f"{bounds.max=}")
oot_collision_mesh_joined = dragex_backend.join_OoTCollisionMeshes(
    [oot_collision_mesh, oot_collision_mesh]
)
os.write(fd, b"// oot_collision_mesh_joined.write_c\n")
oot_collision_mesh_joined.write_c(
    fd,
    "magicJoinedVtxList",
    "magicJoinedPolyList",
    "magicJoinedSurfaceTypes",
)

os.close(fd)
