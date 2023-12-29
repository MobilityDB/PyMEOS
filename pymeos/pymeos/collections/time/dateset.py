from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, List, Union, TYPE_CHECKING, overload, get_args

from dateutil.parser import parse
from pymeos_cffi import *

from .timecollection import TimeCollection
from ..base import Set

if TYPE_CHECKING:
    from ...temporal import Temporal
    from .tstzspan import TsTzSpan
    from .tstzspanset import TsTzSpanSet
    from .time import Time
    from ...boxes import Box


class DateSet(Set[date], TimeCollection[date]):
    """
    Class for representing lists of distinct dates.

    ``DateSet`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> DateSet(string='{2019-09-08, 2019-09-10, 2019-09-11}')

    Another possibility is to give a tuple or list of composing dates,
    which can be instances of ``str`` or ``date``. The composing dates
    must be given in increasing order.

        >>> DateSet(elements=['2019-09-08', '2019-09-10', '2019-09-11'])
        >>> DateSet(elements=[parse('2019-09-08'), parse('2019-09-10'), parse('2019-09-11')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "dateset"

    _parse_function = dateset_in
    _parse_value_function = (
        lambda x: pg_date_in(x)
        if isinstance(x, str)
        else date_to_date_adt(x)
    )
    _make_function = dateset_make
