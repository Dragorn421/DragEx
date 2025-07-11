import argparse
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("blender_manifest")
    parser.add_argument("platform")
    parser.add_argument("wheels_pattern")
    args = parser.parse_args()

    blender_manifest = Path(args.blender_manifest).read_text()

    wheels = list(Path(".").glob(args.wheels_pattern))

    new_lines = []
    in_platforms_list = False
    in_wheels_list = False
    for l in blender_manifest.splitlines(keepends=True):
        if l.strip() == "# PLATFORMS START":
            in_platforms_list = True
            new_lines.append("    # PLATFORMS START\n")
            platform = args.platform
            assert '"' not in platform
            new_lines.append(f'    "{platform}",\n')
            new_lines.append("    # PLATFORMS END\n")
        elif l.strip() == "# PLATFORMS END":
            in_platforms_list = False
        elif l.strip() == "# WHEELS START":
            in_wheels_list = True
            new_lines.append("    # WHEELS START\n")
            for wheel in wheels:
                wheel = str(PurePosixPath(*wheel.parts))
                assert '"' not in wheel
                new_lines.append(f'    "{wheel}",\n')
            new_lines.append("    # WHEELS END\n")
        elif l.strip() == "# WHEELS END":
            in_wheels_list = False
        else:
            if not (in_platforms_list or in_wheels_list):
                new_lines.append(l)

    Path(args.blender_manifest).write_text("".join(new_lines))


if __name__ == "__main__":
    main()
