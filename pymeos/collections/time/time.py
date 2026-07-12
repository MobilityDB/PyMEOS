from datetime import date, datetime

from .dateset import DateSet
from .datespan import DateSpan
from .datespanset import DateSpanSet
from .tstzset import TsTzSet
from .tstzspan import TsTzSpan
from .tstzspanset import TsTzSpanSet

Time = datetime | TsTzSet | TsTzSpan | TsTzSpanSet
"""
Union type that includes all Time types related to timestamps in PyMEOS:

- :class:`~datetime.datetime` for timestamps
- :class:`~pymeos.time.tstzset.TsTzSet` for sets of timestamps
- :class:`~pymeos.time.tstzspan.TsTzSpan` for spans of time
- :class:`~pymeos.time.tstzspanset.TsTzSpanSet` for sets of spans of time
"""

TimeDate = date | DateSet | DateSpan | DateSpanSet

"""
Union type that includes all Time types related to dates in PyMEOS:

- :class:`~datetime.date` for dates
- :class:`~pymeos.time.dateset.DateSet` for sets of dates
- :class:`~pymeos.time.datespan.DateSpan` for spans of dates
- :class:`~pymeos.time.datespanset.DateSpanSet` for sets of spans of dates
"""
