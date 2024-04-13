import os
import shutil

from setuptools import setup


package_data = []

# Conditionally copy PROJ DATA to make self-contained wheels
if os.environ.get("PACKAGE_DATA"):
    print("Copying PROJ data to package data")
    projdatadir = os.environ.get(
        "PROJ_DATA", os.environ.get("PROJ_LIB", "/usr/local/share/proj")
    )
    if os.path.exists(projdatadir):
        shutil.rmtree("pymeos_cffi/proj_data", ignore_errors=True)
        shutil.copytree(
            projdatadir,
            "pymeos_cffi/proj_data",
            ignore=shutil.ignore_patterns("*.txt", "*.tif"),
        )  # Don't copy .tiff files and their related .txt files
    else:
        raise FileNotFoundError(
            f"PROJ data directory not found at {projdatadir}. "
            f"Unable to generate self-contained wheel."
        )
    package_data.append("proj_data/*")
else:
    print("Not copying PROJ data to package data")

setup(
    packages=["pymeos_cffi", "pymeos_cffi.builder"],
    setup_requires=["cffi"],
    include_package_data=True,
    package_data={"pymeos_cffi": package_data},
    cffi_modules=["pymeos_cffi/builder/build_pymeos.py:ffibuilder"],
)
