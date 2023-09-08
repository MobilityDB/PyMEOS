from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Generic, TypeVar, Type, Callable, Any
from typing import Optional, Union, overload, get_args

from pymeos_cffi import *

T = TypeVar('T')
Self = TypeVar('Self', bound='Span[Any]')


class Set(Generic[T], ABC):
    """
    Base class for all set classes.
    """

    __slots__ = ['_inner']
