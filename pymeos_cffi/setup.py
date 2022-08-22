from setuptools import setup

setup(
    setup_requires=['cffi'],
    cffi_modules=['pymeos_cffi/builder/build_pymeos.py:ffibuilder'],
)
