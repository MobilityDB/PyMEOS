from typing import Optional

from pymeos_cffi import meos_initialize, meos_finish


def pymeos_initialize(timezone: Optional[str] = None):
    meos_initialize(timezone)


def pymeos_finalize() -> None:
    meos_finish()
