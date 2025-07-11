from collections.abc import Buffer, Sequence
import os
from typing import Optional

def get_build_id() -> int: ...

class MaterialInfoImage:
    def __init__(
        self,
        c_identifier: str,
        width: int,
        height: int,
    ) -> None: ...

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

class MaterialInfoTile:
    def __init__(
        self,
        image: Optional[MaterialInfoImage],
        #
        format: str,
        size: str,
        line: int,
        address: int,
        palette: int,
        clamp_T: bool,
        mirror_T: bool,
        mask_T: int,
        shift_T: int,
        clamp_S: bool,
        mirror_S: bool,
        mask_S: int,
        shift_S: int,
        #
        upper_left_S: float,
        upper_left_T: float,
        lower_right_S: float,
        lower_right_T: float,
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

class MaterialInfoVals:
    def __init__(
        self,
        primitive_depth_z: int,
        primitive_depth_dz: int,
        fog_color: tuple[float, float, float, float],
        blend_color: tuple[float, float, float, float],
        min_level: int,
        prim_lod_frac: int,
        primitive_color: tuple[float, float, float, float],
        environment_color: tuple[float, float, float, float],
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
        tiles: Sequence[MaterialInfoTile],
        combiner: MaterialInfoCombiner,
        vals: MaterialInfoVals,
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
    buf_points_color: Buffer | None,
    buf_loops_uv: Buffer | None,
    material_infos: Sequence[MaterialInfo | None],
    default_material: MaterialInfo,
    /,
) -> MeshInfo: ...
