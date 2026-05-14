import abc
import math

import bpy


def intlog2(v: int):
    r = round(math.log2(v))
    if 2**r == v:
        return r
    else:
        return None


TMEM_SIZE = 4096


class MaterialMode(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def init(material: bpy.types.Material, prev_mode: str) -> None: ...

    @staticmethod
    @abc.abstractmethod
    def draw(layout: bpy.types.UILayout, material: bpy.types.Material) -> None: ...


def encode_shift(v: int):
    assert -5 <= v <= 10
    return v if v >= 0 else v + 16
