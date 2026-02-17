import abc
import datetime
import math
import os
from pathlib import Path
from typing import TYPE_CHECKING

import bpy
import mathutils

from .build_id import BUILD_ID
from . import meshstuff
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


class DragExBackendDemoOperator(bpy.types.Operator):
    bl_idname = "dragex.dragex_backend_demo"
    bl_label = "DragEx backend demo"

    def execute_impl(self, context: bpy.types.Context):
        import time

        start = time.time()

        print("Hello World")
        assert context.object is not None
        mesh = context.object.data
        assert isinstance(mesh, bpy.types.Mesh)
        image_infos = meshstuff.ImageInfos()
        mesh_info = meshstuff.mesh_to_mesh_info(
            context.object,
            mesh,
            (util.transform_zup_to_yup @ mathutils.Matrix.Scale(1, 3)),
            image_infos,
            "",
        )
        with open(
            "/home/dragorn421/Documents/dragex/dragex_attempt2/output.c", "w"
        ) as f:
            mesh_info.write_c(f.fileno())
        end = time.time()
        print("dragex_backend_demo took", end - start, "seconds")
        return {"FINISHED"}

    def execute(self, context):  # type: ignore
        try:
            return self.execute_impl(context)
        finally:
            dragex_backend.logging.flush()


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


