import argparse
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("blender_manifest_in")
    parser.add_argument("blender_manifest_out")
    parser.add_argument("blender_version_min")
    parser.add_argument("blender_version_max")
    parser.add_argument("platform")
    parser.add_argument("wheels_pattern")
    args = parser.parse_args()

    blender_manifest = Path(args.blender_manifest_in).read_text()

    assert '"' not in args.blender_version_min
    blender_manifest = blender_manifest.replace(
        "# @blender_version_min_line@",
        f'blender_version_min = "{args.blender_version_min}"',
    )

    assert '"' not in args.blender_version_max
    blender_manifest = blender_manifest.replace(
        "# @blender_version_max_line@",
        (
            ""
            if args.blender_version_max == "None"
            else f'blender_version_max = "{args.blender_version_max}"'
        ),
    )

    assert '"' not in args.platform
    blender_manifest = blender_manifest.replace(
        "# @platforms_list@",
        f'    "{args.platform}",',
    )

    wheels_paths = list(Path(".").glob(args.wheels_pattern))
    wheels_list = [str(PurePosixPath(*wheel_p.parts)) for wheel_p in wheels_paths]
    assert all('"' not in wheel for wheel in wheels_list)
    blender_manifest = blender_manifest.replace(
        "# @wheels_list@",
        "\n".join(f'    "{wheel}",' for wheel in wheels_list),
    )

    Path(args.blender_manifest_out).write_text(blender_manifest)


if __name__ == "__main__":
    main()
