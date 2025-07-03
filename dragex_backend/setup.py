from pathlib import Path

from setuptools import Extension, setup


BUILD_ID = int((Path(__file__).parent / "build_id.txt").read_text().strip())

setup(
    version=f"0.0.1.dev{BUILD_ID}",
    ext_modules=[
        Extension(
            name="dragex_backend",
            sources=[
                "src/main.c",
                "src/exporter.c",
                "meshoptimizer/src/indexgenerator.cpp",
                "meshoptimizer/src/vcacheoptimizer.cpp",
            ],
            extra_compile_args=["-Og"],
        ),
    ],
)
