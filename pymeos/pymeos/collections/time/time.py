from datetime import datetime, date
from typing import Union

from .tstzspan import TsTzSpan
from .tstzspanset import TsTzSpanSet
from .tstzset import TsTzSet

Time = Union[
    datetime,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
    date,
]
"""
Union type that includes all Time types in PyMEOS:  

- :class:`~datetime.datetime` for timestamps  
- :class:`~pymeos.time.tstzset.TsTzSet` for sets of timestamps  
- :class:`~pymeos.time.tstzspan.TsTzSpan` for tstzspans of time  
- :class:`~pymeos.time.tstzspanset.TsTzSpanSet` for sets of tstzspans of time  
"""
