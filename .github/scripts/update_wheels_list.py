import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("blender_manifest")
    parser.add_argument("wheel")
    args = parser.parse_args()

    blender_manifest = Path(args.blender_manifest).read_text()

    new_lines = []
    in_wheels_list = False
    for l in blender_manifest.splitlines(keepends=True):
        if l.strip() == "# WHEELS START":
            in_wheels_list = True
            assert '"' not in args.wheel
            new_lines.append(f'    "{args.wheel}",\n')
        elif l.strip() == "# WHEELS END":
            in_wheels_list = False
        else:
            if not in_wheels_list:
                new_lines.append(l)

    Path(args.blender_manifest).write_text("".join(new_lines))


if __name__ == "__main__":
    main()
