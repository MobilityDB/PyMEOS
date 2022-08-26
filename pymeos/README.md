# Py![MEOS Logo](https://docs.mobilitydb.com/pub/meos-logo.png)

[MEOS (Mobility Engine, Open Source)](https://www.libmeos.org/) is a C library which enables the manipulation of 
temporal and spatio-temporal data based on [MobilityDB](https://mobilitydb.com/)'s data types and functions.  
PyMEOS is a Python library built on top of MEOS using CFFI which presents a set of classes to manipulate spatio-temporal 
information

# Usage

## Installation

````shell
pip install pymeos
````
> :warning: PyMEOS wheel should be compatible with any system, but it is possible that the pre-built distribution is 
> not available for PyMEOS CFFI for some OS/Architecture.  
> If it is not available, see the [source installation notes on PyMEOS CFFI's readme](../pymeos_cffi#installation) 
> on how to proceed

## Sample code

> :warning: **IMPORTANT** Before using any PyMEOS function, always call `meos_initialize`. Otherwise, the library will 
> crash with a `Segmentation Fault` error. You should also always call `meos_finish` at the end of your code.

````python
from pymeos import meos_initialize, meos_finish, TGeogPointInst, TGeogPointSeq

# Important: Always initialize MEOS library
meos_initialize()

sequence_from_string = TGeogPointSeq(string='[Point(10.0 10.0)@2019-09-01 00:00:00+01, Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')
print(f'Output: {sequence_from_string}')

sequence_from_points = TGeogPointSeq(instant_list=[TGeogPointInst(string='Point(10.0 10.0)@2019-09-01 00:00:00+01'), TGeogPointInst(string='Point(20.0 20.0)@2019-09-02 00:00:00+01'), TGeogPointInst(string='Point(10.0 10.0)@2019-09-03 00:00:00+01')], lower_inc=True, upper_inc=True)
speed = sequence_from_points.speed
print(f'Speeds: {speed}')

# Call finish at the end of your code
meos_finish()
````