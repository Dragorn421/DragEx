from pathlib import Path
import random
import traceback

import numpy as np

import dragex_backend


fbt = dragex_backend.FloatBufferThing(3, 421.421421421421)
mv = memoryview(fbt)
a = mv[0]
del mv
print(fbt)
print(memoryview(fbt))
print(memoryview(fbt)[0])
print(bytes(fbt))
print(len(bytes(memoryview(fbt))))

fbt.__init__(2, 42)
print(memoryview(fbt)[0])
print(bytes(memoryview(fbt)))
print(len(bytes(memoryview(fbt))))

try:
    dragex_backend.create_MeshInfo(None, None, None)
except TypeError:
    traceback.print_exc()
try:
    dragex_backend.create_MeshInfo(dragex_backend.FloatBufferThing(3), None, None)
except TypeError:
    traceback.print_exc()

buf_vertices_co = dragex_backend.FloatBufferThing(3 * 3)
buf_triangles_loops = np.empty(
    shape=3 * 1,
    dtype=np.uint32,
    order="C",
)
buf_triangles_loops[0] = 0
buf_triangles_loops[1] = 1
buf_triangles_loops[2] = 2
buf_loops_vertex_index = np.empty(
    shape=3 * 1,
    dtype=np.uint32,
    order="C",
)
buf_loops_vertex_index[0] = 0
buf_loops_vertex_index[1] = 1
buf_loops_vertex_index[2] = 2

mi = dragex_backend.create_MeshInfo(
    buf_vertices_co,
    buf_triangles_loops,
    buf_loops_vertex_index,
)
print("mi =", mi)
mi.write_c(Path(__file__).parent / "test_out.c")
mi.write_c(str(Path(__file__).parent / "test_out.c"))
print("del mi")
del mi
print("del mi done")
