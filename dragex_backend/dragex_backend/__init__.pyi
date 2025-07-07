from collections.abc import Buffer, Sequence
import os

def get_build_id() -> int: ...

class MaterialInfo:
    def __init__(
        self,
        name: str,
        uv_basis_s: int,
        uv_basis_t: int,
        lighting: bool,
    ) -> None: ...

class MeshInfo:
    def write_c(self, path: str | os.PathLike, /) -> None: ...

def create_MeshInfo(
    buf_vertices_co: Buffer,
    buf_triangles_loops: Buffer,
    buf_triangles_material_index: Buffer,
    buf_loops_vertex_index: Buffer,
    buf_loops_normal: Buffer,
    buf_corners_color: Buffer | None,
    buf_loops_uv: Buffer | None,
    material_infos: Sequence[MaterialInfo | None],
    default_material: MaterialInfo,
    /,
) -> MeshInfo: ...
