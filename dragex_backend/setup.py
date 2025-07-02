import os

from setuptools import Extension, setup

setup(
    version=os.environ["DRAGEX_BACKEND_VERSION_STRING"],
    ext_modules=[
        Extension(
            name="dragex_backend",
            sources=[
                "src/main.c",
            ],
        ),
    ]
)
