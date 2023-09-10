from typing import Union

from .period import Period
from .periodset import PeriodSet
from .timestampset import TimestampSet
from datetime import datetime

Time = Union[datetime, TimestampSet, Period, PeriodSet]
"""
Union type that includes all Time types in PyMEOS:  

- :class:`~datetime.datetime` for timestamps  
- :class:`~pymeos.time.timestampset.TimestampSet` for sets of timestamps  
- :class:`~pymeos.time.period.Period` for periods of time  
- :class:`~pymeos.time.periodset.PeriodSet` for sets of periods of time  
"""