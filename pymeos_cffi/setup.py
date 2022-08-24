from setuptools import setup

setup(
    packages=['pymeos_cffi'],
    setup_requires=['cffi'],
    cffi_modules=['pymeos_cffi/builder/build_pymeos.py:ffibuilder'],
)
