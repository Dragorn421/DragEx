import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("blender_manifest")
    parser.add_argument("wheels_pattern")
    args = parser.parse_args()

    blender_manifest = Path(args.blender_manifest).read_text()

    wheels = list(Path(".").glob(args.wheels_pattern))

    new_lines = []
    in_wheels_list = False
    for l in blender_manifest.splitlines(keepends=True):
        if l.strip() == "# WHEELS START":
            in_wheels_list = True
            new_lines.append("    # WHEELS START\n")
            for wheel in wheels:
                wheel = str(wheel)
                assert '"' not in wheel
                new_lines.append(f'    "{wheel}",\n')
            new_lines.append("    # WHEELS END\n")
        elif l.strip() == "# WHEELS END":
            in_wheels_list = False
        else:
            if not in_wheels_list:
                new_lines.append(l)

    Path(args.blender_manifest).write_text("".join(new_lines))


if __name__ == "__main__":
    main()
