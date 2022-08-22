from setuptools import setup

setup(
    install_requires=['cffi'],
    setup_requires=['cffi'],
    cffi_modules=['pymeos_cffi/builder/build_pymeos.py:ffibuilder'],
)
