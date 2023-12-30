from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, List

from dateutil.parser import parse
from pymeos_cffi import (
    dateset_in,
    pg_date_in,
    date_to_date_adt,
    dateset_make,
    dateset_out,
)

from .timecollection import TimeCollection
from ..base import Set
from ..base.set import T
from ... import Span, SpanSet

if TYPE_CHECKING:
    pass


class DateSpan(Span[date], TimeCollection[date]):
    pass
