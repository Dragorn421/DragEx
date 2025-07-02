import dragex_backend

fbt = dragex_backend.FloatBufferThing(3, 421.421421421421)
print(fbt)
print(memoryview(fbt))
print(memoryview(fbt)[0])
print(bytes(fbt))
print(len(bytes(memoryview(fbt))))

fbt.__init__(2, 42)
print(memoryview(fbt)[0])
print(bytes(memoryview(fbt)))
print(len(bytes(memoryview(fbt))))