class NoneMaterialMode(MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        pass

    @staticmethod
    def draw(layout, material):
        pass


class BasicMaterialMode(MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        BasicMaterialMode.apply_mode_props(material)

    @staticmethod
    def draw(layout, material):
        material_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        mode_basic = material_dragex.modes.basic
        layout.template_ID(mode_basic, "texture", new="image.new", open="image.open")
        texture = mode_basic.texture
        if texture is not None and tuple(texture.size) != (0, 0):
            texture_w, texture_h = texture.size
            if texture_w * texture_h * 2 > TMEM_SIZE:
                layout.label(text="Texture too big: max 32x64 or 64x32", icon="ERROR")
            if texture_w * 2 % 8 != 0:
                layout.label(text="Texture width must be a multiple of 4", icon="ERROR")
            if intlog2(texture_w) is None:
                layout.label(
                    text="Texture width must be a power of 2 for wrapping", icon="INFO"
                )
            if intlog2(texture_h) is None:
                layout.label(
                    text="Texture height must be a power of 2 for wrapping", icon="INFO"
                )
        layout.prop(mode_basic, "shading")
        layout.prop(mode_basic, "alpha_blend")
        layout.prop(mode_basic, "fog")

    @staticmethod
    def apply_mode_props(material):
        material_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        basic_props = material_dragex.modes.basic
        texture: bpy.types.Image | None = basic_props.texture

        tile0 = material_dragex.rdp.tiles.tiles[0]
        tile0.image = texture
        tile0.format = "RGBA"
        tile0.size = "16"
        tile0.address = 0
        tile0.palette = 0
        if texture is not None and tuple(texture.size) != (0, 0):
            # TODO check if s=width, t=height (test with non-square texture)
            texture_w, texture_h = texture.size
            if texture_w * texture_h * 2 > TMEM_SIZE:
                tile0.image = None
            material_dragex.uv_basis_s = texture_w
            material_dragex.uv_basis_t = texture_h
            if texture_w * 2 % 8 != 0:
                tile0.image = None
            tile0.line = texture_w * 2 // 8
            mask_S = intlog2(texture_w)
            mask_T = intlog2(texture_h)
            if mask_S is None:
                tile0.clamp_S = True
                tile0.mask_S = 0
            else:
                tile0.clamp_S = False
                tile0.mask_S = mask_S
            tile0.mirror_S = False
            tile0.shift_S = 0
            if mask_T is None:
                tile0.clamp_T = True
                tile0.mask_T = 0
            else:
                tile0.clamp_T = False
                tile0.mask_T = mask_T
            tile0.mirror_T = False
            tile0.shift_T = 0
            tile0.upper_left_S = 0
            tile0.upper_left_T = 0
            tile0.lower_right_S = texture_w - 1
            tile0.lower_right_T = texture_h - 1

        rsp_props = material_dragex.rsp

        one_cycle = True
        if basic_props.fog:
            one_cycle = False

        rsp_props.zbuffer = True
        if basic_props.shading == "LIGHTING":
            rsp_props.lighting = True
            rsp_props.vertex_colors = False
        elif basic_props.shading == "VERTEX_COLORS":
            rsp_props.lighting = False
            rsp_props.vertex_colors = True
        else:
            assert False, basic_props.shading
        rsp_props.cull_front = False
        rsp_props.cull_back = True
        rsp_props.fog = basic_props.fog
        rsp_props.uv_gen_spherical = False
        rsp_props.uv_gen_linear = False
        rsp_props.shade_smooth = True

        om = material_dragex.rdp.other_modes
        om.atomic_prim = False
        om.cycle_type = "1CYCLE" if one_cycle else "2CYCLE"
        om.persp_tex_en = True
        om.detail_tex_en = False
        om.sharpen_tex_en = False
        om.tex_lod_en = False
        om.tlut_en = False
        om.tlut_type = False
        om.sample_type = True
        om.mid_texel = False
        om.bi_lerp_0 = True
        om.bi_lerp_1 = True
        om.convert_one = False  # TODO ?
        om.key_en = False
        om.rgb_dither_sel = "MAGIC_SQUARE"
        om.alpha_dither_sel = "SAME_AS_RGB"  # ?
        if rsp_props.fog:
            assert not one_cycle
            om.bl_m1a_0 = "FOG_COLOR"
            om.bl_m1b_0 = "SHADE_ALPHA"
            om.bl_m2a_0 = "INPUT"
            om.bl_m2b_0 = "1_MINUS_A"
            om.bl_m1a_1 = "INPUT"
            om.bl_m1b_1 = "INPUT_ALPHA"
            om.bl_m2a_1 = "MEMORY"
            om.bl_m2b_1 = (
                "1_MINUS_A"
                if basic_props.alpha_blend == "TRANSPARENT"
                else "MEMORY_COVERAGE"
            )
        else:
            om.bl_m1a_0 = "INPUT"
            om.bl_m1b_0 = "INPUT_ALPHA"
            om.bl_m2a_0 = "MEMORY"
            om.bl_m2b_0 = (
                "1_MINUS_A"
                if basic_props.alpha_blend == "TRANSPARENT"
                else "MEMORY_COVERAGE"
            )
            if one_cycle:
                om.bl_m1a_1 = om.bl_m1a_0
                om.bl_m1b_1 = om.bl_m1b_0
                om.bl_m2a_1 = om.bl_m2a_0
                om.bl_m2b_1 = om.bl_m2b_0
            else:
                om.bl_m1a_1 = "INPUT"
                om.bl_m1b_1 = "0"
                om.bl_m2a_1 = "INPUT"
                om.bl_m2b_1 = "1"
        if basic_props.alpha_blend in {"OPAQUE", "CUTOUT"}:
            om.force_blend = False
            om.alpha_cvg_select = True
            om.cvg_x_alpha = basic_props.alpha_blend == "CUTOUT"
            om.z_mode = "OPAQUE"
            om.cvg_dest = "CLAMP"
            om.color_on_cvg = False
            om.z_update_en = True
        elif basic_props.alpha_blend == "TRANSPARENT":
            om.force_blend = True
            om.alpha_cvg_select = False
            om.cvg_x_alpha = False
            om.z_mode = "TRANSPARENT"
            om.cvg_dest = "WRAP"
            om.color_on_cvg = True
            om.z_update_en = False
        else:
            assert False, basic_props.alpha_blend
        om.image_read_en = True
        om.z_compare_en = True
        om.antialias_en = True
        om.z_source_sel = False
        om.dither_alpha_en = False
        om.alpha_compare_en = False

        cb = material_dragex.rdp.combiner
        if texture is None:
            cb.rgb_A_0 = "0"
            cb.rgb_B_0 = "0"
            cb.rgb_C_0 = "0"
            cb.rgb_D_0 = "SHADE"
        else:
            cb.rgb_A_0 = "TEX0"
            cb.rgb_B_0 = "0"
            cb.rgb_C_0 = "SHADE"
            cb.rgb_D_0 = "0"
        if basic_props.alpha_blend in {"CUTOUT", "TRANSPARENT"}:
            if basic_props.fog:
                cb.alpha_A_0 = "0"
                cb.alpha_B_0 = "0"
                cb.alpha_C_0 = "0"
                cb.alpha_D_0 = "1" if texture is None else "TEX0"
            else:
                if texture is None:
                    cb.alpha_A_0 = "0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "0"
                    cb.alpha_D_0 = "SHADE"
                else:
                    cb.alpha_A_0 = "TEX0"
                    cb.alpha_B_0 = "0"
                    cb.alpha_C_0 = "SHADE"
                    cb.alpha_D_0 = "0"
        else:
            cb.alpha_A_0 = "0"
            cb.alpha_B_0 = "0"
            cb.alpha_C_0 = "0"
            cb.alpha_D_0 = "1"
        if one_cycle:
            cb.rgb_A_1 = cb.rgb_A_0
            cb.rgb_B_1 = cb.rgb_B_0
            cb.rgb_C_1 = cb.rgb_C_0
            cb.rgb_D_1 = cb.rgb_D_0
            cb.alpha_A_1 = cb.alpha_A_0
            cb.alpha_B_1 = cb.alpha_B_0
            cb.alpha_C_1 = cb.alpha_C_0
            cb.alpha_D_1 = cb.alpha_D_0
        else:
            cb.rgb_A_1 = "0"
            cb.rgb_B_1 = "0"
            cb.rgb_C_1 = "0"
            cb.rgb_D_1 = "COMBINED"
            cb.alpha_A_1 = "0"
            cb.alpha_B_1 = "0"
            cb.alpha_C_1 = "0"
            cb.alpha_D_1 = "COMBINED"

    @staticmethod
    def on_mode_prop_update(_self, context: bpy.types.Context):
        material = context.material
        assert material is not None
        BasicMaterialMode.apply_mode_props(material)


class DragExMaterialModesBasicProperties(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(
        name="Texture",
        type=bpy.types.Image,
        update=BasicMaterialMode.on_mode_prop_update,
    )
    shading: bpy.props.EnumProperty(
        name="Shading",
        description="Pick the shade color source for vertices",
        items=(
            ("LIGHTING", "Lighting", "Vertices are colored by the active lights"),
            (
                "VERTEX_COLORS",
                "Vertex Colors",
                "Vertices are colored according to the painted vertex colors",
            ),
        ),
        default="LIGHTING",
        update=BasicMaterialMode.on_mode_prop_update,
    )
    alpha_blend: bpy.props.EnumProperty(
        name="Alpha Blend",
        description="Choose how the alpha affects the material",
        items=(
            ("OPAQUE", "Opaque", "Material is fully opaque"),
            (
                "CUTOUT",
                "Cutout",
                (
                    "Material is opaque with holes (fully transparent spots)"
                    " where the alpha is below threshold (e.g. fences)"
                ),
            ),
            (
                "TRANSPARENT",
                "Transparent",
                (
                    "Material is transparent, drawing some geometry that"
                    " can be seen through (e.g. colored glass)"
                ),
            ),
        ),
        default="OPAQUE",
        update=BasicMaterialMode.on_mode_prop_update,
    )
    fog: bpy.props.BoolProperty(
        name="Fog",
        description=(
            "Whether this material is affected by fog"
            " (blend with the fog color as the geometry is further from the camera)"
        ),
        default=True,
        update=BasicMaterialMode.on_mode_prop_update,
    )


class DragExMaterialModesProperties(bpy.types.PropertyGroup):
    basic_: bpy.props.PointerProperty(type=DragExMaterialModesBasicProperties)

    @property
    def basic(self) -> DragExMaterialModesBasicProperties:
        return self.basic_


class FullMaterialMode(MaterialMode):
    @staticmethod
    def init(material, prev_mode):
        pass

    @staticmethod
    def draw(layout, material):
        mat_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        mat_geomode = mat_dragex.rsp
        other_modes = mat_dragex.rdp.other_modes
        combiner = mat_dragex.rdp.combiner
        vals = mat_dragex.rdp.vals
        tiles = mat_dragex.rdp.tiles.tiles
        layout.prop(mat_geomode, "zbuffer")
        layout.prop(mat_geomode, "lighting")
        layout.prop(mat_geomode, "vertex_colors")
        layout.prop(mat_geomode, "cull_front")
        layout.prop(mat_geomode, "cull_back")
        layout.prop(mat_geomode, "fog")
        layout.prop(mat_geomode, "uv_gen_spherical")
        layout.prop(mat_geomode, "uv_gen_linear")
        layout.prop(mat_geomode, "shade_smooth")
        layout.prop(mat_dragex, "uv_basis_s")
        layout.prop(mat_dragex, "uv_basis_t")
        layout.prop(vals, "primitive_depth_z")
        layout.prop(vals, "primitive_depth_dz")
        layout.prop(vals, "fog_color")
        layout.prop(vals, "blend_color")
        layout.prop(vals, "min_level")
        layout.prop(vals, "prim_lod_frac")
        layout.prop(vals, "primitive_color")
        layout.prop(vals, "environment_color")
        box = layout.box()
        box.prop(other_modes, "atomic_prim")
        box.prop(other_modes, "cycle_type")
        box.prop(other_modes, "persp_tex_en")
        box.prop(other_modes, "detail_tex_en")
        box.prop(other_modes, "sharpen_tex_en")
        box.prop(other_modes, "tex_lod_en")
        box.prop(other_modes, "tlut_en")
        box.prop(other_modes, "tlut_type")
        box.prop(other_modes, "sample_type")
        box.prop(other_modes, "mid_texel")
        box.prop(other_modes, "bi_lerp_0")
        box.prop(other_modes, "bi_lerp_1")
        box.prop(other_modes, "convert_one")
        box.prop(other_modes, "key_en")
        box.prop(other_modes, "rgb_dither_sel")
        box.prop(other_modes, "alpha_dither_sel")
        box.prop(other_modes, "bl_m1a_0")
        box.prop(other_modes, "bl_m1a_1")
        box.prop(other_modes, "bl_m1b_0")
        box.prop(other_modes, "bl_m1b_1")
        box.prop(other_modes, "bl_m2a_0")
        box.prop(other_modes, "bl_m2a_1")
        box.prop(other_modes, "bl_m2b_0")
        box.prop(other_modes, "bl_m2b_1")
        box.prop(other_modes, "force_blend")
        box.prop(other_modes, "alpha_cvg_select")
        box.prop(other_modes, "cvg_x_alpha")
        box.prop(other_modes, "z_mode")
        box.prop(other_modes, "cvg_dest")
        box.prop(other_modes, "color_on_cvg")
        box.prop(other_modes, "image_read_en")
        box.prop(other_modes, "z_update_en")
        box.prop(other_modes, "z_compare_en")
        box.prop(other_modes, "antialias_en")
        box.prop(other_modes, "z_source_sel")
        box.prop(other_modes, "dither_alpha_en")
        box.prop(other_modes, "alpha_compare_en")
        box = layout.box()
        box.prop(combiner, "rgb_A_0")
        box.prop(combiner, "rgb_B_0")
        box.prop(combiner, "rgb_C_0")
        box.prop(combiner, "rgb_D_0")
        box.prop(combiner, "alpha_A_0")
        box.prop(combiner, "alpha_B_0")
        box.prop(combiner, "alpha_C_0")
        box.prop(combiner, "alpha_D_0")
        box.prop(combiner, "rgb_A_1")
        box.prop(combiner, "rgb_B_1")
        box.prop(combiner, "rgb_C_1")
        box.prop(combiner, "rgb_D_1")
        box.prop(combiner, "alpha_A_1")
        box.prop(combiner, "alpha_B_1")
        box.prop(combiner, "alpha_C_1")
        box.prop(combiner, "alpha_D_1")
        for i, tile in enumerate(tiles):
            box = layout.box()
            box.label(text=f"Tile {i}")
            box.template_ID(tile, "image", new="image.new", open="image.open")
            box.prop(tile, "format")
            box.prop(tile, "size")
            box.prop(tile, "line")
            box.prop(tile, "address")
            box.prop(tile, "palette")
            box.prop(tile, "clamp_T")
            box.prop(tile, "mirror_T")
            box.prop(tile, "mask_T")
            box.prop(tile, "shift_T")
            box.prop(tile, "clamp_S")
            box.prop(tile, "mirror_S")
            box.prop(tile, "mask_S")
            box.prop(tile, "shift_S")
            box.prop(tile, "upper_left_S")
            box.prop(tile, "upper_left_T")
            box.prop(tile, "lower_right_S")
            box.prop(tile, "lower_right_T")


material_modes_dict: dict[str, type[MaterialMode]] = {
    "NONE": NoneMaterialMode,
    "BASIC": BasicMaterialMode,
    "FULL": FullMaterialMode,
}

material_mode_items = (
    # TODO add descriptions
    ("NONE", "None", ""),
    ("BASIC", "Basic", ""),
    ("FULL", "Full", ""),
)


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


def search_polytype_names(self, context: bpy.types.Context, edit_text: str):
    if not hasattr(context, "object") or context.object is None:
        return list[str]()
    obj = context.object
    search = edit_text.lower()
    used_polytypes = set[str]()
    for coll in bpy.data.collections.values():
        assert coll is not None
        coll_dragex: DragExCollectionProperties = coll.dragex  # type: ignore
        if coll_dragex.oot.type == "SCENE" and obj in coll.all_objects.values():
            for obj in coll.all_objects:
                if obj.type == "MESH":
                    for mat_slot in obj.material_slots:
                        mat = mat_slot.material
                        if mat is not None:
                            mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
                            if search in mat_dragex.polytype_name.lower():
                                used_polytypes.add(mat_dragex.polytype_name)
    return sorted(used_polytypes)


class DragExMaterialProperties(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(
        items=material_mode_items,
        default="NONE",
    )
    modes_: bpy.props.PointerProperty(type=DragExMaterialModesProperties)

    @property
    def modes(self) -> DragExMaterialModesProperties:
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

    polytype_name: bpy.props.StringProperty(
        name="Polytype",
        description=(
            "The name of the polytype (surface type) this material uses"
            " for exporting collision, as found in table_polytypes.h"
        ),
        default="DEFAULT",
        search=search_polytype_names,
    )


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
        scene_dragex: DragExSceneProperties = context.scene.dragex  # type: ignore
        return scene_dragex.target != "NONE" and context.material is not None

    def draw(self, context):
        assert self.layout is not None
        mat = context.material
        assert mat is not None
        mat_dragex: DragExMaterialProperties = mat.dragex  # type: ignore
        self.layout.operator(DragExSetMaterialModeOperator.bl_idname)
        material_modes_dict[mat_dragex.mode].draw(self.layout, mat)


class DragExSetMaterialModeOperator(bpy.types.Operator):
    bl_idname = "dragex.set_material_mode"
    bl_label = "DragEx Set Material Mode"
    bl_property = "mode"

    def get_modes(self, context: bpy.types.Context | None):
        return material_mode_items

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
        material_dragex: DragExMaterialProperties = material.dragex  # type: ignore
        prev_mode = material_dragex.mode
        material_dragex.mode = self.mode
        material_modes_dict[self.mode].init(material, prev_mode)
        if context.region is not None:
            context.region.tag_redraw()
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
        dragex: DragExSceneProperties = scene.dragex  # type: ignore
        self.layout.prop(dragex, "target")


classes = (
    rsp_props.DragExMaterialRSPProperties,
    other_mode_props.DragExMaterialOtherModesProperties,
    tiles_props.DragExMaterialTileProperties,
    tiles_props.DragExMaterialTilesProperties,
    combiner_props.DragExMaterialCombinerProperties,
    vals_props.DragExMaterialValsProperties,
    DragExMaterialModesBasicProperties,
    DragExMaterialModesProperties,
    DragExMaterialRDPProperties,
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
    DragExBackendDemoOperator,
    oot_ops.DragExOoTExportSceneOperator,
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
