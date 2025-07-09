from collections.abc import Buffer, Sequence
import os

def get_build_id() -> int: ...

class MaterialInfoOtherModes:
    def __init__(
        self,
        #
        atomic_prim: bool,
        cycle_type: str,
        persp_tex_en: bool,
        detail_tex_en: bool,
        sharpen_tex_en: bool,
        tex_lod_en: bool,
        tlut_en: bool,
        tlut_type: bool,
        #
        sample_type: bool,
        mid_texel: bool,
        bi_lerp_0: bool,
        bi_lerp_1: bool,
        convert_one: bool,
        key_en: bool,
        rgb_dither_sel: str,
        alpha_dither_sel: str,
        #
        bl_m1a_0: str,
        bl_m1a_1: str,
        bl_m1b_0: str,
        bl_m1b_1: str,
        bl_m2a_0: str,
        bl_m2a_1: str,
        bl_m2b_0: str,
        bl_m2b_1: str,
        #
        force_blend: bool,
        alpha_cvg_select: bool,
        cvg_x_alpha: bool,
        z_mode: str,
        cvg_dest: str,
        color_on_cvg: bool,
        #
        image_read_en: bool,
        z_update_en: bool,
        z_compare_en: bool,
        antialias_en: bool,
        z_source_sel: bool,
        dither_alpha_en: bool,
        alpha_compare_en: bool,
    ) -> None: ...

class MaterialInfoCombiner:
    def __init__(
        self,
        rgb_A_0: str,
        rgb_B_0: str,
        rgb_C_0: str,
        rgb_D_0: str,
        alpha_A_0: str,
        alpha_B_0: str,
        alpha_C_0: str,
        alpha_D_0: str,
        rgb_A_1: str,
        rgb_B_1: str,
        rgb_C_1: str,
        rgb_D_1: str,
        alpha_A_1: str,
        alpha_B_1: str,
        alpha_C_1: str,
        alpha_D_1: str,
    ) -> None: ...

class MaterialInfoGeometryMode:
    def __init__(
        self,
        lighting: bool,
    ) -> None: ...

class MaterialInfo:
    def __init__(
        self,
        name: str,
        uv_basis_s: int,
        uv_basis_t: int,
        other_modes: MaterialInfoOtherModes,
        combiner: MaterialInfoCombiner,
        geometry_mode: MaterialInfoGeometryMode,
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
