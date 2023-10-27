# ![MEOS Logo](https://raw.githubusercontent.com/MobilityDB/PyMEOS/master/docs/images/PyMEOS%20Logo.png)

[MEOS (Mobility Engine, Open Source)](https://www.libmeos.org/) is a C library which enables the manipulation of
temporal and spatio-temporal data based on [MobilityDB](https://mobilitydb.com/)'s data types and functions.

PyMEOS CFFI is a Python library that wraps the MEOS C library using CFFI, providing a set of python functions
that allows to use all MEOS functionality while automatically taking care of conversions between basic Python and C types
(such as Python's `str` to C's `char *`).  

This library is not meant to be used directly by the user, since most of the functions receive or return C objects 
(CFFI's `cdata` type).  

The [PyMEOS](../pymeos) library is built on top of this library and exposes all the functionality
of MEOS through a set of Python classes.

# Usage

## Installation

````shell
pip install pymeos-cffi
````

## Source installation
If the pre-built distribution is not available for your system, `pip` will try to make source distribution. For that, you will 
need to make sure you have the following requirements:

- C compiler
- [MEOS Library](https://www.libmeos.org/)

If the installation fails, you can submit an issue in the [PyMEOS issue tracker](https://github.com/MobilityDB/PyMEOS/issues)