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

from datetime import datetime
from dateutil.parser import parse
import warnings

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

        >>> TBox("TBOX((1.0, 2000-01-01), (2.0, 2000-01-02))")
        >>> TBox("TBOX((1.0,), (2.0,))")
        >>> TBox("TBOX((, 2000-01-01), (, 2000-01-02))")

    Another possibility is to give the bounds in the following order:
    ``xmin``, ``tmin``, ``xmax``, ``tmax``, where the bounds can be
    instances of ``str``, ``float`` or ``datetime``. All arguments are
    optional but they must be given in pairs for each dimension and at
    least one pair must be given.

        >>> TBox("1.0", "2000-01-01", "2.0", "2000-01-02")
        >>> TBox(1.0, 2.0)
        >>> TBox(parse("2000-01-01"), parse("2000-01-02"))

    """
    __slots__ = ['_xmin', '_tmin', '_xmax', '_tmax']

    def __init__(self, xmin, tmin=None, xmax=None, tmax=None):
        if tmin is None and isinstance(xmin, str):
            self.parse_from_string(xmin)
        elif tmin is None and isinstance(xmin, (tuple, list)):
            xmin, tmin, *extra = xmin
            if extra:
                xmax, tmax, *extra = extra
                if extra:
                    raise Exception("ERROR: Cannot parse TBox")
        elif xmax is None:
            # Only two arguments given
            if isinstance(xmin, str) and isinstance(tmin, str):
                try:
                    self._xmin = float(xmin)
                    self._xmax = float(tmin)
                    self._tmin = self._tmax = None
                except:
                    self._tmin = parse(xmin)
                    self._tmax = parse(tmin)
                    self._xmin = self._xmax = None
            elif isinstance(xmin, float) and isinstance(tmin, float):
                self._xmin = xmin
                self._xmax = tmin
                self._tmin = self._tmax = None
            elif isinstance(xmin, datetime) and isinstance(tmin, datetime):
                self._tmin = xmin
                self._tmax = tmin
                self._xmin = self._xmax = None
            else:
                raise Exception("ERROR: Cannot parse TBox")
        else:
            # Four arguments given
            self._xmin = float(xmin)
            self._xmax = float(xmax)
            if isinstance(tmin, str) and isinstance(tmax, str):
                self._tmin = parse(tmin)
                self._tmax = parse(tmax)
            elif isinstance(tmin, datetime) and isinstance(tmax, datetime):
                self._tmin = tmin
                self._tmax = tmax
            else:
                raise Exception("ERROR: Cannot parse TBox")

    def parse_from_string(self, value):
        values = value.replace("TBOX", '')
        if 'T' in values:
            time = True
            self._xmin = None
            self._xmax = None
        else:
            time = False
        values = values.replace('T', '').replace('(', '').replace(')', '').split(',')
        if time:
            self._tmin = parse(values[0])
            self._tmax = parse(values[1])
        elif len(values) == 4:
            self._xmin = float(values[0]) if values[0] != '' and not values[0].isspace() else None
            self._xmax = float(values[2]) if values[2] != '' and not values[2].isspace() else None
            self._tmin = parse(values[1]) if values[1] != '' and not values[1].isspace() else None
            self._tmax = parse(values[3]) if values[3] != '' and not values[3].isspace() else None
        else:
            raise Exception("ERROR: Cannot parse TBox")

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return TBox(value)

    @staticmethod
    def write(value):
        if not isinstance(value, TBox):
            raise ValueError('Value must be an instance of TBox class')
        return value.__str__().strip("'")

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    def getquoted(self):
        return "{}".format(self.__str__())
    # End Psycopg2 interface.

    @property
    def xmin(self):
        """
        Minimum X
        """
        return self._xmin

    @property
    def tmin(self):
        """
        Minimum T
        """
        return self._tmin

    @property
    def xmax(self):
        """
        Maximum X
        """
        return self._xmax

    @property
    def tmax(self):
        """
        Maximum T
        """
        return self._tmax

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._xmin == other._xmin and self._tmin == other._tmin and self._xmax == other._xmax and \
                self._tmax == other._tmax
        return False

    def __str__(self):
        if self._xmin is not None and self._tmin is not None:
            return "'TBOX((%s, %s), (%s, %s))'" % (repr(self._xmin), self._tmin, repr(self._xmax), self._tmax)
        elif self._xmin is not None:
            return "'TBOX((%s, ), (%s, ))'" % (repr(self._xmin), repr(self._xmax))
        elif self._tmin is not None:
            return "'TBOX((, %s), (, %s))'" % (self._tmin, self._tmax)

    def __repr__(self):
        return (f'{self.__class__.__name__ }'
                f'({self._xmin!r}, {self._tmin!r}, {self._xmax!r}, {self._tmax!r})')

