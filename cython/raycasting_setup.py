from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

extensions = [
    Extension(
        "raycast", ["raycast.pyx"],
        extra_compile_args=["-O3", "-fPIC"],  # Optimization and Position Independent Code flags
    )
]

setup(
    ext_modules=cythonize(extensions, annotate=True, force=True, compiler_directives={
        'boundscheck': False,
        'wraparound': False,
        'nonecheck': False
    }),
)
