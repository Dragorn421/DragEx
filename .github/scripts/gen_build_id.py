from pathlib import Path
import time

build_id = int(time.time())

Path("dragex_addon/build_id.py").write_text(f"BUILD_ID = {build_id}\n")
Path("dragex_backend/build_id.txt").write_text(f"{build_id}\n")
Path("dragex_backend/build_id.h").write_text(f"#define BUILD_ID {build_id}\n")
