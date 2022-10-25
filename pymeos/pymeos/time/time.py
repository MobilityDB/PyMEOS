from typing import Union

from .period import Period
from .periodset import PeriodSet
from .timestampset import TimestampSet
from datetime import datetime

Time = Union[datetime, TimestampSet, Period, PeriodSet]