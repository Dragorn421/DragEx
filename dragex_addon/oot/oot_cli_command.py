import argparse
import dataclasses
from pathlib import Path
import tomllib
from typing import Optional

import bpy

from . import oot_export_map
from . import oot_skelanime
from . import oot_util


EXAMPLE_CATALOG_TOML = """\
[[export_map]]
collection = "My map Scene"
to = "assets/scenes/mymap/"
[[export_skeleton]]
armature = "Armature"
to = "assets/objects/object_myskeleton/"
[[export_animation]]
armature = "Armature"
action = "ArmatureAction"
to = "assets/objects/object_myskeleton/"
"""


@dataclasses.dataclass
class CatalogExportMapEntry:
    collection_name: str
    to: Path


@dataclasses.dataclass
class CatalogExportSkeletonEntry:
    armature_name: str
    to: Path


@dataclasses.dataclass
class CatalogExportAnimationEntry:
    armature_name: str
    action_name: str
    to: Path


@dataclasses.dataclass
class Catalog:
    export_maps: list[CatalogExportMapEntry]
    export_skeletons: list[CatalogExportSkeletonEntry]
    export_animations: list[CatalogExportAnimationEntry]


def export_catalog(
    catalog: Catalog,
    repo_root_p: Optional[Path] = None,
):
    scene = bpy.context.scene
    assert scene is not None

    for export_map_entry in catalog.export_maps:
        coll_scene_to_export = bpy.data.collections[export_map_entry.collection_name]

        if repo_root_p is None:
            try:
                decomp_repo_p = oot_util.find_decomp_repo(export_map_entry.to)
            except:
                print(f"{export_map_entry.to=}")
                raise
        else:
            decomp_repo_p = repo_root_p

        oot_export_map.export_coll_scene(
            coll_scene_to_export,
            export_map_entry.to,
            scene,
            decomp_repo_p,
        )

    for export_skeleton_entry in catalog.export_skeletons:
        armature_object = bpy.data.objects[export_skeleton_entry.armature_name]
        armature_data = armature_object.data
        assert isinstance(armature_data, bpy.types.Armature), armature_data

        if repo_root_p is None:
            try:
                decomp_repo_p = oot_util.find_decomp_repo(export_skeleton_entry.to)
            except:
                print(f"{export_skeleton_entry.to=}")
                raise
        else:
            decomp_repo_p = repo_root_p

        oot_skelanime.export_skeleton(
            armature_object,
            armature_data,
            scene,
            export_skeleton_entry.to,
            decomp_repo_p,
        )

    for export_animation_entry in catalog.export_animations:
        armature_object = bpy.data.objects[export_animation_entry.armature_name]
        armature_data = armature_object.data
        assert isinstance(armature_data, bpy.types.Armature), armature_data
        action = bpy.data.actions[export_animation_entry.action_name]

        armature_object.animation_data_create()
        assert armature_object.animation_data is not None
        armature_object.animation_data.action = action

        oot_skelanime.export_anim(
            armature_object,
            armature_data,
            scene,
            export_animation_entry.to,
            action,
        )


def parse_catalog(catalog_toml_p: Path):
    with catalog_toml_p.open("rb") as f:
        data = tomllib.load(f)

    data_export_map = data.get("export_map", [])
    assert isinstance(data_export_map, list), data_export_map
    export_maps: list[CatalogExportMapEntry] = []
    for data_export_map_entry in data_export_map:
        assert isinstance(data_export_map_entry, dict), data_export_map_entry
        export_maps.append(
            CatalogExportMapEntry(
                data_export_map_entry["collection"],
                Path(data_export_map_entry["to"]),
            )
        )

    data_export_skeleton = data.get("export_skeleton", [])
    assert isinstance(data_export_skeleton, list), data_export_skeleton
    export_skeletons: list[CatalogExportSkeletonEntry] = []
    for data_export_skeleton_entry in data_export_skeleton:
        assert isinstance(data_export_skeleton_entry, dict), data_export_skeleton_entry
        export_skeletons.append(
            CatalogExportSkeletonEntry(
                data_export_skeleton_entry["armature"],
                Path(data_export_skeleton_entry["to"]),
            )
        )

    data_export_animation = data.get("export_animation", [])
    assert isinstance(data_export_animation, list), data_export_animation
    export_animations: list[CatalogExportAnimationEntry] = []
    for data_export_animation_entry in data_export_animation:
        assert isinstance(
            data_export_animation_entry, dict
        ), data_export_animation_entry
        export_animations.append(
            CatalogExportAnimationEntry(
                data_export_animation_entry["armature"],
                data_export_animation_entry["action"],
                Path(data_export_animation_entry["to"]),
            )
        )

    return Catalog(
        export_maps,
        export_skeletons,
        export_animations,
    )


def run_oot_command(args):
    catalog = parse_catalog(Path(args.catalog))
    export_catalog(
        catalog,
        Path(args.repo_root) if args.repo_root is not None else None,
    )
    return 0


def add_subparser(subparsers):
    oot_parser: argparse.ArgumentParser = subparsers.add_parser(
        "oot",
        description=("Example catalog.toml:\n\n" + EXAMPLE_CATALOG_TOML),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    oot_parser.add_argument(
        "--repo-root",
        dest="repo_root",
        help=(
            "Path to the root of the repo in which data is exported. "
            "Defaults to a parent folder where spec is found"
        ),
    )
    oot_parser.add_argument(
        "catalog",
        help="The catalog.toml file containing information on what to export",
    )
    oot_parser.set_defaults(func=run_oot_command)
