from __future__ import annotations

from abc import ABC
from typing import Optional, Union, List, Any, TypeVar, Type

from pymeos_cffi import *

from .interpolation import TInterpolation
from .temporal import Temporal

TBase = TypeVar("TBase")
TG = TypeVar("TG", bound="Temporal[Any]")
TI = TypeVar("TI", bound="TInstant[Any]")
TS = TypeVar("TS", bound="TSequence[Any]")
TSS = TypeVar("TSS", bound="TSequenceSet[Any]")
Self = TypeVar("Self", bound="TSequence[Any]")


class TSequence(Temporal[TBase, TG, TI, TS, TSS], ABC):
    """
    Base class for temporal sequence types, i.e. temporal values that are
    defined over a continuous tstzspan of time.
    """

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, Any]]] = None,
        lower_inc: bool = True,
        upper_inc: bool = False,
        interpolation: TInterpolation = TInterpolation.LINEAR,
        normalize: bool = True,
        _inner=None,
    ):
        assert (_inner is not None) or (
            (string is not None) != (instant_list is not None)
        ), "Either string must be not None or instant_list must be not"
        if _inner is not None:
            self._inner = as_tsequence(_inner)
        elif string is not None:
            self._inner = as_tsequence(self.__class__._parse_function(string))
        else:
            self._instants = [
                (
                    x._inner
                    if isinstance(x, self.ComponentClass)
                    else self.__class__._parse_function(x)
                )
                for x in instant_list
            ]
            count = len(self._instants)
            self._inner = tsequence_make(
                self._instants,
                count,
                lower_inc,
                upper_inc,
                interpolation.value,
                normalize,
            )

    @classmethod
    def from_instants(
        cls: Type[Self],
        instant_list: Optional[List[Union[str, Any]]],
        lower_inc: bool = True,
        upper_inc: bool = False,
        interpolation: TInterpolation = TInterpolation.LINEAR,
        normalize: bool = True,
    ) -> Self:
        """
        Create a temporal sequence from a list of instants.

        Args:
            instant_list: List of instants
            lower_inc: Whether the lower bound is inclusive
            upper_inc: Whether the upper bound is inclusive
            interpolation: Interpolation method
            normalize: Whether to normalize the sequence

        Returns:
            A new temporal sequence.
        """
        return cls(
            instant_list=instant_list,
            lower_inc=lower_inc,
            upper_inc=upper_inc,
            interpolation=interpolation,
            normalize=normalize,
        )

    # ------------------------- Accessors -------------------------------------
    def lower_inc(self) -> bool:
        """
        Returns whether the lower bound is inclusive.

        Returns:
            `True` if the lower bound is inclusive, `False` otherwise.
        """
        return self._inner.period.lower_inc

    def upper_inc(self) -> bool:
        """
        Returns whether the upper bound is inclusive.

        Returns:
            `True` if the upper bound is inclusive, `False` otherwise.
        """
        return self._inner.period.upper_inc

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        """
        Plot the temporal sequence.

        See Also:
            :meth:`pymeos.plotters.TemporalSequencePlotter.plot`
        """
        from ..plotters import TemporalSequencePlotter

        return TemporalSequencePlotter.plot(self, *args, **kwargs)
