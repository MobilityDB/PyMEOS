from typing import Optional

from pymeos_cffi import meos_initialize, meos_finalize, meos_set_debug


def pymeos_initialize(timezone: Optional[str] = None, debug: bool = False) -> None:
    """
    Initializes the underlying MEOS platform.
    Must be called before any other PyMEOS function.

    Args:
        timezone: :class:`str` indicating the desired timezone to be used. Defaults to system timezone.
        debug: :class:`bool` indicating whether debug mode should be enabled. Defaults to False.

    MEOS Functions:
        meos_initialize
    """
    meos_initialize(timezone)
    meos_set_debug(debug)


def pymeos_set_debug(debug: bool) -> None:
    """
    Sets the debug mode of the underlying MEOS platform.

    Args:
        debug: :class:`bool` indicating whether debug mode should be enabled.
    """
    meos_set_debug(debug)


def pymeos_finalize() -> None:
    """
    Cleans up the underlying MEOS platform.
    Should be called at the end after PyMEOS is no longer used.

    MEOS Functions:
        meos_finalize
    """
    meos_finalize()
