from pathlib import Path
import random
import traceback

import numpy as np

import dragex_backend


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

default_mat_info = dragex_backend.MaterialInfo(
    name="mymaterial",
    lighting=False,
)

mi = dragex_backend.create_MeshInfo(
    buf_vertices_co,
    buf_triangles_loops,
    buf_triangles_material_index,
    buf_loops_vertex_index,
    buf_loops_normal,
    buf_corners_color,
    [],
    default_mat_info,
)
print("mi =", mi)
mi.write_c(Path(__file__).parent / "test_out.c")
mi.write_c(str(Path(__file__).parent / "test_out.c"))
print("del mi")
del mi
print("del mi done")
