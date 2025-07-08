# This is a script to convert shader/defines.glsl to pydefines.py

from pathlib import Path

pydefines = list[str]()

pydefines.append("# This file was auto-generated from ../shader/defines.glsl by " + Path(__file__).name)

for l in (Path(__file__).parent.parent / "shader/defines.glsl").read_text().splitlines():
    l = l.replace("//", "#")
    if l.startswith("#define"):
        toks = l.split(maxsplit=2)
        assert len(toks) == 3, l
        l = toks[1] + " = " + toks[2]
    pydefines.append(l)

(Path(__file__).parent / "pydefines.py").write_text("".join(f"{l}\n" for l in pydefines))
