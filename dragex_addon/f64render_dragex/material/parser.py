import copy
from dataclasses import dataclass
import dataclasses
import functools
import struct
import bpy
import mathutils
import numpy as np
from typing import TYPE_CHECKING

from .tile import get_tile_conf, F64Texture
from .cc import SOLID_CC, get_cc_settings
from ..globals import F64_GLOBALS
from . import pydefines

if TYPE_CHECKING:
    from ... import DragExMaterialProperties


@functools.cache
def quantize(x: float, bits: int, mi=0.0, ma=1.0):  # quantize in a range
    value_count = 2**bits - 1
    range_size = ma - mi
    return mi + round((x - mi) / range_size * value_count) / value_count * range_size


@functools.cache
def quantize_tuple_cached(t: tuple, bits: int, mi=0.0, ma=1.0):
    return tuple(quantize(x, bits, mi, ma) for x in t)


def quantize_tuple(t, bits: int, mi=0.0, ma=1.0):
    return quantize_tuple_cached(tuple(t), bits, mi, ma)


@functools.cache
def quantize_srgb_cached(linear_color: tuple, include_alpha: bool, force_alpha: bool):
    result = list(mathutils.Color(linear_color[:3]).from_scene_linear_to_srgb())
    if include_alpha or force_alpha:
        if len(linear_color) > 3 and not force_alpha:
            result.append(linear_color[3])
        else:
            result.append(1.0)
    return quantize_tuple(result, 8)


def quantize_srgb(
    linear_color, include_alpha=True, force_alpha=False
):  # caching this makes it basically free in subsequent frames
    return quantize_srgb_cached(tuple(linear_color), include_alpha, force_alpha)


GEO_MODE_ATTRS = [
    "g_zbuffer",
    "g_shade",
    "g_cull_front",
    "g_cull_back",
    "g_ambocclusion",
    "g_attroffset_z_enable",
    "g_attroffset_st_enable",
    "g_packed_normals",
    "g_lighttoalpha",
    "g_lighting_specular",
    "g_fresnel_color",
    "g_fresnel_alpha",
    "g_fog",
    "g_lighting",
    "g_tex_gen",
    "g_tex_gen_linear",
    "g_lod",
    "g_shade_smooth",
    "g_clipping",
]


@dataclass
class RenderMode:  # one class for all rendermodes
    aa_en: bool = False
    z_cmp: bool = False
    z_upd: bool = False
    im_rd: bool = False
    clr_on_cvg: bool = False
    cvg_dst: str = "CVG_DST_CLAMP"
    zmode: str = "ZMODE_OPA"
    cvg_x_alpha: bool = False
    alpha_cvg_sel: bool = False
    force_bl: bool = False
    blend_cycle1: tuple[int, int, int, int] = (
        pydefines.BLENDER_CLR_IN,
        pydefines.BLENDER_A_IN,
        pydefines.BLENDER_CLR_IN,
        pydefines.BLENDER_1MA,
    )
    blend_cycle2: tuple[int, int, int, int] = (
        pydefines.BLENDER_CLR_IN,
        pydefines.BLENDER_A_IN,
        pydefines.BLENDER_CLR_IN,
        pydefines.BLENDER_1MA,
    )


@functools.cache
def parse_f3d_rendermode_preset(preset_cycle1: str, preset_cycle2: str | None):
    return RenderMode()  # TODO-tmp_porting

    # TODO: If/When porting to fast64 reuse this in rendermode_preset_to_advanced (where the logic is sourced)
    from fast64_internal.f3d.f3d_gbi import get_F3D_GBI

    f3d = get_F3D_GBI()

    def get_with_default(preset, default):
        return getattr(f3d, preset, default)

    if preset_cycle2 is not None:
        r1 = get_with_default(preset_cycle1, f3d.G_RM_FOG_SHADE_A)
        r2 = get_with_default(preset_cycle2, f3d.G_RM_AA_ZB_OPA_SURF2)
        r = r1 | r2
    else:
        r = get_with_default(preset_cycle1, f3d.G_RM_AA_ZB_OPA_SURF)
        r1 = r
        # The cycle 1 bits are copied to the cycle 2 bits at export if in 1-cycle mode
        # (the hardware requires them to be the same). So, here we also move the cycle 1
        # bits to the cycle 2 slots. r2 is only read for the cycle dependent settings below.
        r2 = r >> 2

    return RenderMode(
        (r & f3d.AA_EN) != 0,
        (r & f3d.Z_CMP) != 0,
        (r & f3d.Z_UPD) != 0,
        (r & f3d.IM_RD) != 0,
        (r & f3d.CLR_ON_CVG) != 0,
        f3d.cvgDstDict[r & f3d.CVG_DST_SAVE],
        f3d.zmodeDict[r & f3d.ZMODE_DEC],
        (r & f3d.CVG_X_ALPHA) != 0,
        (r & f3d.ALPHA_CVG_SEL) != 0,
        (r & f3d.FORCE_BL) != 0,
        (
            f3d.blendColorDict[(r1 >> 30) & 3],
            f3d.blendAlphaDict[(r1 >> 26) & 3],
            f3d.blendColorDict[(r1 >> 22) & 3],
            f3d.blendMixDict[(r1 >> 18) & 3],
        ),
        (
            f3d.blendColorDict[(r2 >> 28) & 3],
            f3d.blendAlphaDict[(r2 >> 24) & 3],
            f3d.blendColorDict[(r2 >> 20) & 3],
            f3d.blendMixDict[(r2 >> 16) & 3],
        ),
    )


