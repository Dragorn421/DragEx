# DragEx

DragEx is an addon for [Blender](https://www.blender.org/) 4.2+ for exporting
data like maps and rigged meshes for use in OoT64 modding.

It also has provisions for supporting other (Nintendo 64) targets (other
games), but only OoT64 is supported at present.

## Installing

DragEx can be installed
through [setting up its extension repository](#extension-repository)
or by [downloading from releases](#download).

### Extension repository

You can add the extension repository for DragEx by going in Blender to
Edit > Preferences > Get Extensions > [Repositories](https://docs.blender.org/manual/en/dev/editors/preferences/extensions.html#repositories) > + > Add Remote Repository

And supplying the URL of your choice:

- https://dragorn421.github.io/DragEx/ext_repo/latest/index.json (for latest release)
- https://dragorn421.github.io/DragEx/ext_repo/nightly/index.json (for nightly release)

You can also add repositories from the command line:

```sh
blender --command extension repo-add --name 'DragEx latest' --url https://dragorn421.github.io/DragEx/ext_repo/latest/index.json dragex_latest
blender --command extension repo-add --name 'DragEx nightly' --url https://dragorn421.github.io/DragEx/ext_repo/nightly/index.json dragex_nightly
```

You can add both latest and nightly repositories and choose later which version of DragEx to install.

After adding the DragEx extension repository, DragEx will be available for install in the extensions list.

### Download

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
Edit > Preferences > Get Extensions > (top-right down arrow) > [Install from Disk...](https://docs.blender.org/manual/en/dev/editors/preferences/extensions.html#bpy-ops-extensions-package-install-files)

## Development notes

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install black==25.1.0
pip install fake-bpy-module

ln -s $(realpath dragex_addon) ~/.config/blender/4.2/extensions/user_default/dragex
```

### Versioning

The version number is stored in `version.txt`. It uses [SemVer](https://semver.org/).

Note it should always be ahead of the latest (non-nightly) release.

### Releasing

To make a new release:

1. Create a release and associated tag on GitHub. Use the version from `version.txt`.
2. GitHub actions will automatically build and upload to the release.
3. Bump the version in `version.txt` (so that future nightly builds have higher precedence).
