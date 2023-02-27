from typing import Optional

from pymeos_cffi import meos_initialize, meos_finalize


def pymeos_initialize(timezone: Optional[str] = None) -> None:
    """
    Initializes the underlying MEOS platform.
    Must be called before any other PyMEOS function.

    Args:
        timezone: :class:`str` indicating the desired timezone to be used. Defaults to system timezone.

    MEOS Functions:
        meos_initialize
    """
    meos_initialize(timezone)


def pymeos_finalize() -> None:
    """
    Cleans up the underlying MEOS platform.
    Should be called at the end after PyMEOS is no longer used.

    MEOS Functions:
        meos_finish
    """
    meos_finalize()
