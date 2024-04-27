# ![MEOS Logo](https://raw.githubusercontent.com/MobilityDB/PyMEOS/master/docs/images/PyMEOS%20Logo.png)

[![pypi](https://img.shields.io/pypi/v/pymeos.svg)](https://pypi.python.org/pypi/pymeos/)
[![docs status](https://readthedocs.org/projects/pymeos/badge/?version=latest)](https://pymeos.readthedocs.io/en/latest/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[MEOS (Mobility Engine, Open Source)](https://www.libmeos.org/) is a C library which enables the manipulation of
temporal and spatio-temporal data based on [MobilityDB](https://mobilitydb.com/)'s data types and functions.

PyMEOS is a library built on top of MEOS that provides all of its functionality wrapped in a set of Python classes.

For the PyMEOS CFFI library, the middle layer between MEOS and PyMEOS, see
the [PyMEOS CFFI repository](https://github.com/MobilityDB/PyMEOS-CFFI).

# Usage

## Installation

You can install PyMEOS (`pymeos` and `pymeos-cffi`) using `pip`, `conda`, or from sources.

### Using pip

````shell
pip install pymeos
````

> PyMEOS wheel should be compatible with any system, but it is possible that the pre-built distribution is
> not available for PyMEOS CFFI for some OS/Architecture.

### Using conda

PyMEOS is also available on the conda-forge channel. To install it, first add the conda-forge channel to your conda
configuration:

````shell
conda config --add channels conda-forge
conda config --set channel_priority strict
````

Then, you can install PyMEOS using the following command:

````shell
conda install conda-forge::pymeos
````

### Source installation

For detailed instructions on how to install PyMEOS from sources, see
the [installation page](https://pymeos.readthedocs.io/en/latest/src/installation.html#) in the PyMEOS Documentation.

## Sample code

> **IMPORTANT** Before using any PyMEOS function, always call `pymeos_initialize`. Otherwise, the library will
> crash with a `Segmentation Fault` error. You should also always call `pymeos_finalize` at the end of your code.

````python
from pymeos import pymeos_initialize, pymeos_finalize, TGeogPointInst, TGeogPointSeq

# Important: Always initialize MEOS library
pymeos_initialize()

sequence_from_string = TGeogPointSeq(
    string='[Point(10.0 10.0)@2019-09-01 00:00:00+01, Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')
print(f'Output: {sequence_from_string}')

sequence_from_points = TGeogPointSeq(instant_list=[TGeogPointInst(string='Point(10.0 10.0)@2019-09-01 00:00:00+01'),
                                                   TGeogPointInst(string='Point(20.0 20.0)@2019-09-02 00:00:00+01'),
                                                   TGeogPointInst(string='Point(10.0 10.0)@2019-09-03 00:00:00+01')],
                                     lower_inc=True, upper_inc=True)
speed = sequence_from_points.speed()
print(f'Speeds: {speed}')

# Call finish at the end of your code
pymeos_finalize()
````

````
Output: [POINT(10 10)@2019-09-01 01:00:00+02, POINT(20 20)@2019-09-02 01:00:00+02, POINT(10 10)@2019-09-03 01:00:00+02]
Speeds: Interp=Step;[17.84556057812839@2019-09-01 01:00:00+02, 17.84556057812839@2019-09-03 01:00:00+02]
````

For more examples and use-cases, see [PyMEOS Examples repository](https://github.com/MobilityDB/PyMEOS-Examples)

# Documentation

Visit our [ReadTheDocs page](https://pymeos.readthedocs.io/en/latest/) for a more complete and detailed documentation,
including an installation manual and several examples.