BL_INP = {
    "0": pydefines.BLENDER_0,
    "1": pydefines.BLENDER_1,
    "INPUT": pydefines.BLENDER_CLR_IN,
    "MEMORY": pydefines.BLENDER_CLR_MEM,
    "BLEND_COLOR": pydefines.BLENDER_CLR_BL,
    "FOG_COLOR": pydefines.BLENDER_CLR_FOG,
    "INPUT_ALPHA": pydefines.BLENDER_A_IN,
    "FOG_ALPHA": pydefines.BLENDER_A_FOG,
    "SHADE_ALPHA": pydefines.BLENDER_A_SHADE,
    "1_MINUS_A": pydefines.BLENDER_1MA,
    "MEMORY_COVERAGE": pydefines.BLENDER_A_MEM,
}


def parse_f3d_mat_rendermode(f3d_mat: "DragExMaterialProperties"):
    other_modes = f3d_mat.other_modes

    blend_cycle1 = (
        BL_INP[other_modes.bl_m1a_0],
        BL_INP[other_modes.bl_m1b_0],
        BL_INP[other_modes.bl_m2a_0],
        BL_INP[other_modes.bl_m2b_0],
    )
    if other_modes.cycle_type == "2CYCLE":
        blend_cycle2 = (
            BL_INP[other_modes.bl_m1a_1],
            BL_INP[other_modes.bl_m1b_1],
            BL_INP[other_modes.bl_m2a_1],
            BL_INP[other_modes.bl_m2b_1],
        )
    else:
        # Note: This allows F64RenderState.set_from_rendermode to detect alpha blend by checking blend_cycle2 even in 1-cycle mode
        # Also note: the shader doesn't implement 1-cycle blending. See blendColor in main3d.frag.glsl
        blend_cycle2 = blend_cycle1

    return RenderMode(
        aa_en=other_modes.antialias_en,
        z_cmp=other_modes.z_compare_en,
        z_upd=other_modes.z_update_en,
        im_rd=other_modes.image_read_en,
        clr_on_cvg=other_modes.color_on_cvg,
        cvg_dst=other_modes.cvg_dest,
        zmode=other_modes.z_mode,
        cvg_x_alpha=other_modes.cvg_x_alpha,
        alpha_cvg_sel=other_modes.alpha_cvg_select,
        force_bl=other_modes.force_blend,
        blend_cycle1=blend_cycle1,
        blend_cycle2=blend_cycle2,
    )


LIGHT_STRUCT = "4f 3f 4x"  # color, direction, padding
TILE_STRUCT = "2f 2f 2f 2f i 12x"  # mask, shift, low, high, flags, padding

UNIFORM_BUFFER_STRUCT = struct.Struct(
    (TILE_STRUCT * 8) + (LIGHT_STRUCT * 8) + "8i"  # texture configurations, lights, blender
    "16i"  # color-combiner settings
    "i i i i"  # geoMode, other-low, other-high, flags
    "4f 4f 4f 4f"  # prim, prim_lod, prim-depth, env, ambient
    "3f f 3f i 3f i"  # ck center, alpha clip, ck scale, light count, width, mipmap count
    "6f 2i"  # k0-k5, tex size
)
# version of the uniform buffer with all ints
UNIFORM_BUFFER_MASK_STRUCT = struct.Struct(UNIFORM_BUFFER_STRUCT.format.replace("f", "I").replace("i", "I"))

