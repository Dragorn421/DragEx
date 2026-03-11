import datetime
import os
from pathlib import Path
from typing import TYPE_CHECKING

import bpy

from .build_id import BUILD_ID
from . import material_modes
from .oot import oot_ops
from .oot import oot_panels
from .oot import oot_props
from .props import other_mode_props
from .props import tiles_props
from .props import combiner_props
from .props import vals_props
from .props import rsp_props
from . import util

if TYPE_CHECKING:
    from ..dragex_backend import dragex_backend
else:
    try:
        import dragex_backend
    except ModuleNotFoundError:
        dragex_backend = None


class DragExMaterialRDPProperties(bpy.types.PropertyGroup):
    other_modes_: bpy.props.PointerProperty(
        type=other_mode_props.DragExMaterialOtherModesProperties
    )
    tiles_: bpy.props.PointerProperty(type=tiles_props.DragExMaterialTilesProperties)
    combiner_: bpy.props.PointerProperty(
        type=combiner_props.DragExMaterialCombinerProperties
    )
    vals_: bpy.props.PointerProperty(type=vals_props.DragExMaterialValsProperties)

    @property
    def other_modes(self) -> other_mode_props.DragExMaterialOtherModesProperties:
        return self.other_modes_

    @property
    def tiles(self) -> tiles_props.DragExMaterialTilesProperties:
        return self.tiles_

    @property
    def combiner(self) -> combiner_props.DragExMaterialCombinerProperties:
        return self.combiner_

    @property
    def vals(self) -> vals_props.DragExMaterialValsProperties:
        return self.vals_


class DragExMaterialProperties(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(
        items=material_modes.material_mode_items,
        default="NONE",
    )
    modes_: bpy.props.PointerProperty(type=material_modes.DragExMaterialModesProperties)

    @property
    def modes(self) -> material_modes.DragExMaterialModesProperties:
        return self.modes_

    uv_basis_s: bpy.props.IntProperty(name="UV Basis S", min=1, default=1)
    uv_basis_t: bpy.props.IntProperty(name="UV Basis T", min=1, default=1)

    rdp_: bpy.props.PointerProperty(type=DragExMaterialRDPProperties)

    rsp_: bpy.props.PointerProperty(type=rsp_props.DragExMaterialRSPProperties)

    @property
    def rdp(self) -> DragExMaterialRDPProperties:
        return self.rdp_

    @property
    def rsp(self) -> rsp_props.DragExMaterialRSPProperties:
        return self.rsp_

    oot_: bpy.props.PointerProperty(type=oot_props.DragExMaterialOoTProperties)

    @property
    def oot(self) -> oot_props.DragExMaterialOoTProperties:
        return self.oot_


class DragExMaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_dragex"
    bl_label = "DragEx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        scene_dragex = util.DRAGEX(context.scene)
        return scene_dragex.target != "NONE" and context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex = util.DRAGEX(mat)
        self.layout.operator(DragExSetMaterialModeOperator.bl_idname)
        material_modes.material_modes_dict[mat_dragex.mode].draw(self.layout, mat)


class DragExSetMaterialModeOperator(bpy.types.Operator):
    bl_idname = "dragex.set_material_mode"
    bl_label = "DragEx Set Material Mode"
    bl_property = "mode"

    def get_modes(self, context: bpy.types.Context | None):
        return material_modes.material_mode_items

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=get_modes,
    )

    @classmethod
    def poll(cls, context):
        return hasattr(context, "material") and context.material is not None

    def execute(self, context):  # type: ignore
        material = context.material
        assert material is not None
        material_dragex = util.DRAGEX(material)
        prev_mode = material_dragex.mode
        material_dragex.mode = self.mode
        material_modes.material_modes_dict[self.mode].init(material, prev_mode)
        material.update_tag()
        return {"FINISHED"}

    def invoke(self, context, event):  # type: ignore
        assert context.window_manager is not None
        context.window_manager.invoke_search_popup(self)
        return {"RUNNING_MODAL"}


class DragExCollectionProperties(bpy.types.PropertyGroup):
    oot_: bpy.props.PointerProperty(type=oot_props.DragExCollectionOoTProperties)

    @property
    def oot(self) -> oot_props.DragExCollectionOoTProperties:
        return self.oot_


class DragExSceneProperties(bpy.types.PropertyGroup):
    target: bpy.props.EnumProperty(
        name="Target",
        description="DragEx target",
        default="NONE",
        items=(
            ("NONE", "None", "Disable DragEx features", 1),
            (
                "OOT_F3DEX2_PL",
                "OoT F3DEX2 PosLight",
                "Ocarina of Time 64 with the F3DEX2 Positional Light microcode",
                2,
            ),
        ),
    )

    oot_: bpy.props.PointerProperty(type=oot_props.DragExSceneOoTProperties)

    @property
    def oot(self) -> oot_props.DragExSceneOoTProperties:
        return self.oot_


