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
from __future__ import annotations

import warnings
from datetime import datetime, timedelta
from typing import Optional, Union

from pymeos_cffi.functions import stbox_in, stbox_make, stbox_eq, stbox_out, stbox_isgeodetic, stbox_hasx, stbox_hast, \
    stbox_hasz, stbox_xmin, stbox_ymin, stbox_zmin, timestamptz_to_datetime, stbox_tmin, stbox_xmax, stbox_ymax, \
    stbox_zmax, stbox_tmax, stbox_expand, stbox_expand_spatial, stbox_expand_temporal, timedelta_to_interval, \
    stbox_shift_tscale, stbox_set_srid
from ..time.period import Period

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class STBox:
    """
    Class for representing bounding boxes composed of coordinate and/or time
    dimensions, where the coordinates may be in 2D (``X`` and ``Y``) or in 3D
    (``X``, ``Y``, and ``Z``). For each dimension, minimum and maximum values
    are stored. The coordinates may be either Cartesian (planar) or geodetic
    (spherical). Additionally, the SRID of coordinates can be specified.


    ``STBox`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> "STBOX ((1.0, 2.0), (1.0, 2.0))",
        >>> "STBOX Z((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))",
        >>> "STBOX T((1.0, 2.0, 2001-01-03 00:00:00+01), (1.0, 2.0, 2001-01-03 00:00:00+01))",
        >>> "STBOX ZT((1.0, 2.0, 3.0, 2001-01-04 00:00:00+01), (1.0, 2.0, 3.0, 2001-01-04 00:00:00+01))",
        >>> "STBOX T(, 2001-01-03 00:00:00+01), (, 2001-01-03 00:00:00+01))",
        >>> "GEODSTBOX((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))",
        >>> "GEODSTBOX T((1.0, 2.0, 3.0, 2001-01-03 00:00:00+01), (1.0, 2.0, 3.0, 2001-01-04 00:00:00+01))",
        >>> "GEODSTBOX T((, 2001-01-03 00:00:00+01), (, 2001-01-03 00:00:00+01))",
        >>> "SRID=5676;STBOX T((1.0, 2.0, 2001-01-04), (1.0, 2.0, 2001-01-04))",
        >>> "SRID=4326;GEODSTBOX((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))",

    Another possibility is to give the bounds in the following order:
    ``xmin``, ``ymin``, ``zmin``, ``tmin``, ``xmax``, ``ymax``, ``zmax``,
    ``tmax``, where the bounds can be instances of ``str``, ``float``
    and ``datetime``. All arguments are optional but they must be given
    in pairs for each dimension and at least one pair must be given.
    When three pairs are given, by default, the third pair will be
    interpreted as representing the ``Z`` dimension unless the ``dimt``
    parameter is given. Finally, the ``geodetic`` parameter determines
    whether the coordinates in the bounds are planar or spherical.

        >>> STBox((1.0, 2.0, 1.0, 2.0))
        >>> STBox((1.0, 2.0, 3.0, 1.0, 2.0, 3.0))
        >>> STBox((1.0, 2.0, '2001-01-03', 1.0, 2.0, '2001-01-03'), dimt=True)
        >>> STBox((1.0, 2.0, 3.0, '2001-01-04', 1.0, 2.0, 3.0, '2001-01-04'))
        >>> STBox(('2001-01-03', '2001-01-03'))
        >>> STBox((1.0, 2.0, 3.0, 1.0, 2.0, 3.0), geodetic=True)
        >>> STBox((1.0, 2.0, 3.0, '2001-01-04', 1.0, 2.0, 3.0, '2001-01-03'), geodetic=True)
        >>> STBox((1.0, 2.0, 3.0, '2001-01-04', 1.0, 2.0, 3.0, '2001-01-03'), geodetic=True, srid=4326)
        >>> STBox(('2001-01-03', '2001-01-03'), geodetic=True)

    """
    __slots__ = ['_inner']

    def __init__(self, *, string: Optional[str] = None,
                 xmin: Optional[Union[str, float]] = None, xmax: Optional[Union[str, float]] = None,
                 ymin: Optional[Union[str, float]] = None, ymax: Optional[Union[str, float]] = None,
                 zmin: Optional[Union[str, float]] = None, zmax: Optional[Union[str, float]] = None,
                 tmin: Optional[Union[str, datetime]] = None, tmax: Optional[Union[str, datetime]] = None,
                 geodetic: bool = False, srid: Optional[int] = None,
                 _inner=None):

        assert (_inner is not None) or (string is not None) != (
                (xmin is not None and xmax is not None and ymin is not None and ymax is not None) or
                (tmin is not None and tmax is not None)), \
            "Either string must be not None or at least a bound pair (xmin/max and ymin/max, or tmin/max)" \
            " must be not None"

        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = stbox_in(string)
        else:
            period = None
            hast = tmin is not None and tmax is not None
            hasx = xmin is not None and xmax is not None and ymin is not None and ymax is not None
            hasz = zmin is not None and zmax is not None
            if hast:
                period = Period(lower=tmin, upper=tmax, lower_inc=True, upper_inc=True)._inner
            self._inner = stbox_make(period, hasx, hasz, geodetic, srid or 0, float(xmin or 0), float(xmax or 0),
                                     float(ymin or 0), float(ymax or 0), float(zmin or 0), float(zmax or 0))

    @property
    def has_x(self):
        return stbox_hasx(self._inner)

    @property
    def has_z(self):
        return stbox_hasz(self._inner)

    @property
    def has_t(self):
        return stbox_hast(self._inner)

    @property
    def geodetic(self):
        """
        Is the box is geodetic?
        """
        return stbox_isgeodetic(self._inner)

    @property
    def xmin(self):
        """
        Minimum X
        """
        return stbox_xmin(self._inner)

    @property
    def ymin(self):
        """
        Minimum Y
        """
        return stbox_ymin(self._inner)

    @property
    def zmin(self):
        """
        Minimum Z
        """
        return stbox_zmin(self._inner)

    @property
    def tmin(self):
        """
        Minimum T
        """
        return timestamptz_to_datetime(stbox_tmin(self._inner))

    @property
    def xmax(self):
        """
        Maximum X
        """
        return stbox_xmax(self._inner)

    @property
    def ymax(self):
        """
        Maximum Y
        """
        return stbox_ymax(self._inner)

    @property
    def zmax(self):
        """
        Maximum Z
        """
        return stbox_zmax(self._inner)

    @property
    def tmax(self):
        """
        Maximum T
        """
        return timestamptz_to_datetime(stbox_tmax(self._inner))

    @property
    def srid(self):
        """
        SRID of the geographic coordinates
        """
        return self._inner.srid

    @srid.setter
    def srid(self, value: int):
        self._inner = stbox_set_srid(self._inner, value)

    def expand(self, other: Union[STBox, float, timedelta]) -> None:
        if isinstance(other, STBox):
            stbox_expand(other._inner, self._inner)
        elif isinstance(other, float):
            self._inner = stbox_expand_spatial(self._inner, other)
        elif isinstance(other, timedelta):
            self._inner = stbox_expand_temporal(self._inner, timedelta_to_interval(other))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def shift(self, shift: timedelta) -> None:
        stbox_shift_tscale(timedelta_to_interval(shift), None, self._inner)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return stbox_eq(self._inner, other._inner)
        return False

    def __str__(self):
        return stbox_out(self._inner, 3)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return STBox(string=value)

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    # End Psycopg2 interface.
