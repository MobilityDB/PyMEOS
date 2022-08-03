import warnings
from datetime import datetime

from dateutil.parser import parse

from src.functions import datetime_to_timestamptz, period_in, pg_timestamptz_in, period_make, pg_timestamptz_out, \
    overlaps_span_span, span_ge, contains_period_timestamp, span_eq, span_cmp, span_lt, span_le, span_gt, span_out

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class Period:
    """
    Class for representing sets of contiguous timestamps between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``Period`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> Period('(2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01)')

    Another possibility is to give a tuple of arguments as follows:

    * ``lower`` and ``upper`` are instances of ``str`` or ``datetime``
      specifying the bounds,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not. By default, ``lower_inc``
      is ``True`` and ``upper_inc`` is ``False``.

    Some examples are given next.

        >>> Period('2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01')
        >>> Period('2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', False, True)
        >>> Period(parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'))
        >>> Period(parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), False, True)

    """

    __slots__ = ['_inner', '_lower', '_upper']

    def __init__(self, lower, upper=None, lower_inc=None, upper_inc=None):
        assert (isinstance(lower_inc, (bool, type(None)))), "ERROR: Invalid lower bound flag"
        assert (isinstance(upper_inc, (bool, type(None)))), "ERROR: Invalid upper bound flag"
        # Constructor with a single argument of type string
        if upper is None and isinstance(lower, str):
            self._inner = period_in(lower.strip())
        elif isinstance(lower, str) and isinstance(upper, str):
            _lower = pg_timestamptz_in(lower, -1)
            _upper = pg_timestamptz_in(upper, -1)
            _lower_inc = lower_inc or True
            _upper_inc = upper_inc or False
            self._inner = period_make(_lower, _upper, _lower_inc, _upper_inc)
        # Constructor with two arguments of type datetime and optional arguments for the bounds
        elif isinstance(lower, datetime) and isinstance(upper, datetime):
            _lower = datetime_to_timestamptz(lower)
            _upper = datetime_to_timestamptz(upper)
            _lower_inc = lower_inc or True
            _upper_inc = upper_inc or False
            self._inner = period_make(_lower, _upper, _lower_inc, _upper_inc)
        else:
            raise Exception("ERROR: Could not parse period value")

        self._lower = parse(pg_timestamptz_out(self._inner.lower))
        self._upper = parse(pg_timestamptz_out(self._inner.upper))

    @property
    def lower(self) -> datetime:
        """
        Lower bound
        """
        return self._lower

    @property
    def upper(self) -> datetime:
        """
        Upper bound
        """
        return self._upper

    @property
    def lower_inc(self):
        """
        Is the lower bound inclusive?
        """
        return self._inner.lower_inc

    @property
    def upper_inc(self):
        """
        Is the upper bound inclusive?
        """
        return self._inner.upper_inc

    @property
    def duration(self):
        """
        Time interval on which the period is defined
        """
        return self.upper - self.lower

    def shift(self, timedelta):
        """
        Shift the period by a time interval
        """
        return Period(self._lower + timedelta, self._upper + timedelta, self.lower_inc, self.upper_inc)

    def overlap(self, other):
        """
        Do the periods share a timestamp?
        """
        return overlaps_span_span(self._inner, other._inner)

    def contains_timestamp(self, date_time: datetime):
        """
        Does the period contain the timestamp?
        """
        ts = datetime_to_timestamptz(date_time)
        return contains_period_timestamp(self._inner, ts)

    def __eq__(self, other):
        return span_eq(self._inner, other._inner)

    def _cmp(self, other):
        return span_cmp(self._inner, other._inner)

    def __lt__(self, other):
        return span_lt(self._inner, other._inner)

    def __le__(self, other):
        return span_le(self._inner, other._inner)

    def __gt__(self, other):
        return span_gt(self._inner, other._inner)

    def __ge__(self, other):
        return span_ge(self._inner, other._inner)

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    def getquoted(self):
        return "{}".format(self.__str__())

    # End Psycopg2 interface.

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return Period(value)

    @staticmethod
    def write(value):
        if not isinstance(value, Period):
            raise ValueError('Value must be an instance of Period class')
        return value.__str__().strip("'")

    def __str__(self):
        return span_out(self._inner, 0)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self._lower!r}, {self._upper!r}, {self.lower_inc!r}, {self.upper_inc!r})')
