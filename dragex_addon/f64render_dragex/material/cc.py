from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import bpy

from . import pydefines

if TYPE_CHECKING:
    from ... import DragExMaterialProperties


CC1_C = {
    "0": pydefines.CC_C_0,
    "1": pydefines.CC_C_1,
    "COMBINED": pydefines.CC_C_COMB,
    "TEXEL0": pydefines.CC_C_TEX0,
    "TEXEL1": pydefines.CC_C_TEX1,
    "PRIMITIVE": pydefines.CC_C_PRIM,
    "SHADE": pydefines.CC_C_SHADE,
    "ENVIRONMENT": pydefines.CC_C_ENV,
    "CENTER": pydefines.CC_C_CENTER,
    "SCALE": pydefines.CC_C_SCALE,
    "COMBINED_ALPHA": pydefines.CC_C_COMB_ALPHA,
    "TEXEL0_ALPHA": pydefines.CC_C_TEX0_ALPHA,
    "TEXEL1_ALPHA": pydefines.CC_C_TEX1_ALPHA,
    "PRIMITIVE_ALPHA": pydefines.CC_C_PRIM_ALPHA,
    "SHADE_ALPHA": pydefines.CC_C_SHADE_ALPHA,
    "ENV_ALPHA": pydefines.CC_C_ENV_ALPHA,
    "LOD_FRACTION": pydefines.CC_C_LOD_FRAC,
    "PRIM_LOD_FRAC": pydefines.CC_C_PRIM_LOD_FRAC,
    "NOISE": pydefines.CC_C_NOISE,
    "K4": pydefines.CC_C_K4,
    "K5": pydefines.CC_C_K5,
}

CC2_C = {  # TEX0 and TEX1 are swapped
    "0": pydefines.CC_C_0,
    "1": pydefines.CC_C_1,
    "COMBINED": pydefines.CC_C_COMB,
    "TEXEL1": pydefines.CC_C_TEX0,
    "TEXEL0": pydefines.CC_C_TEX1,
    "PRIMITIVE": pydefines.CC_C_PRIM,
    "SHADE": pydefines.CC_C_SHADE,
    "ENVIRONMENT": pydefines.CC_C_ENV,
    "CENTER": pydefines.CC_C_CENTER,
    "SCALE": pydefines.CC_C_SCALE,
    "COMBINED_ALPHA": pydefines.CC_C_COMB_ALPHA,
    "TEXEL1_ALPHA": pydefines.CC_C_TEX0_ALPHA,
    "TEXEL0_ALPHA": pydefines.CC_C_TEX1_ALPHA,
    "PRIMITIVE_ALPHA": pydefines.CC_C_PRIM_ALPHA,
    "SHADE_ALPHA": pydefines.CC_C_SHADE_ALPHA,
    "ENV_ALPHA": pydefines.CC_C_ENV_ALPHA,
    "LOD_FRACTION": pydefines.CC_C_LOD_FRAC,
    "PRIM_LOD_FRAC": pydefines.CC_C_PRIM_LOD_FRAC,
    "NOISE": pydefines.CC_C_NOISE,
    "K4": pydefines.CC_C_K4,
    "K5": pydefines.CC_C_K5,
}

CC1_A = {
    "0": pydefines.CC_A_0,
    "1": pydefines.CC_A_1,
    "COMBINED": pydefines.CC_A_COMB,
    "TEXEL0": pydefines.CC_A_TEX0,
    "TEXEL1": pydefines.CC_A_TEX1,
    "PRIMITIVE": pydefines.CC_A_PRIM,
    "SHADE": pydefines.CC_A_SHADE,
    "ENVIRONMENT": pydefines.CC_A_ENV,
    "LOD_FRACTION": pydefines.CC_A_LOD_FRAC,
    "PRIM_LOD_FRAC": pydefines.CC_A_PRIM_LOD_FRAC,
}

CC2_A = {  # TEX0 and TEX1 are swapped
    "0": pydefines.CC_A_0,
    "1": pydefines.CC_A_1,
    "COMBINED": pydefines.CC_A_COMB,
    "TEXEL1": pydefines.CC_A_TEX0,
    "TEXEL0": pydefines.CC_A_TEX1,
    "PRIMITIVE": pydefines.CC_A_PRIM,
    "SHADE": pydefines.CC_A_SHADE,
    "ENVIRONMENT": pydefines.CC_A_ENV,
    "LOD_FRACTION": pydefines.CC_A_LOD_FRAC,
    "PRIM_LOD_FRAC": pydefines.CC_A_PRIM_LOD_FRAC,
}

SOLID_CC = (
    (pydefines.CC_C_0, pydefines.CC_C_0, pydefines.CC_C_0, pydefines.CC_C_PRIM)
    + (pydefines.CC_A_0, pydefines.CC_A_0, pydefines.CC_A_0, pydefines.CC_A_PRIM)
    + (pydefines.CC_C_0, pydefines.CC_C_0, pydefines.CC_C_0, pydefines.CC_C_PRIM)
    + (pydefines.CC_A_0, pydefines.CC_A_0, pydefines.CC_A_0, pydefines.CC_A_PRIM)
)


# Fetches CC settings from a given fast64-material
def get_cc_settings(f3d_mat: "DragExMaterialProperties") -> np.ndarray:
    c0 = f3d_mat.quickanddirty.combiner1
    c1 = f3d_mat.quickanddirty.combiner2

    if f3d_mat.other_modes.cycle_type == "1CYCLE":
        # Note: this is the opposite of what the RDP does which is ignore c0 and read c1 in 1-cycle mode
        # https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x3C_-_Set_Combine_Mode
        # > In 1-Cycle mode only the second cycle configuration is used, the first cycle configuration is ignored.
        # Also note: this is useless as the shader ignores c1 in 1-cycle mode
        c1 = c0

    return np.array(
        [
            CC1_C[c0.A],
            CC1_C[c0.B],
            CC1_C[c0.C],
            CC1_C[c0.D],
            CC1_A[c0.A_alpha],
            CC1_A[c0.B_alpha],
            CC1_A[c0.C_alpha],
            CC1_A[c0.D_alpha],
            CC2_C[c1.A],
            CC2_C[c1.B],
            CC2_C[c1.C],
            CC2_C[c1.D],
            CC2_A[c1.A_alpha],
            CC2_A[c1.B_alpha],
            CC2_A[c1.C_alpha],
            CC2_A[c1.D_alpha],
        ],
        dtype=np.int32,
    )
