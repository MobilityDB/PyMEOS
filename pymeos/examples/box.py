###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################

from mobilitydb import TBox, STBox

print("############################")
print('# Create new TBOX instances')
print("############################")

print('\n# Input string')

# Both value and time dimensions
var = TBox('TBOX((1.0, 2000-01-01), (2.0, 2000-01-02))')
print(var)
# Only value dimension
var = TBox('TBOX((1.0,), (2.0,))')
print(var)
# Only time dimension
var = TBox('TBOX((, 2000-01-01), (, 2000-01-02))')
print(var)

print('\n# Constructors')

# Both value and time dimensions
var = TBox(1.0, '2001-01-01', 2.0, '2001-01-02')
print(var)
# Only value dimension
var = TBox(1.0, 2.0)
print(var)
# Only time dimension
var = TBox('2001-01-01', '2001-01-02')
print(var)

print("\n############################")
print('# Create new STBOX instances')
print("############################")

print('\n# Input string')

# Only coordinate (X and Y) dimension
var = STBox('STBOX((1.0, 2.0), (1.0, 2.0))')
print(var)
# Only coordinate (X, Y and Z) dimension
var = STBox('STBOX Z((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))')
print(var)
# Both coordinate (X, Y) and time dimensions
var = STBox('STBOX T((1.0, 2.0, 2001-01-03), (1.0, 2.0, 2001-01-03))')
print(var)
# Both coordinate (X, Y, and Z) and time dimensions
var = STBox('STBOX ZT((1.0, 2.0, 3.0, 2001-01-04), (1.0, 2.0, 3.0, 2001-01-04))')
print(var)
# Only time dimension
var = STBox('STBOX T(( , , 2001-01-03), ( , , 2001-01-03))')
print(var)
# Only geodetic coordinate (X, Y and Z) dimension
var = STBox('GEODSTBOX((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))')
print(var)
#  Both geodetic coordinate (X, Y, and Z) and time dimensions
var = STBox('GEODSTBOX T((1.0, 2.0, 3.0, 2001-01-04), (1.0, 2.0, 3.0, 2001-01-04))')
print(var)
# Only time dimension for geodetic box
var = STBox('GEODSTBOX T(( , , 2001-01-03), ( , , 2001-01-03))')
print(var)

print('\n# Constructors')

# Only coordinate (X and Y) dimension
var = STBox((1.0, 2.0, 1.0, 2.0))
print(var)
# Only coordinate (X, Y and Z) dimension
var = STBox((1.0, 2.0, 3.0, 1.0, 2.0, 3.0))
print(var)
# Both coordinate (X, Y) and time dimensions
var = STBox((1.0, 2.0, '2001-01-03', 1.0, 2.0, '2001-01-03'), dimt=True)
print(var)
# Both coordinate (X, Y, and Z) and time dimensions
var = STBox((1.0, 2.0, 3.0, '2001-01-04', 1.0, 2.0, 3.0, '2001-01-04'))
print(var)
# Only time dimension
var = STBox(('2001-01-03', '2001-01-03'))
print(var)
# Only geodetic coordinate (X, Y and Z) dimension
var = STBox((1.0, 2.0, 3.0, 1.0, 2.0, 3.0), geodetic=True)
print(var)
#  Both geodetic coordinate (X, Y, and Z) and time dimensions
var = STBox((1.0, 2.0, 3.0, '2001-01-04', 1.0, 2.0, 3.0, '2001-01-03'), geodetic=True)
print(var)
# Only time dimension for geodetic box
var = STBox(('2001-01-03', '2001-01-03'), geodetic=True)
print(var)

