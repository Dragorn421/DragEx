import argparse
import dataclasses
from pathlib import Path
import tomllib
from typing import Optional

import bpy

from . import oot_export_map
from . import oot_util


EXAMPLE_CATALOG_TOML = """\
[[export_map]]
collection = "My map Scene"
to = "assets/scenes/mymap/"
"""


@dataclasses.dataclass
class CatalogExportMapEntry:
    collection_name: str
    to: Path


@dataclasses.dataclass
class Catalog:
    export_maps: list[CatalogExportMapEntry]


def export_catalog(
    catalog: Catalog,
    repo_root_p: Optional[Path] = None,
):
    for export_map_entry in catalog.export_maps:
        coll_scene_to_export = bpy.data.collections[export_map_entry.collection_name]

        scene = bpy.context.scene
        assert scene is not None

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
    return Catalog(
        export_maps=export_maps,
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
