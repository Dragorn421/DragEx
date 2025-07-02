```sh
python3 -m venv .venv
. .venv/bin/activate
pip install black==25.1.0
pip install fake-bpy-module

# seems jank wrt wheels? no longer using symlinks, trying zip and install (was using 4.2.0, going back to symlinks after upgrade to 4.2.11)
ln -s $(realpath dragex_addon) ~/.config/blender/4.2/extensions/user_default/dragex
```

```sh
# needed this at one point, to force blender to forget the wheel install?
# but then it didn't reinstall them idk (was using 4.2.0 though, upgrading to 4.2.11 seems to have fixed it)
rm -r ~/.config/blender/4.2/extensions/.local/lib/python3.11/site-packages
```
