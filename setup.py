from setuptools import setup

setup(
    name='pymeos',
    version='1.1',
    install_requires=['cffi'],
    setup_requires=['cffi'],
    cffi_modules=['build_pymeos.py:ffibuilder'],
)
