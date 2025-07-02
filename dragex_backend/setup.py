from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            name="dragex_backend",
            sources=[
                "src/main.c",
            ],
            extra_compile_args=["-g"],
        ),
    ]
)
