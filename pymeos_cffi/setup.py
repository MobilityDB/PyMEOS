import os
import shutil

from setuptools import setup


def copy_data_tree(source, destination):
    try:
        shutil.rmtree(destination)
    except OSError:
        pass
    shutil.copytree(source, destination)


package_data = []

# Conditionally copy PROJ DATA to make self-contained wheels
if os.environ.get("PACKAGE_DATA"):
    projdatadir = os.environ.get(
        "PROJ_DATA", os.environ.get("PROJ_LIB", "/usr/local/share/proj")
    )
    if os.path.exists(projdatadir):
        copy_data_tree(projdatadir, "pymeos_cffi/proj_data")
    else:
        raise FileNotFoundError(
            f"PROJ data directory not found at {projdatadir}. "
            f"Unable to generate self-contained wheel."
        )
    package_data.append("proj_data/*")

setup(
    packages=["pymeos_cffi", "pymeos_cffi.builder"],
    setup_requires=["cffi"],
    package_data={"pymeos_cffi": package_data},
    cffi_modules=["pymeos_cffi/builder/build_pymeos.py:ffibuilder"],
)
