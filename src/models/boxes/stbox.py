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
    __slots__ = ['_xmin', '_ymin', '_zmin', '_tmin', '_xmax', '_ymax', '_zmax', '_tmax', '_geodetic', '_srid']

    def __init__(self, bounds, dimt=None, geodetic=None, srid=None):
        # Initialize arguments to None and set geodetic if given
        self._xmin = self._ymin = self._zmin = self._tmin = None
        self._xmax = self._ymax = self._zmax = self._tmax = None
        assert(geodetic is None or isinstance(geodetic, bool)), "ERROR: Geodetic parameter must be Boolean"
        self._geodetic = geodetic if geodetic is not None else False
        assert(srid is None or isinstance(srid, int)), "ERROR: SRID parameter must be Integer"
        self._srid = srid if srid is not None else False
        # Unpack the bounds
        if isinstance(bounds, str):
            self.parse_from_string(bounds)
            return
        if isinstance(bounds, (tuple, list)):
            xmin = ymin = zmin = tmin = None
            xmax = ymax = zmax = tmax = None
            if len(bounds) == 2:
                tmin, tmax = bounds
            elif len(bounds) == 4:
                xmin, ymin, xmax, ymax = bounds
            elif len(bounds) == 6:
                if dimt:
                    xmin, ymin, tmin, xmax, ymax, tmax = bounds
                else:
                    xmin, ymin, zmin, xmax, ymax, zmax = bounds
            elif len(bounds) == 8:
                xmin, ymin, zmin, tmin, xmax, ymax, zmax, tmax = bounds
            else:
                raise Exception("ERROR: Cannot parse STBox")
        # Initialize the new instance
        self._xmin = float(xmin) if xmin is not None else None
        self._xmax = float(xmax) if xmax is not None else None
        self._ymin = float(ymin) if ymin is not None else None
        self._ymax = float(ymax) if ymax is not None else None
        self._zmin = float(zmin) if zmin is not None else None
        self._zmax = float(zmax) if zmax is not None else None
        if tmin is not None and tmax is not None:
            if isinstance(tmin, str) and isinstance(tmax, str):
                self._tmin = parse(tmin)
                self._tmax = parse(tmax)
            elif isinstance(tmin, datetime) and isinstance(tmax, datetime):
                self._tmin = tmin
                self._tmax = tmax
            else:
                raise Exception("ERROR: Cannot parse STBox")

    def parse_from_string(self, value):
        if value is None or not isinstance(value, str):
            raise Exception("ERROR: Cannot parse STBox")
        value = value.strip()
        values = None

        # SRID, if specified would be at start of the value. Example:
        #   SRID=4326;GEODSTBOX((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))
        if value.startswith("SRID"):
            srid, _stbox = value.split(";")
            srid = int(srid.split('=')[1])
            self._srid = srid
            value = _stbox

        if 'GEODSTBOX' in value:
            self._geodetic = True
            value = value.replace("GEODSTBOX", '')
            hasz = True
            hast = True if 'T' in value else False
        elif 'STBOX' in value:
            value = value.replace("STBOX", '')
            hasz = True if 'Z' in value else False
            hast = True if 'T' in value else False
        else:
            raise Exception("ERROR: Input must be STBOX")

        values = value.replace('Z', '').replace('T', ''). replace('(', '').replace(')', '').split(',')
        # Remove empty or only space strings
        values = [value for value in values if value != '' and not value.isspace()]

        if len(values) == 2:
            self._tmin = parse(values[0])
            self._tmax = parse(values[1])
        else:
            if len(values) >= 4:
                self._xmin = float(values[0])
                self._xmax = float(values[int(len(values) / 2)])
                self._ymin = float(values[1])
                self._ymax = float(values[1 + int(len(values) / 2)])
            if hasz:
                self._zmin = float(values[2])
                self._zmax = float(values[2 + int(len(values) / 2)])
            if hast:
                self._tmin = parse(values[int(len(values) / 2) - 1])
                self._tmax = parse(values[(int(len(values) / 2) - 1) + int(len(values) / 2)])

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return STBox(value)

    @staticmethod
    def write(value):
        if not isinstance(value, STBox):
            raise ValueError('Value must be an instance of STBox class')
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
    def ymin(self):
        """
        Minimum Y
        """
        return self._ymin

    @property
    def zmin(self):
        """
        Minimum Z
        """
        return self._ymin

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
    def ymax(self):
        """
        Maximum Y
        """
        return self._ymax

    @property
    def zmax(self):
        """
        Maximum Z
        """
        return self._zmax

    @property
    def tmax(self):
        """
        Maximum T
        """
        return self._tmax

    @property
    def geodetic(self):
        """
        Is the box is geodetic?
        """
        return self._geodetic

    @property
    def srid(self):
        """
        SRID of the geographic coordinates
        """
        return self._srid

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._xmin == other._xmin and self._ymin == other._ymin and self._zmin == other._zmin and \
                   self._tmin == other._tmin and self._xmax == other._xmax and self._ymax == other._ymax and \
                   self._zmax == other._zmax and self._tmax == other._tmax and self._geodetic == other._geodetic
        return False

    def __str__(self):
        srid_prefix = ('SRID=%s;' % self._srid) if self._srid else ''
        if self._geodetic:
            if self._tmin is not None:
                if self._xmin is not None:
                    return "'%sGEODSTBOX T((%s, %s, %s, %s), (%s, %s, %s, %s))'" % \
                        (srid_prefix, self._xmin, self._ymin, self._zmin, self._tmin, self._xmax, self._ymax, self._zmax, self._tmax)
                else:
                    return "'%sGEODSTBOX T((, %s), (, %s))'" % (srid_prefix, self._tmin, self._tmax)
            else:
                return "'%sGEODSTBOX((%s, %s, %s), (%s, %s, %s))'" % \
                    (srid_prefix, self._xmin, self._ymin, self._zmin, self._xmax, self._ymax, self._zmax)
        else:
            if self._xmin is not None and self._zmin is not None and self._tmin is not None:
                return "'%sSTBOX ZT((%s, %s, %s, %s), (%s, %s, %s, %s))'" % \
                    (srid_prefix, self._xmin, self._ymin, self._zmin, self._tmin, self._xmax, self._ymax, self._zmax, self._tmax)
            elif self._xmin is not None and self._zmin is not None and self._tmin is None:
                return "'%sSTBOX Z((%s, %s, %s), (%s, %s, %s))'" % \
                    (srid_prefix, self._xmin, self._ymin, self._zmin, self._xmax, self._ymax, self._zmax)
            elif self._xmin is not None and self._zmin is None and self._tmin is not None:
                return "'%sSTBOX T((%s, %s, %s), (%s, %s, %s))'" % \
                    (srid_prefix, self._xmin, self._ymin, self._tmin, self._xmax, self._ymax, self._tmax)
            elif self._xmin is not None and self._zmin is None and self._tmin is None:
                return "'%sSTBOX ((%s, %s), (%s, %s))'" % \
                       (srid_prefix, self._xmin, self._ymin, self._xmax, self._ymax)
            elif self._xmin is None and self._zmin is None and self._tmin is not None:
                return "'%sSTBOX T((, %s), (, %s))'" % (srid_prefix, self._tmin, self._tmax)
            else:
                raise Exception("ERROR: Wrong values")

    def __repr__(self):
        return (f'{self.__class__.__name__ }'
                f'({self._xmin!r}, {self._ymin!r}, {self._zmin!r}, {self._tmin!r}, '
                f'{self._xmax!r}, {self._ymax!r}, {self._zmax!r}, {self._tmax!r}, {self._geodetic!r}, {self._srid!r})')
