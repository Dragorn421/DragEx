import dataclasses
from pathlib import Path, PurePosixPath

import bpy
import mathutils

from .. import mesh
from .. import util


@dataclasses.dataclass
class ExportOptions:
    transform: mathutils.Matrix
    decomp_repo_p: Path


def export_dlist_impl(
    mesh_object: bpy.types.Object,
    export_filepath: Path,
    export_options: ExportOptions,
):
    export_directory = export_filepath.parent
    export_directory.mkdir(parents=True, exist_ok=True)
    assert mesh_object.type == "MESH"
    assert isinstance(mesh_object.data, bpy.types.Mesh)

    image_infos = mesh.ImageInfos()

    mesh_info = mesh.mesh_to_mesh_info(
        mesh_object,
        mesh_object.data,
        # TODO test more with different matrix_world
        export_options.transform @ mesh_object.matrix_world,
        image_infos,
        # TODO rework prefixing. this prefix is useful for prefixing image symbol
        # names, but leads to a duplicate prefix for everything else
        util.make_c_identifier(mesh_object.name) + "_",
    )

    with util.FDManager() as fd_manager:
        fd = fd_manager.open_w(export_filepath)
        with open(fd, "w", closefd=False) as f:
            f.write("""\
#include "ultra64.h"

""")

            for c_identifier, image_key in image_infos.key_by_c_identifier.items():
                image_file_stem = (
                    f"{c_identifier}.{image_key.format.lower()}{image_key.size}"
                )
                image_key.image.save(
                    filepath=str(export_directory / f"{image_file_stem}.png"),
                )
                image_inc_c_p = (
                    PurePosixPath(
                        *export_directory.relative_to(
                            export_options.decomp_repo_p
                        ).parts
                    )
                    / f"{image_file_stem}.inc.c"
                )
                f.write(
                    f"u64 {c_identifier}[] = "
                    "{\n"
                    f'#include "{image_inc_c_p}"\n'
                    "};\n"
                    "\n"
                )

        mesh_info.write_c(fd, ())


def export_dlist(
    mesh_object: bpy.types.Object,
    export_filepath: Path,
    scene: bpy.types.Scene,
    decomp_repo_p: Path,
):
    export_dlist_impl(
        mesh_object,
        export_filepath,
        ExportOptions(
            transform=(
                util.transform_zup_to_yup.to_4x4()
                @ mathutils.Matrix.Scale(1 / util.DRAGEX(scene).oot.scale, 4)
            ),
            decomp_repo_p=decomp_repo_p,
        ),
    )
