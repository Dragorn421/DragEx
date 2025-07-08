#!/bin/sh

set -ex

black .

# python3 -m venv black23.venv
# black23.venv/bin/pip install 'black>=23,<24'
black23.venv/bin/black dragex_addon/f64render_dragex