F64Color = tuple[float, float, float, float]


@dataclass
class F64Rendermode:
    blender: tuple[int, int, int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0, 0, 0)
    flags: int = 0
    blend: str = "NONE"
    depth_test: str = "LESS_EQUAL"
    depth_write: bool = True
    alpha_clip: float = -1


@dataclass
class F64Light:
    color: F64Color = (0, 0, 0, 0)
    direction: tuple[float, float, float] | None = None


@dataclass
class F64RenderState:
    tex_confs: list[F64Texture | None] = None
    lights: list[F64Light | None] = None
    ambient_color: F64Color | None = None
    light_count: int | None = None
    prim_color: F64Color | None = None
    prim_lod: tuple[float, float] | None = None
    env_color: F64Color | None = None
    ck: tuple[float, float, float, float, float, float, float, float] | None = None
    convert: tuple[float, float, float, float, float, float] | None = None
    cc: tuple[
        float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float
    ] | None = None
    render_mode: F64Rendermode | None = None
    flags: int = 0
    geo_mode: int = 0
    othermode_l: int = 0
    othermode_h: int = 0
    prim_depth: tuple[float, float] = None
    tex_size: tuple[int, int] = None
    mip_count: int = None

    cached_values: np.ndarray | None = None
    cached_mask: np.ndarray | None = None

    def __post_init__(self):
        if self.lights is None:
            self.lights = [None] * 8
        if self.tex_confs is None:
            self.tex_confs = [None] * 8

    def save_cache(self):
        self.cached_values = self.np_array(False)
        self.cached_mask = self.np_array(True)

    def np_array(self, make_mask: bool = False):
        if make_mask:

            def mask(value: None | object, size: int = 1, mask_value: int = 0xFFFFFFFF):
                return (mask_value if value is None else 0,) * size

            def mask_single(value: None | object, mask_value: int = 0xFFFFFFFF):
                return mask_value if value is None else 0

            ubo_struct = UNIFORM_BUFFER_MASK_STRUCT
        else:

            def mask(value: None | object, size: int = 1, _mask_value=0):
                if value is None:
                    return (0,) * size
                return value

            def mask_single(value: None | object, _mask_value=0):
                return 0 if value is None else value

            ubo_struct = UNIFORM_BUFFER_STRUCT

        light_data = []
        for l in self.lights:
            if l is None:
                light_data.extend(mask(None, 7))
            else:
                light_data.extend(mask(l.color, 4))
                light_data.extend(mask(l.direction, 3))
        tex_data = []
        for t in self.tex_confs:
            if t is None:
                tex_data.extend(mask(None, 9))
            else:
                tex_data.extend(mask(t.values, 9))

        blender, alpha_clip, flags = None, -1, self.flags
        if self.render_mode is not None:
            blender = self.render_mode.blender
            alpha_clip = self.render_mode.alpha_clip
            flags |= self.render_mode.flags

        ck = self.ck
        if ck is None:
            ck = (0,) * 9

        return np.frombuffer(
            ubo_struct.pack(
                *tex_data,
                *light_data,
                *mask(blender, 8),
                *mask(self.cc, 16),
                mask_single(self.geo_mode),
                mask_single(self.othermode_l),
                mask_single(self.othermode_h),
                mask_single(flags),
                *mask(self.prim_color, 4),
                *mask(self.prim_lod, 2),
                *mask(self.prim_depth, 2),
                *mask(self.env_color, 4),
                *mask(self.ambient_color, 4),
                *mask(ck[:3], 3),
                mask_single(alpha_clip),
                *mask(ck[3:6], 3),
                mask_single(self.light_count),
                *mask(ck[6:9], 3),
                mask_single(self.mip_count),
                *mask(self.convert, 6),
                *mask(self.tex_size, 2),
            ),
            dtype=np.uint64,
        )

    def set_values_from_cache(self, other: "F64RenderState"):
        assert self.cached_values is not None
        assert other.cached_mask is not None
        assert other.cached_values is not None
        self.cached_values = (self.cached_values & other.cached_mask) | other.cached_values
        for i, other_conf in enumerate(other.tex_confs):
            if other_conf is not None:
                self.tex_confs[i] = other_conf
        if other.render_mode is not None:
            self.render_mode = other.render_mode

    def copy(self):
        new = copy.copy(self)
        new.cached_values = new.cached_values.copy()
        return new

    def set_from_rendermode(self, rendermode: RenderMode):
        self.render_mode = F64Rendermode(
            blender=rendermode.blend_cycle1 + rendermode.blend_cycle2, depth_write=rendermode.z_upd
        )
        if rendermode.zmode == "ZMODE_DEC":
            self.render_mode.depth_test = "EQUAL"
            self.render_mode.flags |= pydefines.DRAW_FLAG_DECAL
        if rendermode.cvg_x_alpha:
            self.render_mode.alpha_clip = 0.49
        else:
            self.render_mode.alpha_clip = -1
        if rendermode.force_bl and rendermode.blend_cycle2 == (
            pydefines.BLENDER_CLR_IN,
            pydefines.BLENDER_A_IN,
            pydefines.BLENDER_CLR_MEM,
            pydefines.BLENDER_1MA,
        ):
            self.render_mode.blend = "ALPHA"
            self.render_mode.flags |= pydefines.DRAW_FLAG_ALPHA_BLEND


