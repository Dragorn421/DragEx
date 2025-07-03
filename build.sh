#!/bin/bash
set -e

python3 -m venv .venv
. .venv/bin/activate
python3 .github/scripts/gen_build_id.py
python3 -m pip install cibuildwheel==3.0.0
pushd dragex_backend
rm -rf wheelhouse
cibuildwheel --only cp311-manylinux_x86_64
popd
rm -rf dragex_addon/wheels
mkdir -p dragex_addon/wheels
cp dragex_backend/wheelhouse/*.whl dragex_addon/wheels/
pushd dragex_addon
python3 ../.github/scripts/update_wheels_list.py blender_manifest.toml wheels/*.whl
popd

#blender=/home/dragorn421/blender_collection/blender-4.2.11-linux-x64/blender
#$blender --command extension build --source-dir dragex_addon --output-filepath dragex-dev.zip
#$blender --command extension install-file -r user_default dragex-dev.zip
