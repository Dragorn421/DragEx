#!/bin/bash
set -e

. .venv/bin/activate
python3 .github/scripts/gen_build_id.py
pip install dragex_backend/
python3 test.py
