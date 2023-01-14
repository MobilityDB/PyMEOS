from typing import Union

from .period import Period
from .periodset import PeriodSet
from .timestampset import TimestampSet
from datetime import datetime

Time = Union[datetime, TimestampSet, Period, PeriodSet]
"""
Union type that includes all Time types in PyMEOS:  

- :class:`datetime` for timestamps  
- :class:`TimestampSet` for sets of timestamps  
- :class:`Period` for periods of time  
- :class:`PeriodSet` for sets of periods of time  
"""