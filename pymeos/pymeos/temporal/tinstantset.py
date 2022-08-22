###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################
from __future__ import annotations

from abc import ABC
from typing import Optional, List, Union, Any, TYPE_CHECKING

from pymeos_cffi.functions import tinstantset_make
from ..temporal import TemporalInstants

if TYPE_CHECKING:
    pass


class TInstantSet(TemporalInstants, ABC):
    """
    Abstract class for representing temporal values of instant set subtype.
    """

    def __init__(self, *, string: Optional[str] = None, instant_list: Optional[List[Union[str, Any]]] = None,
                 merge: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (instant_list is not None)), \
            "Either string must be not None or instant_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = self.__class__._parse_function(string)
        else:
            instants = [x._inner if isinstance(x, self.ComponentClass) else self.__class__._parse_function(x) for x in
                        instant_list]
            self._inner = tinstantset_make(instants, len(instants), merge)

    @classmethod
    def temp_subtype(cls):
        """
        Subtype of the temporal value, that is, ``'InstantSet'``.
        """
        return "InstantSet"
