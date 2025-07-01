import dragex_backend


def register():
    print("Hi from", __package__)
    print(dragex_backend.get_value())


def unregister():
    print("Bye from", __package__)
