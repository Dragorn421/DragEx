#!/bin/bash
set -e

python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade cibuildwheel
pushd dragex_backend
cibuildwheel --only cp311-manylinux_x86_64
popd
mkdir -p dragex_addon/wheels
cp dragex_backend/wheelhouse/*.whl dragex_addon/wheels/
