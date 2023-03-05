from typing import Union

from .stbox import STBox
from .tbox import TBox

Box = Union[TBox, STBox]
"""
Union type that includes all Box types in PyMEOS:  

- :class:`~pymeos.boxes.tbox.TBox` for numeric temporal boxes.  
- :class:`~pymeos.boxes.stbox.STBox` for spatio-temporal boxes.
"""