@dataclass
class F64Material:
    state: F64RenderState = dataclasses.field(default_factory=F64RenderState)
    cull: str = "NONE"
    layer: int | str | None = None


def quantize_direction(direction):
    return tuple(quantize(x, 8, -1, 1) for x in direction)


# copied from fast64
def getObjDirectionVec(obj, toExport: bool):
    rotation = getObjectQuaternion(obj)
    if toExport:
        spaceRot = mathutils.Euler((-pi / 2, 0, 0)).to_quaternion()
        rotation = spaceRot @ rotation
    normal = (rotation @ mathutils.Vector((0, 0, 1))).normalized()
    return normal


def f64_parse_obj_light(f64_light: F64Light, obj: bpy.types.Object, set_light_dir: bool):
    f64_light.color = quantize_srgb(obj.data.color, force_alpha=True)
    if set_light_dir:
        f64_light.direction = quantize_direction(getObjDirectionVec(obj, False))
    else:
        f64_light.direction = None


DEFAULT_LIGHT_DIR = quantize_direction(mathutils.Vector((0x49, 0x49, 0x49)).normalized())


def f64_material_parse(f3d_mat: "DragExMaterialProperties", always_set: bool, set_light_dir: bool) -> F64Material:
    print("f64_material_parse")

    state = F64RenderState()
    f64mat = F64Material(state=state)

    state.tex_size = (f3d_mat.uv_basis_s, f3d_mat.uv_basis_t)

    for i, tile in enumerate(f3d_mat.tiles.tiles):
        f64mat.state.tex_confs[i] = get_tile_conf(tile)

    state.cc = get_cc_settings(f3d_mat)
    state.prim_color = quantize_srgb(f3d_mat.vals.primitive_color)
    state.prim_lod = (f3d_mat.vals.prim_lod_frac / 255, f3d_mat.vals.min_level / 255)
    state.env_color = quantize_srgb(f3d_mat.vals.environment_color)
    state.prim_depth = (f3d_mat.vals.primitive_depth_z, f3d_mat.vals.primitive_depth_dz)

    state.set_from_rendermode(parse_f3d_mat_rendermode(f3d_mat))

    geo_mode = pydefines.G_SHADE | pydefines.G_SHADE_SMOOTH
    if f3d_mat.geometry_mode.lighting:
        geo_mode |= pydefines.G_LIGHTING
    state.geo_mode = geo_mode

    othermode_l = 0

    if f3d_mat.other_modes.alpha_compare_en:
        if f3d_mat.other_modes.dither_alpha_en:
            othermode_l |= pydefines.G_AC_DITHER
        else:
            othermode_l |= pydefines.G_AC_THRESHOLD
    else:
        othermode_l |= pydefines.G_AC_NONE

    if f3d_mat.other_modes.z_source_sel:
        othermode_l |= pydefines.G_ZS_PRIM
    else:
        othermode_l |= pydefines.G_ZS_PIXEL

    state.othermode_l = othermode_l

    othermode_h = 0

    othermode_h |= {
        "SAME_AS_RGB": pydefines.G_AD_PATTERN,
        "INVERSE_OF_RGB": pydefines.G_AD_NOTPATTERN,
        "RANDOM_NOISE": pydefines.G_AD_NOISE,
        "NONE": pydefines.G_AD_DISABLE,
    }[f3d_mat.other_modes.alpha_dither_sel]

    othermode_h |= {
        "MAGIC_SQUARE": pydefines.G_CD_MAGICSQ,
        "BAYER": pydefines.G_CD_BAYER,
        "RANDOM_NOISE": pydefines.G_CD_NOISE,
        "NONE": pydefines.G_CD_DISABLE,
    }[f3d_mat.other_modes.rgb_dither_sel]

    othermode_h |= pydefines.G_CK_KEY if f3d_mat.other_modes.key_en else pydefines.G_CK_NONE

    """
    f3d_mat.other_modes.bi_lerp_0    # 4
    f3d_mat.other_modes.bi_lerp_1    # 2
    f3d_mat.other_modes.convert_one  # 1
    pydefines.G_TC_CONV     # 0
    pydefines.G_TC_FILTCONV # 5 = bi_lerp_0 | convert_one
    pydefines.G_TC_FILT     # 6 = bi_lerp_0 | bi_lerp_1
    """
    # this is approximate but the shader doesn't use this anyway
    if f3d_mat.other_modes.bi_lerp_0 and f3d_mat.other_modes.bi_lerp_1:
        othermode_h |= pydefines.G_TC_FILT
    elif f3d_mat.other_modes.bi_lerp_0 and f3d_mat.other_modes.convert_one:
        othermode_h |= pydefines.G_TC_FILTCONV
    else:
        othermode_h |= pydefines.G_TC_CONV

    if f3d_mat.other_modes.sample_type:
        if f3d_mat.other_modes.mid_texel:
            othermode_h |= pydefines.G_TF_AVERAGE
        else:
            othermode_h |= pydefines.G_TF_BILERP
    else:
        othermode_h |= pydefines.G_TF_POINT

    othermode_h |= pydefines.G_TL_LOD if f3d_mat.other_modes.tex_lod_en else pydefines.G_TL_TILE

    # Note: having both detail and sharpen at once is invalid
    # N64brew discord: https://discord.com/channels/205520502922543113/205520502922543113/1392399686819774575
    if f3d_mat.other_modes.detail_tex_en:
        othermode_h |= pydefines.G_TD_DETAIL
    elif f3d_mat.other_modes.sharpen_tex_en:
        othermode_h |= pydefines.G_TD_SHARPEN
    else:
        othermode_h |= pydefines.G_TD_CLAMP

    othermode_h |= pydefines.G_TP_PERSP if f3d_mat.other_modes.persp_tex_en else pydefines.G_TP_NONE

    othermode_h |= {
        "1CYCLE": pydefines.G_CYC_1CYCLE,
        "2CYCLE": pydefines.G_CYC_2CYCLE,
        "COPY": pydefines.G_CYC_COPY,
        "FILL": pydefines.G_CYC_FILL,
    }[f3d_mat.other_modes.cycle_type]

    othermode_h |= pydefines.G_PM_1PRIMITIVE if f3d_mat.other_modes.atomic_prim else pydefines.G_PM_NPRIMITIVE

    if f3d_mat.other_modes.tlut_en:
        if f3d_mat.other_modes.tlut_type:
            othermode_h |= pydefines.G_TT_IA16
        else:
            othermode_h |= pydefines.G_TT_RGBA16
    else:
        othermode_h |= pydefines.G_TT_NONE

    if f3d_mat.other_modes.cycle_type == "COPY":
        othermode_h &= ~(pydefines.G_TF_BILERP | pydefines.G_TF_AVERAGE)

    state.othermode_h = othermode_h

    # TODO-tmp_porting

    state.save_cache()

    return f64mat

    from fast64_internal.f3d.f3d_material import all_combiner_uses
    from fast64_internal.f3d.f3d_writer import lightDataToObj

    cc_uses = all_combiner_uses(f3d_mat)
    rdp = f3d_mat.rdp_settings

    state = F64RenderState()  # None equals not set
    f64mat = F64Material(state=state)
    if always_set or rdp.set_rendermode:
        state.set_from_rendermode(parse_f3d_mat_rendermode(f3d_mat))
    if always_set or f3d_mat.set_combiner:
        state.cc = get_cc_settings(f3d_mat)
    if always_set or (f3d_mat.set_prim and cc_uses["Primitive"]):
        state.prim_color = quantize_srgb(f3d_mat.prim_color)
        state.prim_lod = (f3d_mat.prim_lod_frac, f3d_mat.prim_lod_min)
    if always_set or (f3d_mat.set_env and cc_uses["Environment"]):
        state.env_color = quantize_srgb(f3d_mat.env_color)
    if always_set or (f3d_mat.set_key and cc_uses["Key"]):  # extra 0 for alignment
        state.ck = tuple((*quantize_srgb(f3d_mat.key_center, False), *f3d_mat.key_scale, *f3d_mat.key_width))
    if always_set or (f3d_mat.set_k0_5 and cc_uses["Convert"]):
        state.convert = tuple(getattr(f3d_mat, f"k{i}") for i in range(0, 6))
    if always_set or (cc_uses["Shade"] and rdp.g_lighting and f3d_mat.set_lights):
        state.ambient_color = quantize_srgb(f3d_mat.ambient_light_color, force_alpha=True)
        if f3d_mat.use_default_lighting:
            state.light_count = 1
            state.lights[0] = F64Light(quantize_srgb(f3d_mat.default_light_color, force_alpha=True))
            if set_light_dir:
                state.lights[0].direction = DEFAULT_LIGHT_DIR
        else:
            light_index = 0
            for i in range(0, 7):
                light_data = getattr(f3d_mat, f"f3d_light{i + 1}", None)
                if light_data is None:
                    continue
                obj = lightDataToObj(light_data.original)
                f64_light = state.lights[light_index] = F64_GLOBALS.obj_lights.setdefault(obj.name, F64Light())
                f64_parse_obj_light(f64_light, obj, set_light_dir)
                light_index += 1
            state.light_count = light_index

    if rdp.g_cull_back:
        f64mat.cull = "BACK"
    if rdp.g_cull_front:
        f64mat.cull = "BOTH" if f64mat.cull == "BACK" else "FRONT"

    use_tex0, use_tex1 = f3d_mat.tex0.tex_set and cc_uses["Texture 0"], f3d_mat.tex1.tex_set and cc_uses["Texture 1"]
    if use_tex0:
        state.tex_confs[0] = get_tile_conf(f3d_mat.tex0)
    if use_tex1:
        state.tex_confs[1] = get_tile_conf(f3d_mat.tex1)
    # TODO: use check for multitex function in glTF pr?

    uv_basis = None
    if use_tex0 and use_tex1:
        uv_basis = int(f3d_mat.uv_basis.removeprefix("TEXEL"))
    elif use_tex0 or use_tex1:
        uv_basis = 0 if use_tex0 else 1
    if uv_basis is not None:
        state.tex_size = tuple(getattr(f3d_mat, f"tex{uv_basis}").get_tex_size())

    if cc_uses["Texture 0"] and cc_uses["Texture 1"]:
        f64mat.mip_count = f3d_mat.rdp_settings.num_textures_mipmapped - 1
    state.prim_depth = (rdp.prim_depth.z, rdp.prim_depth.dz)

    from fast64_internal.f3d.f3d_gbi import get_F3D_GBI
    from fast64_internal.f3d.f3d_material import get_textlut_mode

    gbi = get_F3D_GBI()
    geo_mode = othermode_l = othermode_h = 0
    # TODO: use geo_modes_in_ucode (T3D UI pr) to check if the geo mode exists in the current ucode
    for i, attr in enumerate(GEO_MODE_ATTRS):
        if not getattr(
            gbi, attr.upper().replace("G_TEX_GEN", "G_TEXTURE_GEN").replace("G_SHADE_SMOOTH", "G_SHADING_SMOOTH"), False
        ):
            continue
        geo_mode |= int(getattr(rdp, attr)) << i
    for i, attr in enumerate(OTHERMODE_L_ATTRS):
        othermode_l |= getattr(gbi, getattr(rdp, attr))
    for i, attr in enumerate(OTHERMODE_H_ATTRS):
        othermode_h |= getattr(gbi, getattr(rdp, attr))
    if rdp.g_mdsft_cycletype == "G_CYC_COPY":
        othermode_h ^= gbi.G_TF_BILERP | gbi.G_TF_AVERAGE
    othermode_h |= getattr(gbi, get_textlut_mode(f3d_mat))
    state.geo_mode, state.othermode_l, state.othermode_h = geo_mode, othermode_l, othermode_h
    state.save_cache()

    game_mode = bpy.context.scene.gameEditorMode
    f64mat.layer = getattr(f3d_mat.draw_layer, game_mode.lower(), None)

    return f64mat


# parses a non-f3d material for the fallback renderer
def node_material_parse(mat: bpy.types.Material) -> F64Material:
    # TODO: If bsdf to f3d gets merged into fast, consider using that?
    color = None
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            color = quantize_srgb(bsdf.inputs["Base Color"].default_value)

    state = F64RenderState(prim_color=color, cc=SOLID_CC)
    state.save_cache()
    return F64Material(state)
