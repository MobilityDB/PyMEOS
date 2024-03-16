from typing import Optional, Union, Tuple, Any

from pymeos_cffi import (
    meos_initialize,
    meos_finalize,
    meos_set_datestyle,
    meos_set_intervalstyle,
)


def pymeos_initialize(
    timezone: Optional[str] = None,
    date_style: Union[None, str, Tuple[str, Any]] = None,
    interval_style: Union[None, str, Tuple[str, int]] = None,
) -> None:
    """
    Initializes the underlying MEOS platform.
    Must be called before any other PyMEOS function.

    Args:
        timezone: :class:`str` indicating the desired timezone to be used. Defaults to system timezone.
        date_style: :class:`str` indicating the desired date style to be used.
        interval_style: :class:`str` indicating the desired interval style to be used.

    MEOS Functions:
        meos_initialize, meos_set_datestyle, meos_set_intervalstyle
    """
    meos_initialize(timezone)

    if date_style is not None:
        if isinstance(date_style, str):
            meos_set_datestyle(date_style, None)
        else:
            meos_set_datestyle(*date_style)

    if interval_style is not None:
        if isinstance(interval_style, str):
            meos_set_intervalstyle(interval_style, None)
        else:
            meos_set_intervalstyle(*interval_style)


def pymeos_finalize() -> None:
    """
    Cleans up the underlying MEOS platform.
    Should be called at the end after PyMEOS is no longer used.

    MEOS Functions:
        meos_finalize
    """
    meos_finalize()
