import time

from setuptools import Extension, setup

setup(
    version=f"0.0.1.dev{int(time.time())}",
    ext_modules=[
        Extension(
            name="dragex_backend",
            sources=[
                "src/main.c",
            ],
        ),
    ],
)
