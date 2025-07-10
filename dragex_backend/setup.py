from pathlib import Path

from setuptools import Extension, setup


BUILD_ID = int((Path(__file__).parent / "build_id.txt").read_text().strip())

setup(
    version=f"0.0.1.dev{BUILD_ID}",
    ext_modules=[
        Extension(
            name="dragex_backend",
            sources=[
                "src/py/main.c",
                "src/py/mat_info_image_obj.c",
                "src/py/mat_info_other_modes_obj.c",
                "src/py/mat_info_tile_obj.c",
                "src/py/mat_info_combiner_obj.c",
                "src/py/mat_info_vals_obj.c",
                "src/py/mat_info_geometry_mode_obj.c",
                "src/py/mat_info_obj.c",
                "src/py/mesh_info_obj.c",
                "src/exporter.c",
                "meshoptimizer/src/indexgenerator.cpp",
                "meshoptimizer/src/vcacheoptimizer.cpp",
            ],
            extra_compile_args=[
                # TODO only pass these args in ""development mode""
                "-Og",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-Wno-unused-parameter",
                "-UNDEBUG",
            ],
        ),
    ],
)
