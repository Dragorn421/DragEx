import typing

import dragex_backend

if typing.TYPE_CHECKING:
    #from ..dragex_backend.dragex_backend import dragex_backend
    pass


def register():
    print("Hi from", __package__)
    print(dragex_backend.get_value())


def unregister():
    print("Bye from", __package__)
