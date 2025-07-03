from collections.abc import Buffer
import os

def get_build_id() -> int: ...

class FloatBufferThing(Buffer):
    def __init__(self, length: int, value: float = 0.0) -> None: ...
    # memoryview should be memoryview[float] but that makes Pylance complain
    def __buffer__(self, flags: int, /) -> memoryview: ...

class MeshInfo:
    def write_c(self, path: str | os.PathLike) -> None: ...

def create_MeshInfo(
    buf_vertices_co: Buffer,
    buf_triangles_loops: Buffer,
    buf_loops_vertex_index: Buffer,
    buf_loops_normal: Buffer,
) -> MeshInfo: ...
