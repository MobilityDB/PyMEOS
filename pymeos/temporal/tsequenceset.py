from __future__ import annotations

from abc import ABC
from typing import Optional, List, Union, Any, TypeVar, Type, TYPE_CHECKING

from pymeos_cffi import *

from .temporal import Temporal, import_pandas

if TYPE_CHECKING:
    import pandas as pd


TBase = TypeVar("TBase")
TG = TypeVar("TG", bound="Temporal[Any]")
TI = TypeVar("TI", bound="TInstant[Any]")
TS = TypeVar("TS", bound="TSequence[Any]")
TSS = TypeVar("TSS", bound="TSequenceSet[Any]")
Self = TypeVar("Self", bound="TSequenceSet[Any]")


class TSequenceSet(Temporal[TBase, TG, TI, TS, TSS], ABC):
    """
    Base class for temporal sequence set types, i.e. temporal values that are
    defined by a set of temporal sequences.
    """

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, Any]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        assert (_inner is not None) or (
            (string is not None) != (sequence_list is not None)
        ), "Either string must be not None or sequence_list must be not"
        if _inner is not None:
            self._inner = as_tsequenceset(_inner)
        elif string is not None:
            self._inner = as_tsequenceset(self.__class__._parse_function(string))
        else:
            sequences = [
                (
                    x._inner
                    if isinstance(x, self.ComponentClass)
                    else self.__class__._parse_function(x)
                )
                for x in sequence_list
            ]
            count = len(sequences)
            self._inner = tsequenceset_make(sequences, count, normalize)

    @classmethod
    def from_sequences(
        cls: Type[Self],
        sequence_list: Optional[List[Union[str, Any]]] = None,
        normalize: bool = True,
    ) -> Self:
        """
        Create a temporal sequence set from a list of sequences.

        Args:
            sequence_list: List of sequences.
            normalize: Whether to normalize the temporal sequence set.

        Returns:
            A temporal sequence set.
        """
        return cls(sequence_list=sequence_list, normalize=normalize)

    # ------------------------- Accessors -------------------------------------
    def num_sequences(self) -> int:
        """
        Returns the number of sequences in ``self``.
        """
        return temporal_num_sequences(self._inner)

    def start_sequence(self) -> TS:
        """
        Returns the first sequence in ``self``.
        """
        return self.ComponentClass(_inner=temporal_start_sequence(self._inner))

    def end_sequence(self) -> TS:
        """
        Returns the last sequence in ``self``.
        """
        return self.ComponentClass(_inner=temporal_end_sequence(self._inner))

    def sequence_n(self, n) -> TS:
        """
        Returns the ``n``-th sequence in ``self``.
        """
        return self.ComponentClass(_inner=temporal_sequence_n(self._inner, n + 1))

    def sequences(self) -> List[TS]:
        """
        Returns the list of sequences in ``self``.
        """
        ss, count = temporal_sequences(self._inner)
        return [self.ComponentClass(_inner=ss[i]) for i in range(count)]

    # ------------------------- Transformations -------------------------------
    def to_dataframe(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame representation of ``self``.
        """
        pd = import_pandas()
        sequences = self.sequences()
        data = {
            "sequence": [
                i for i, seq in enumerate(sequences) for _ in range(seq.num_instants())
            ],
            "time": [t for seq in sequences for t in seq.timestamps()],
            "value": [v for seq in sequences for v in seq.values()],
        }
        return pd.DataFrame(data).set_index(keys=["sequence", "time"])

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        """
        Plot the temporal sequence set.

        See Also:
            :meth:`pymeos.plotters.TemporalSequenceSetPlotter.plot`
        """
        from ..plotters import TemporalSequenceSetPlotter

        return TemporalSequenceSetPlotter.plot(self, *args, **kwargs)
