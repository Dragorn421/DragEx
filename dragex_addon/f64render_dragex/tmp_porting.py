useWorldSpaceLighting = True
ambientColor = (1, 1, 1, 1)
light0Color = (0, 0, 0, 1)
light0Direction = (1, 0, 0)
light1Color = (0, 0, 0, 1)
light1Direction = (1, 0, 0)
f3d_type = "f3dex2"
gameEditorMode = "_"


def is_dragex_material(mat):
    return mat.dragex.mode != "NONE"
