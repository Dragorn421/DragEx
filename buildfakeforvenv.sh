#!/bin/bash
set -e

python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
pushd dragex_backend
python3 -m build
popd
pip uninstall --yes dragex_backend
python3 -m pip install dragex_backend/dist/*.whl
