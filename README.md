# DragEx

DragEx is an addon for [Blender](https://www.blender.org/) 4.2+ for exporting
data like maps and rigged meshes for use in OoT64 modding.

It also has provisions for supporting other (Nintendo 64) targets (other
games), but only OoT64 is supported at present.

## Installing

Downloads are available on the
[releases page](https://github.com/Dragorn421/DragEx/releases).

As the addon is partly written in C and compiled, you need to download the right
version of the addon corresponding to your operating system and Blender version.

The downloads are named like `dragex-PYTHON-TARGET-COMMIT.zip`, where
- `PYTHON` is the target version of Python, like `cp311`. It needs to match your
  Blender version's Python.
- `TARGET` is a combination of the target operating system and CPU, like `win_amd64` for x86_64 Windows.
- `COMMIT` is the hash of the corresponding commit.

If you are using a version of Blender from 4.2 to 5.0 (inclusive), you need
`PYTHON`=`cp311`.

If you are using a version of Blender from 5.1 to above (inclusive), you need
`PYTHON`=`cp313`.

There currently are only builds for x86_64 CPUs, but it should be trivial to add
more (feel free to open an issue).

If you are on Windows, you need `TARGET`=`win_amd64`.

If you are on Linux, you need `TARGET`=`manylinux_x86_64`.

Once you have downloaded the zip, you can install it by going in Blender to
Edit > Preferences > Get Extensions > (top-right down arrow) > Install from Disk...

## Development notes

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install black==25.1.0
pip install fake-bpy-module

ln -s $(realpath dragex_addon) ~/.config/blender/4.2/extensions/user_default/dragex
```

### Versioning

The version number is stored in `version.txt`. It uses [SemVer](https://semver.org/). Note it should always be ahead of the latest (non-nightly) release.

### Releasing

To make a new release:

1. Create a release and associated tag on GitHub. Use the version from `version.txt`.
2. GitHub actions will automatically build and upload to the release.
3. Bump the version in `version.txt` (so that future nightly builds have higher precedence).
