from typing import TYPE_CHECKING

import bpy

from . import util

if TYPE_CHECKING:
    from .props import tiles_props


SHADER_NODE_TEX_IMAGE_NAME = "DragEx for face texture selection"


# This function ensures there is an active texture image shader node with the current
# material's image in the material's nodes.  This makes "face texture selection" work,
# the feature that switches the image in the UV editor based on the currently active
# face in edit mode.
def on_update_rdp_tile_image(self, context: bpy.types.Context):
    mat = self.id_data
    assert isinstance(mat, bpy.types.Material)

    image = None
    mat_dragex = util.DRAGEX(mat)
    for i in range(8):
        tile = getattr(mat_dragex.rdp.tiles, f"tile_{i}")
        tile: "tiles_props.DragExMaterialTileProperties"
        if tile.image is not None:
            image = tile.image
            break

    if mat.node_tree is None:
        mat.node_tree = bpy.data.node_groups.new(mat.name, "ShaderNodeTree")  # type: ignore
    assert mat.node_tree is not None
    node = mat.node_tree.nodes.get(SHADER_NODE_TEX_IMAGE_NAME)
    if node is not None and not isinstance(node, bpy.types.ShaderNodeTexImage):
        node.name = "_" + SHADER_NODE_TEX_IMAGE_NAME
        node = None
    if node is None:
        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        assert isinstance(node, bpy.types.ShaderNodeTexImage)
        node.name = SHADER_NODE_TEX_IMAGE_NAME
    node.image = image
    mat.node_tree.nodes.active = node
