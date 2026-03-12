import bpy

from .. import util


class DragExCollectionOoTSceneProperties(bpy.types.PropertyGroup):
    pass


class DragExCollectionOoTRoomProperties(bpy.types.PropertyGroup):
    number: bpy.props.IntProperty(
        name="Room Number",
        description="Number/ID for this room",
        min=0,
    )


class DragExCollectionOoTProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description="OoT collection type",
        items=(
            ("NONE", "None", "No type. A regular collection"),
            ("SCENE", "Scene", "Collection represents an OoT scene"),
            ("ROOM", "Room", "Collection represents an OoT room"),
        ),
        default="NONE",
    )

    scene_: bpy.props.PointerProperty(type=DragExCollectionOoTSceneProperties)
    room_: bpy.props.PointerProperty(type=DragExCollectionOoTRoomProperties)

    @property
    def scene(self) -> DragExCollectionOoTSceneProperties:
        return self.scene_

    @property
    def room(self) -> DragExCollectionOoTRoomProperties:
        return self.room_


class DragExSceneOoTProperties(bpy.types.PropertyGroup):
    scale: bpy.props.FloatProperty(
        name="Scale",
        description=(
            "OoT to Blender scaling factor. "
            "For example the default value of 0.01 means 1 Blender centimeter "
            "corresponds to 1 OoT unit"
        ),
        default=0.01,
    )


def validate_export_pos_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = util.make_c_identifier(self.export_pos_name)
    if self.export_pos_name != c_identifier:
        self.export_pos_name = c_identifier


def validate_export_rot_yxz_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = util.make_c_identifier(self.export_rot_yxz_name)
    if self.export_rot_yxz_name != c_identifier:
        self.export_rot_yxz_name = c_identifier


def validate_export_yaw_name(self, context):
    assert isinstance(self, DragExObjectOoTEmptyProperties)
    c_identifier = util.make_c_identifier(self.export_yaw_name)
    if self.export_yaw_name != c_identifier:
        self.export_yaw_name = c_identifier


class DragExObjectOoTEmptyProperties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description="Type of OoT empty object",
        default="NONE",
        items=(("NONE", "None", "No type. A regular empty object"),),
    )

    export_pos: bpy.props.BoolProperty(
        name="Export Position",
        description=(
            "On export, write the location of this empty to a positions.h file"
        ),
    )
    export_pos_name: bpy.props.StringProperty(
        name="Export Position Name",
        description="The name of the macro to name the exported location as",
        default="POS_",
        update=validate_export_pos_name,
    )

    export_rot_yxz: bpy.props.BoolProperty(
        name="Export Rotation",
        description=(
            "On export, write the rotation (as Euler YXZ, as used by Actor_Draw)"
            " of this empty to a positions.h file"
        ),
    )
    export_rot_yxz_name: bpy.props.StringProperty(
        name="Export Rotation Name",
        description="The name of the macro to name the exported rotation as",
        default="ROT_",
        update=validate_export_rot_yxz_name,
    )

    export_yaw: bpy.props.BoolProperty(
        name="Export Yaw",
        description=(
            "On export, write the yaw (rotation around the vertical axis)"
            " of this empty to a positions.h file"
        ),
    )
    export_yaw_name: bpy.props.StringProperty(
        name="Export Yaw Name",
        description="The name of the macro to name the exported yaw as",
        default="YAW_",
        update=validate_export_yaw_name,
    )


class DragExObjectOoTProperties(bpy.types.PropertyGroup):
    empty_: bpy.props.PointerProperty(type=DragExObjectOoTEmptyProperties)

    @property
    def empty(self) -> DragExObjectOoTEmptyProperties:
        return self.empty_


def search_polytype_names(self, context: bpy.types.Context, edit_text: str):
    if not hasattr(context, "object") or context.object is None:
        return list[str]()
    obj = context.object
    search = edit_text.lower()
    used_polytypes = set[str]()
    for coll in bpy.data.collections.values():
        assert coll is not None
        coll_dragex = util.DRAGEX(coll)
        if coll_dragex.oot.type == "SCENE" and obj in coll.all_objects.values():
            for obj in coll.all_objects:
                if obj.type == "MESH":
                    for mat_slot in obj.material_slots:
                        mat = mat_slot.material
                        if mat is not None:
                            mat_dragex = util.DRAGEX(mat)
                            if search in mat_dragex.oot.polytype_name.lower():
                                used_polytypes.add(mat_dragex.oot.polytype_name)
    return sorted(used_polytypes)


class DragExMaterialOoTProperties(bpy.types.PropertyGroup):
    polytype_name: bpy.props.StringProperty(
        name="Polytype",
        description=(
            "The name of the polytype (surface type) this material uses"
            " for exporting collision, as found in table_polytypes.h"
        ),
        default="DEFAULT",
        search=search_polytype_names,
    )


class DragExMeshOoTProperties(bpy.types.PropertyGroup):
    draw_layer: bpy.props.EnumProperty(
        name="Draw Layer",
        description="",
        items=(
            ("OPA", "Opaque", ""),
            ("XLU", "Translucent", ""),
        ),
        default="OPA",
    )
