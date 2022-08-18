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

from dateutil.parser import parse

from pymeos_cffi.functions import tbox_in, floatspan_make, tbox_make, tbox_out, tbox_eq, tbox_hasx, tbox_hast, \
    tbox_xmin, tbox_tmin, timestamptz_to_datetime, tbox_tmax, tbox_xmax, tbox_expand, tbox_expand_value, \
    tbox_expand_temporal, timedelta_to_interval, tbox_shift_tscale
from ..time.period import Period

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class TBox:
    """
    Class for representing bounding boxes with value (``X``) and/or time (``T``)
    dimensions.


    ``TBox`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TBox(string="TBOX((1.0, 2000-01-01), (2.0, 2000-01-02))")
        >>> TBox(string="TBOX((1.0,), (2.0,))")
        >>> TBox(string="TBOX((, 2000-01-01), (, 2000-01-02))")

    Another possibility is to give the bounds in the following order:
    ``xmin``, ``tmin``, ``xmax``, ``tmax``, where the bounds can be
    instances of ``str``, ``float`` or ``datetime``. All arguments are
    optional but they must be given in pairs for each dimension and at
    least one pair must be given.

        >>> TBox(xmin="1.0", tmin="2000-01-01", xmax="2.0", tmax="2000-01-02")
        >>> TBox(xmin=1.0, xmax=2.0)
        >>> TBox(tmin=parse("2000-01-01"), tmax=parse("2000-01-02"))

    """
    __slots__ = ['_inner']

    def __init__(self, *, string: Optional[str] = None,
                 xmin: Optional[Union[str, float]] = None,
                 tmin: Optional[Union[str, datetime]] = None,
                 xmax: Optional[Union[str, float]] = None,
                 tmax: Optional[Union[str, datetime]] = None,
                 _inner=None):
        assert (_inner is not None) or (string is not None) != (
                (xmin is not None and xmax is not None) or (tmin is not None and tmax is not None)), \
            "Either string must be not None or at least a bound pair (xmin/max or tmin/max) must be not None"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = tbox_in(string)
        else:
            span = None
            period = None
            if xmin is not None and xmax is not None:
                span = floatspan_make(float(xmin), float(xmax), True, True)
            if tmin is not None and tmax is not None:
                period = Period(lower=tmin, upper=tmax, lower_inc=True, upper_inc=True)._inner
            self._inner = tbox_make(period, span)

    @property
    def has_x(self):
        return tbox_hasx(self._inner)

    @property
    def has_t(self):
        return tbox_hast(self._inner)

    @property
    def xmin(self):
        """
        Minimum X
        """
        return tbox_xmin(self._inner)

    @property
    def tmin(self):
        """
        Minimum T
        """
        return timestamptz_to_datetime(tbox_tmin(self._inner))

    @property
    def xmax(self):
        """
        Maximum X
        """
        return tbox_xmax(self._inner)

    @property
    def tmax(self):
        """
        Maximum T
        """
        return timestamptz_to_datetime(tbox_tmax(self._inner))

    def expand(self, other: Union[TBox, float, timedelta]) -> None:
        if isinstance(other, TBox):
            tbox_expand(other._inner, self._inner)
        elif isinstance(other, float):
            self._inner = tbox_expand_value(self._inner, other)
        elif isinstance(other, timedelta):
            self._inner = tbox_expand_temporal(self._inner, timedelta_to_interval(other))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def shift(self, shift: timedelta) -> None:
        tbox_shift_tscale(timedelta_to_interval(shift), None, self._inner)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            tbox_eq(self._inner, other._inner)
        return False

    def __str__(self):
        return tbox_out(self._inner, 3)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return TBox(string=value)

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    # End Psycopg2 interface.
