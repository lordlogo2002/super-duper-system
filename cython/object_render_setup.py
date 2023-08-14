# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    name='object_render_cython',
    ext_modules=cythonize("object_render.pyx"),
    zip_safe=False,
)
