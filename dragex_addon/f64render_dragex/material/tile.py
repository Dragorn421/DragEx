from typing import TYPE_CHECKING

import bpy
import gpu

from dataclasses import dataclass
import numpy as np

from . import pydefines

if TYPE_CHECKING:
    from ... import DragExMaterialTileProperties
    from ..properties import TextureProperty


@dataclass
class F64Texture:
    values: tuple[float, float, float, float, float, float, float, float, int]
    buff: gpu.types.GPUTexture


def get_tile_conf(tex: "DragExMaterialTileProperties") -> F64Texture:
    flags = 0
    if tex.image is not None:
        # Note: doing 'gpu.texture.from_image' seems to cost nothing, caching is not needed
        buff = gpu.texture.from_image(tex.image)
        tex_format = tex.format + tex.size
        if tex_format in {"I4", "I8"}:
            flags |= pydefines.TEX_FLAG_MONO
        if tex_format in {"I4", "IA8"}:
            flags |= pydefines.TEX_FLAG_4BIT
        if tex_format == "IA4":
            flags |= pydefines.TEX_FLAG_3BIT
    else:
        buff = gpu.texture.from_image(bpy.data.images["f64render_missing_texture"])
        flags |= pydefines.TEX_FLAG_MONO

    def get_shift(n: int):
        if not (0 <= n <= 15):
            return 0  # TODO
        if n <= 10:
            return n
        else:
            return n - 16

    conf = np.array(
        [
            tex.mask_S,
            tex.mask_T,
            get_shift(tex.shift_S),
            get_shift(tex.shift_T),
            # TODO not sure if low/high corresponds to ul/lr respectively, seems to?
            tex.upper_left_S,  # tex.S.low
            -tex.upper_left_T,  # -tex.T.low
            tex.lower_right_S,  # tex.S.high
            tex.lower_right_T,  # tex.T.high
        ],
        dtype=np.float32,
    )

    conf[0:4] = 2 ** conf[0:4]  # mask/shift are exponents, calc. 2^x
    conf[2:4] = 1 / conf[2:4]  # shift is inverted

    # quantize the low/high values into 0.25 pixel increments
    conf[4:] = np.round(conf[4:] * 4) / 4

    # if clamp is on, negate the mask value
    if tex.clamp_S:
        conf[0] = -conf[0]
    if tex.clamp_T:
        conf[1] = -conf[1]

    # if mirror is on, negate the high value
    if tex.mirror_S:
        conf[6] = -conf[6]
    if tex.mirror_T:
        conf[7] = -conf[7]

    return F64Texture((*conf, flags), buff)


def get_tile_conf_from_default(tex: "TextureProperty") -> F64Texture:
    flags = 0
    if tex.image is not None:
        # Note: doing 'gpu.texture.from_image' seems to cost nothing, caching is not needed
        buff = gpu.texture.from_image(tex.image)
        if tex.tex_format in {"I4", "I8"}:
            flags |= pydefines.TEX_FLAG_MONO
        if tex.tex_format in {"I4", "IA8"}:
            flags |= pydefines.TEX_FLAG_4BIT
        if tex.tex_format == "IA4":
            flags |= pydefines.TEX_FLAG_3BIT
    else:
        buff = gpu.texture.from_image(bpy.data.images["f64render_missing_texture"])
        flags |= pydefines.TEX_FLAG_MONO

    conf = np.array(
        [
            tex.S.mask,
            tex.T.mask,
            tex.S.shift,
            tex.T.shift,
            tex.S.low,
            -tex.T.low,
            tex.S.high,
            tex.T.high,
        ],
        dtype=np.float32,
    )

    conf[0:4] = 2 ** conf[0:4]  # mask/shift are exponents, calc. 2^x
    conf[2:4] = 1 / conf[2:4]  # shift is inverted

    # quantize the low/high values into 0.25 pixel increments
    conf[4:] = np.round(conf[4:] * 4) / 4

    # if clamp is on, negate the mask value
    if tex.S.clamp:
        conf[0] = -conf[0]
    if tex.T.clamp:
        conf[1] = -conf[1]

    # if mirror is on, negate the high value
    if tex.S.mirror:
        conf[6] = -conf[6]
    if tex.T.mirror:
        conf[7] = -conf[7]

    return F64Texture((*conf, flags), buff)
