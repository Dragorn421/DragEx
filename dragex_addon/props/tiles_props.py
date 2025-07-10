from typing import Sequence

import bpy


tile_format_items = (
    ("RGBA", "RGBA", "RGBA"),
    ("YUV", "YUV", "YUV"),
    ("CI", "CI", "Color-Indexed (CI)"),
    ("IA", "IA", "Intensity-Alpha (IA)"),
    ("I", "I", "Intensity (I)"),
)

tile_size_items = (
    ("4", "4", "4"),
    ("8", "8", "8"),
    ("16", "16", "16"),
    ("32", "32", "32"),
)


# https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x35_-_Set_Tile
# and https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x32_-_Set_Tile_Size
# TODO improve names/descriptions
class DragExMaterialTileProperties(bpy.types.PropertyGroup):
    image: bpy.props.PointerProperty(
        name="Image",
        description="Tile data to be loaded",
        type=bpy.types.Image,
    )

    format: bpy.props.EnumProperty(
        name="format",
        description="Tile texel format",
        items=tile_format_items,
    )
    size: bpy.props.EnumProperty(
        name="size",
        description="Tile texel size",
        items=tile_size_items,
    )
    line: bpy.props.IntProperty(
        name="line",
        description="Tile line length in TMEM words",
    )
    address: bpy.props.IntProperty(
        name="address",
        description="TMEM address in TMEM words",
    )
    palette: bpy.props.IntProperty(
        name="palette",
        description="Palette index",
    )
    clamp_T: bpy.props.BoolProperty(
        name="clamp_T",
        description="Clamp enable (T-axis)",
    )
    mirror_T: bpy.props.BoolProperty(
        name="mirror_T",
        description="Mirror enable (T-axis)",
    )
    mask_T: bpy.props.IntProperty(
        name="mask_T",
        description="Mask (T-axis)",
    )
    shift_T: bpy.props.IntProperty(
        name="shift_T",
        description="Shift (T-axis)",
    )
    clamp_S: bpy.props.BoolProperty(
        name="clamp_S",
        description="Clamp enable (S-axis)",
    )
    mirror_S: bpy.props.BoolProperty(
        name="mirror_S",
        description="Mirror enable (S-axis)",
    )
    mask_S: bpy.props.IntProperty(
        name="mask_S",
        description="Mask (S-axis)",
    )
    shift_S: bpy.props.IntProperty(
        name="shift_S",
        description="Shift (S-axis)",
    )

    upper_left_S: bpy.props.FloatProperty(
        name="upper_left_S",
        description="Upper-left s coordinate (u10.2 format)",
    )
    upper_left_T: bpy.props.FloatProperty(
        name="upper_left_T",
        description="Upper-left t coordinate (u10.2 format)",
    )
    lower_right_S: bpy.props.FloatProperty(
        name="lower_right_S",
        description="Lower-right s coordinate (u10.2 format)",
    )
    lower_right_T: bpy.props.FloatProperty(
        name="lower_right_T",
        description="Lower-right t coordinate (u10.2 format)",
    )


class DragExMaterialTilesProperties(bpy.types.PropertyGroup):
    tile_0: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_1: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_2: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_3: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_4: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_5: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_6: bpy.props.PointerProperty(type=DragExMaterialTileProperties)
    tile_7: bpy.props.PointerProperty(type=DragExMaterialTileProperties)

    @property
    def tiles(self) -> Sequence[DragExMaterialTileProperties]:
        return (
            self.tile_0,
            self.tile_1,
            self.tile_2,
            self.tile_3,
            self.tile_4,
            self.tile_5,
            self.tile_6,
            self.tile_7,
        )
