```sh
python3 -m venv .venv
. .venv/bin/activate
pip install black==25.1.0
pip install fake-bpy-module
ln -s $(realpath src/dragex_addon) ~/.config/blender/4.2/scripts/addons/dragex
```
