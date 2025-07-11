from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


BUILD_ID = int((Path(__file__).parent / "build_id.txt").read_text().strip())


class CustomBuildExt(build_ext):
    def build_extensions(self):
        compiler = self.compiler.compiler_type
        print(f"Using compiler: {compiler}")

        for ext in self.extensions:
            # TODO only pass these args in ""development mode""
            if compiler == "msvc":
                ext.extra_compile_args = [
                    "/Od",
                    "/W4",
                    # "/WX",
                    "/U",
                    "NDEBUG",
                ]
            else:  # Assume GCC/Clang
                ext.extra_compile_args = [
                    "-Og",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-Wno-unused-parameter",
                    "-UNDEBUG",
                ]
        super().build_extensions()


setup(
    version=f"0.0.1.dev{BUILD_ID}",
    ext_modules=[
        Extension(
            name="dragex_backend",
            sources=[
                "src/logging/logging.c",
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
        ),
    ],
    cmdclass={"build_ext": CustomBuildExt},
)