class DragExObjectProperties(bpy.types.PropertyGroup):
    oot_: bpy.props.PointerProperty(type=oot_props.DragExObjectOoTProperties)

    @property
    def oot(self) -> oot_props.DragExObjectOoTProperties:
        return self.oot_


class DragExTargetPanel(bpy.types.Panel):
    bl_idname = "DRAGEX_PT_target"
    bl_label = "Target"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DragEx"
    bl_order = 0

    def draw(self, context):
        assert self.layout is not None
        scene = context.scene
        assert scene is not None
        dragex = util.DRAGEX(scene)
        self.layout.prop(dragex, "target")


classes = (
    rsp_props.DragExMaterialRSPProperties,
    other_mode_props.DragExMaterialOtherModesProperties,
    tiles_props.DragExMaterialTileProperties,
    tiles_props.DragExMaterialTilesProperties,
    combiner_props.DragExMaterialCombinerProperties,
    vals_props.DragExMaterialValsProperties,
    material_modes.DragExMaterialModesBasicProperties,
    material_modes.DragExMaterialModesMultitextureProperties,
    material_modes.DragExMaterialModesProperties,
    DragExMaterialRDPProperties,
    oot_props.DragExMaterialOoTProperties,
    DragExMaterialProperties,
    DragExMaterialPanel,
    oot_panels.DragExMaterialOoTCollisionPanel,
    oot_props.DragExCollectionOoTSceneProperties,
    oot_props.DragExCollectionOoTRoomProperties,
    oot_props.DragExCollectionOoTProperties,
    DragExCollectionProperties,
    oot_props.DragExSceneOoTProperties,
    DragExSceneProperties,
    oot_props.DragExObjectOoTEmptyProperties,
    oot_props.DragExObjectOoTProperties,
    DragExObjectProperties,
    DragExTargetPanel,
    oot_ops.DragExOoTNewSceneOperator,
    oot_panels.DragExOoTPanel,
    oot_panels.DragExCollectionOoTPanel,
    oot_panels.DragExObjectOoTEmptyPanel,
    oot_ops.DragExOoTExportSceneOperator,
    oot_ops.DragExOoTExportSkeletonOperator,
    oot_ops.DragExOoTFindNotSingleBindVerticesOperator,
    DragExSetMaterialModeOperator,
)

cannot_register = False


def register():
    global cannot_register
    cannot_register = False

    print("Hi from", __package__)

    if dragex_backend is None:
        print("DragEx cannot register, dragex_backend is missing")
        cannot_register = True
        return

    print(dir(dragex_backend))

    print(f"{BUILD_ID=}")
    print(f"{dragex_backend.get_build_id()=}")

    if dragex_backend.get_build_id() != BUILD_ID:
        print("DragEx cannot register, dragex_backend has a mismatching BUILD_ID")
        cannot_register = True
        return

    assert __package__ is not None
    logs_folder_p = Path(
        bpy.utils.extension_path_user(__package__, path="logs", create=True)
    )

    with os.scandir(logs_folder_p) as it:
        logs_entries = [_entry for _entry in it if _entry.is_file()]
    if len(logs_entries) > 200:
        logs_entries.sort(key=lambda entry: entry.stat().st_mtime)
        # delete all entries except the 100 most recent ones
        for entry in logs_entries[:-100]:
            os.unlink(entry.path)

    log_file_p = (
        logs_folder_p
        / f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}.txt"
    )

    dragex_backend.logging.set_log_file(log_file_p)

    dragex_backend.logging.info(f"Now logging to {log_file_p}")

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.dragex = bpy.props.PointerProperty(type=DragExSceneProperties)  # type: ignore
    bpy.types.Collection.dragex = bpy.props.PointerProperty(  # type: ignore
        type=DragExCollectionProperties
    )
    bpy.types.Object.dragex = bpy.props.PointerProperty(type=DragExObjectProperties)  # type: ignore
    bpy.types.Material.dragex = bpy.props.PointerProperty(type=DragExMaterialProperties)  # type: ignore

    from . import f64render_dragex

    f64render_dragex.register()


def unregister():
    if cannot_register:
        print("DragEx unregister skipped as it could not register")
        return

    try:
        unregister_impl()
    finally:
        dragex_backend.logging.clear_log_file()


def unregister_impl():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    from . import f64render_dragex

    f64render_dragex.unregister()

    print("Bye from", __package__)
