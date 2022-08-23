# Py![MEOS Logo](./doc/images/meos-logo.png)

[MEOS (Mobility Engine, Open Source)](https://www.libmeos.org/) is a C library which enables the manipulation of
temporal and spatio-temporal data based on [MobilityDB](https://mobilitydb.com/)'s data types and functions.

PyMEOS is a library built on top of MEOS that provides all of its functionality wrapped in a set of Python classes.

This repository contains 3 subprojects:

- [PyMEOS CFFI](./pymeos_cffi): wrapper of the MEOS C Library built using CFFI.
- [PyMEOS](./pymeos): library that exposes the set of classes that should be used by the developer. Built on top of
  PyMEOS CFFI.
- [PyMEOS Examples](./pymeos_examples): set of example programs using PyMEOS.

# Usage

## Installation

````shell
pip install pymeos
````

> :warning: PyMEOS wheel should be compatible with any system, but it is possible that the pre-built distribution is 
> not available for PyMEOS CFFI for some OS/Architectures. If it is not available, see the [installation notes on PyMEOS CFFI's readme](./pymeos_cffi#installation) 
> on how to proceed

