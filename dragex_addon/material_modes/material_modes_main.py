import bpy

from . import material_modes_defs
from . import material_mode_basic
from . import material_mode_multitexture
from . import material_mode_full


class NoneMaterialMode(material_modes_defs.MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        pass

    @staticmethod
    def draw(layout, material):
        pass


class DragExMaterialModesProperties(bpy.types.PropertyGroup):
    basic_: bpy.props.PointerProperty(
        type=material_mode_basic.DragExMaterialModesBasicProperties
    )

    @property
    def basic(self) -> material_mode_basic.DragExMaterialModesBasicProperties:
        return self.basic_

    multitexture_: bpy.props.PointerProperty(
        type=material_mode_multitexture.DragExMaterialModesMultitextureProperties
    )

    @property
    def multitexture(
        self,
    ) -> material_mode_multitexture.DragExMaterialModesMultitextureProperties:
        return self.multitexture_


material_modes_dict: dict[str, type[material_modes_defs.MaterialMode]] = {
    "NONE": NoneMaterialMode,
    "BASIC": material_mode_basic.BasicMaterialMode,
    "MULTITEXTURE": material_mode_multitexture.MultitextureMaterialMode,
    "FULL": material_mode_full.FullMaterialMode,
}

material_mode_items = (
    # TODO add descriptions
    ("NONE", "None", "", 1),
    ("BASIC", "Basic", "", 2),
    ("MULTITEXTURE", "Multitexture", "", 3),
    ("FULL", "Full", "", 0),
)
