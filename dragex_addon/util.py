import os

import numpy as np

import mathutils


transform_zup_to_yup = mathutils.Matrix(
    (
        (1, 0, 0),
        (0, 0, 1),
        (0, -1, 0),
    )
).freeze()


def new_float_buf(len):
    return np.empty(
        shape=len,
        dtype=np.float32,
        order="C",
    )


def new_uint_buf(len):
    return np.empty(
        shape=len,
        dtype=np.uint32,  # np.uint leads to L format (unsigned long)
        order="C",
    )


C_IDENTIFIER_ALLOWED = frozenset(
    "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_" "0123456789"
)
C_IDENTIFIER_START_ALLOWED = frozenset(
    "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_"
)


def make_c_identifier(s: str):
    if s == "":
        return "_"
    s = "".join(c if c in C_IDENTIFIER_ALLOWED else "_" for c in s)
    if s[0] not in C_IDENTIFIER_START_ALLOWED:
        s = "_" + s
    return s


class FDManager:
    def __init__(self):
        self.fds = list[int]()
        self.entered = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.entered = False
        for fd in self.fds:
            os.close(fd)

    def open_w(self, p: os.PathLike):
        fd = os.open(p, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
        self.fds.append(fd)
        return fd
