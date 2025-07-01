#!/bin/sh
python3 -m venv .venv
. .venv/bin/activate
#python3 -m pip install --upgrade pip
#python3 -m pip install --upgrade build
python3 -m pip install --upgrade cibuildwheel
cd src/dragex_backend
cibuildwheel --only cp311-manylinux_x86_64
