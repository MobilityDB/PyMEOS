from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Union, TYPE_CHECKING, Set, Generic, TypeVar, Type

from pandas import DataFrame
from pymeos_cffi import *

from .interpolation import TInterpolation
from ..time import *

if TYPE_CHECKING:
    from .tinstant import TInstant
    from ..main import TBool
    from ..boxes import Box
TBase = TypeVar('TBase')
TG = TypeVar('TG', bound='Temporal[Any]')
TI = TypeVar('TI', bound='TInstant[Any]')
TS = TypeVar('TS', bound='TSequence[Any]')
TSS = TypeVar('TSS', bound='TSequenceSet[Any]')
Self = TypeVar('Self', bound='Temporal[Any]')


class Temporal(Generic[TBase, TG, TI, TS, TSS], ABC):
    """
    Abstract class for representing temporal values of any subtype.
    """
    __slots__ = ['_inner']

    BaseClass = None
    """
    Class of the base type, for example, ``float`` for ``TFloat``
    """

    ComponentClass = None
    """
    Class of the components, for example, 

    1. ``TFloatInst`` for both ``TFloatInst`` and ``TFloatSeq``
    2. ``TFloatSeq`` for ``TFloatSeqSet``.
    """

    _parse_function = None

    def _expandable(self) -> bool:
        return False

    @classmethod
    def _factory(cls, inner):
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(inner)

    # ------------------------- Input/Output ----------------------------------
    @staticmethod
    @abstractmethod
    def from_base_time(value: TBase, base: Time) -> TG:
        """
        Create a temporal object from a boolean value and a time object.

        Args:
            value: Base value.
            base: Time object to use as temporal dimension.

        Returns:
            A new temporal object.

        """
        pass

    @classmethod
    def from_wkb(cls: Type[Self], wkb: bytes) -> Self:
        """
        Returns a temporal object from WKB bytes.

        Args:
            wkb: The WKB string.

        Returns:
            A temporal object from WKB bytes.

        MEOS Functions:
            temporal_from_wkb
        """
        result = temporal_from_wkb(wkb)
        return Temporal._factory(result)

    @classmethod
    def from_hexwkb(cls: Type[Self], hexwkb: str) -> Self:
        """
        Returns a temporal object from a hex-encoded WKB string.

        Args:
            hexwkb: The hex-encoded WKB string.

        Returns:
            A temporal object from a hex-encoded WKB string.

        MEOS Functions:
            temporal_from_hexwkb
        """
        result = temporal_from_hexwkb(hexwkb)
        return Temporal._factory(result)

    @classmethod
    def from_mfjson(cls: Type[Self], mfjson: str) -> Self:
        """
        Returns a temporal object from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal object from a MF-JSON string.

        MEOS Functions:
            temporal_from_mfjson
        """
        result = temporal_from_mfjson(mfjson)
        return Temporal._factory(result)

    @classmethod
    def from_merge(cls: Type[Self], *temporals: TG) -> Self:
        """
        Returns a temporal object that is the result of merging the given temporal objects.

        Args:
            *temporals: The temporal objects to merge.

        Returns:
            A temporal object that is the result of merging the given temporal objects.

        MEOS Functions:
            temporal_merge_array
        """
        result = temporal_merge_array([temp._inner for temp in temporals if temp is not None], len(temporals))
        return Temporal._factory(result)

    @classmethod
    def from_merge_array(cls: Type[Self], temporals: List[TG]) -> Self:
        """
        Returns a temporal object that is the result of merging the given temporal objects.

        Args:
            temporals: The temporal objects to merge.

        Returns:
            A temporal object that is the result of merging the given temporal objects.
        """
        result = temporal_merge_array([temp._inner for temp in temporals if temp is not None], len(temporals))
        return Temporal._factory(result)

    @abstractmethod
    def as_wkt(self) -> str:
        """
        Returns the temporal object as a WKT string.

        Returns:
            The temporal object as a WKT string.
        """
        pass

    def as_mfjson(self, with_bbox: bool = True, flags: int = 3, precision: int = 6, srs: Optional[str] = None) -> str:
        """
        Returns the temporal object as a MF-JSON string.

        Args:
            with_bbox: Whether to include the bounding box in the output.
            flags: The flags to use for the output.
            precision: The precision to use for the output.
            srs: The SRS to use for the output.

        Returns:
            The temporal object as a MF-JSON string.

        MEOS Functions:
            temporal_as_mfjson
        """
        return temporal_as_mfjson(self._inner, with_bbox, flags, precision, srs)

    def as_wkb(self) -> bytes:
        """
        Returns the temporal object as a hex-encoded WKB string.

        Returns:
            The temporal object as a hex-encoded WKB string.

        MEOS Functions:
            temporal_as_hexwkb
        """
        return temporal_as_wkb(self._inner, 4)

    def as_hexwkb(self) -> str:
        """
        Returns the temporal object as a hex-encoded WKB string.

        Returns:
            The temporal object as a hex-encoded WKB string.

        MEOS Functions:
            temporal_as_hexwkb
        """
        return temporal_as_hexwkb(self._inner, 4)[0]

    # ------------------------- Accessors -------------------------------------
    def interpolation(self) -> TInterpolation:
        """
        Returns the interpolation of `self`

        MEOS Functions:
            temporal_interpolation
        """
        val = temporal_interp(self._inner)
        return TInterpolation.from_string(val)

    @abstractmethod
    def value_set(self) -> Set[TBase]:
        """
        Returns the unique values in `self`.
        """
        pass

    def values(self) -> List[TBase]:
        """
        Returns the list of values taken by `self`.
        """
        return [i.value() for i in self.instants()]

    @abstractmethod
    def start_value(self) -> TBase:
        """
        Returns the starting value of `self`.
        """
        pass

    @abstractmethod
    def end_value(self) -> TBase:
        """
        Returns the end value of `self`.
        """
        pass

    def min_value(self) -> TBase:
        """
        Returns the minimum value that `self` takes.
        """
        return min(self.value_set())

    def max_value(self) -> TBase:
        """
        Returns the maximum value that `self` takes.
        """
        return max(self.value_set())

    @abstractmethod
    def value_at_timestamp(self, timestamp: datetime) -> TBase:
        """
        Returns the value that `self` takes at a certain moment.
        """
        pass

    def time(self) -> PeriodSet:
        """
        Returns the :class:`PeriodSet` on which `self` is defined.

        MEOS Functions:
            temporal_time
        """
        return PeriodSet(_inner=temporal_time(self._inner))

    def duration(self, ignore_gaps=False) -> timedelta:
        """
        Returns the duration of `self`. By default, the gaps in `self` are taken into account, but this can be
        changed by setting `ignore_gaps` to ``True``. This will only potentially alter the result for sequence sets and
        discrete sequences.

        Parameters:
            ignore_gaps: Whether to take into account potential time gaps in the temporal value.

        MEOS Functions:
            temporal_duration
        """
        return interval_to_timedelta(temporal_duration(self._inner, ignore_gaps))

    def period(self) -> Period:
        """
        Returns the :class:`Period` on which `self` is defined ignoring potential time gaps.

        MEOS Functions:
            temporal_to_period
        """
        return self.timespan()

    def timespan(self) -> Period:
        """
        Returns the :class:`Period` on which `self` is defined ignoring potential time gaps.

        MEOS Functions:
            temporal_to_period
        """
        return Period(_inner=temporal_to_period(self._inner))

    def num_instants(self) -> int:
        """
        Returns the number of instants in `self`.

        MEOS Functions:
            temporal_num_instants
        """
        return temporal_num_instants(self._inner)

    def start_instant(self) -> TI:
        """
        Returns the first instant in `self`.

        MEOS Functions:
            temporal_start_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_start_instant(self._inner))

    def end_instant(self) -> TI:
        """
        Returns the last instant in `self`.

        MEOS Functions:
            temporal_end_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_end_instant(self._inner))

    def max_instant(self) -> TI:
        """
        Returns the instant in `self` with the maximum value.
        If multiple instants have the maximum value, the first one is returned.

        MEOS Functions:
            temporal_max_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_max_instant(self._inner))

    def min_instant(self) -> TI:
        """
        Returns the instant in `self` with the minimum value.
        If multiple instants have the minimum value, the first one is returned.

        MEOS Functions:
            temporal_min_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_min_instant(self._inner))

    def instant_n(self, n: int) -> TI:
        """
        Returns the n-th instant in `self`. (0-based)

        MEOS Functions:
            temporal_instant_n
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_instant_n(self._inner, n + 1))

    def instants(self) -> List[TI]:
        """
        Returns the instants in `self`.

        MEOS Functions:
            temporal_instants
        """
        from ..factory import _TemporalFactory
        ins, count = temporal_instants(self._inner)
        return [_TemporalFactory.create_temporal(ins[i]) for i in range(count)]

    def num_timestamps(self) -> int:
        """
        Returns the number of timestamps in `self`.

        MEOS Functions:
            temporal_num_timestamps
        """
        return temporal_num_timestamps(self._inner)

    def start_timestamp(self) -> datetime:
        """
        Returns the first timestamp in `self`.

        MEOS Functions:
            temporal_start_timestamps
        """
        return timestamptz_to_datetime(temporal_start_timestamp(self._inner))

    def end_timestamp(self) -> datetime:
        """
        Returns the last timestamp in `self`.

        MEOS Functions:
            temporal_end_timestamps
        """
        return timestamptz_to_datetime(temporal_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in `self`. (0-based)

        MEOS Functions:
            temporal_timestamp_n
        """
        return timestamptz_to_datetime(temporal_timestamp_n(self._inner, n + 1))

    def timestamps(self) -> List[datetime]:
        """
        Returns the timestamps in `self`.

        MEOS Functions:
            temporal_timestamps
        """
        ts, count = temporal_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    def segments(self) -> List[TS]:
        """
        Returns the temporal segments in `self`.

        MEOS Functions:
            temporal_segments
        """
        seqs, count = temporal_segments(self._inner)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(seqs[i]) for i in range(count)]

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: timedelta) -> Period:
        """
        Returns a new :class:`Temporal` with the temporal dimension shifted by ``delta``.

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        MEOS Functions:
            temporal_shift
        """
        shifted = temporal_shift(self._inner, timedelta_to_interval(delta))
        return Temporal._factory(shifted)

    def tscale(self, duration: timedelta) -> Period:
        """
        Returns a new :class:`Temporal` scaled so the temporal dimension has duration ``duration``.

        Args:
            duration: :class:`datetime.timedelta` instance representing the duration of the new temporal

        MEOS Functions:
            temporal_tscale
        """
        scaled = temporal_tscale(self._inner, timedelta_to_interval(duration))
        return Temporal._factory(scaled)

    def shift_tscale(self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None) -> Self:
        """
        Returns a new :class:`Temporal` with the time dimension shifted by ``shift`` and scaled so the temporal
        dimension has duration ``duration``.

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the duration of the new temporal

        MEOS Functions:
            temporal_shift_tscale
        """
        assert shift is not None or duration is not None, 'shift and duration must not be both None'
        scaled = temporal_shift_tscale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None
        )
        return Temporal._factory(scaled)

    def to_instant(self) -> TI:
        """
        Returns `self` as a :class:`TInstant`.

        MEOS Functions:
            temporal_to_tinstant
        """
        inst = temporal_to_tinstant(self._inner)
        return Temporal._factory(inst)

    def to_sequence(self) -> TS:
        """
        Converts `self` into a :class:`TSequence`.

        MEOS Functions:
            temporal_to_sequence
        """
        seq = temporal_to_tsequence(self._inner)
        return Temporal._factory(seq)

    def to_sequenceset(self) -> TSS:
        """
        Returns `self` as a :class:`TSequenceSet`.

        MEOS Functions:
            temporal_to_tsequenceset
        """
        ss = temporal_to_tsequenceset(self._inner)
        return Temporal._factory(ss)

    def to_dataframe(self) -> DataFrame:
        """
        Returns `self` as a :class:`pd.DataFrame` with two columns: `time` and `value`.
        """
        data = {
            'time': self.timestamps(),
            'value': self.values()
        }
        return DataFrame(data).set_index(keys='time')

    # ------------------------- Modifications ---------------------------------
    def append(self, instant: TInstant[TBase], max_dist: float, max_time: timedelta) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` with `instant` appended.

        Args:
            instant: :class:`TInstant` to append
            max_dist: Maximum distance for defining a gap
            max_time: Maximum time for defining a gap

        MEOS Functions:
            temporal_append_tinstant
        """
        new_inner = temporal_append_tinstant(self._inner, instant._inner, max_dist, timedelta_to_interval(max_time),
                                             self._expandable())
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    def merge(self, other: Union[type(None), Temporal[TBase], List[Temporal[TBase]]]) -> TG:
        """
        Returns a new :class:`Temporal` object that is the result of merging `self` with `other`.

        MEOS Functions:
            temporal_merge, temporal_merge_array
        """
        if isinstance(self, type(None)):
            return other
        if isinstance(other, type(None)):
            return self
        if isinstance(other, Temporal):
            new_temp = temporal_merge(self._inner, other._inner)
        elif isinstance(other, list):
            new_temp = temporal_merge_array([self._inner, *(o._inner for o in other)], len(other) + 1)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(new_temp)

    def insert(self, other: TG, connect: bool = False) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` with `other` inserted.

        Args:
            other: :class:`Temporal` object to insert in `self`
            connect: wether to connect the inserted elements with the existing elements.

        MEOS Functions:
            temporal_insert
        """
        new_inner = temporal_insert(self._inner, other._inner, connect)
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    def update(self, other: TG, connect: bool = False) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` updated with `other`.

        Args:
            other: :class:`Temporal` object to update `self` with
            connect: wether to connect the updated elements with the existing elements.

        MEOS Functions:
            temporal_update
        """
        new_inner = temporal_update(self._inner, other._inner, connect)
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    def delete(self, other: Time, connect: bool = False) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` with elements at `other` removed.

        Args:
            other: :class:`Time` object to remove from `self`
            connect: wether to connect the potential gaps generated by the deletions.

        MEOS Functions:
            temporal_update
        """
        if isinstance(other, datetime):
            new_inner = temporal_delete_timestamp(self._inner, datetime_to_timestamptz(other), connect)
        elif isinstance(other, TimestampSet):
            new_inner = temporal_delete_timestampset(self._inner, other._inner, connect)
        elif isinstance(other, Period):
            new_inner = temporal_delete_period(self._inner, other._inner, connect)
        elif isinstance(other, PeriodSet):
            new_inner = temporal_delete_periodset(self._inner, other._inner, connect)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    def set_interpolation(self: Self, interpolation: TInterpolation) -> Self:
        """
        Returns a new :class:`Temporal` object equal to `self` with the given interpolation.

        MEOS Functions:
            temporal_set_interpolation
        """
        new_temp = temporal_set_interp(self._inner, interpolation)
        return Temporal._factory(new_temp)

    # ------------------------- Restrictions ----------------------------------
    def at(self, other: Time) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to the time `other`.

        Args:
            other: A time object to restrict the values of `self` to.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_at_timestamp, temporal_at_timestampset, temporal_at_period, temporal_at_periodset
        """
        if isinstance(other, datetime):
            result = temporal_at_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            result = temporal_at_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            result = temporal_at_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            result = temporal_at_periodset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def at_max(self) -> TG:
        """
        Returns a new temporal object containing the times ``self`` is at its maximum value.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_at_max
        """
        result = temporal_at_max(self._inner)
        return Temporal._factory(result)

    def at_min(self) -> TG:
        """
        Returns a new temporal object containing the times ``self`` is at its minimum value.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_at_min
        """
        result = temporal_at_min(self._inner)
        return Temporal._factory(result)

    def minus(self, other: Time) -> TG:
        """
        Returns a new temporal object with the values of `self` removing those happening at `other`.

        Args:
            other: A time object to remove from `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_minus_timestamp, temporal_minus_timestampset, temporal_minus_period, temporal_minus_periodset
        """
        if isinstance(other, Period):
            result = temporal_minus_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            result = temporal_minus_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            result = temporal_minus_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            result = temporal_minus_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def minus_max(self) -> TG:
        """
        Returns a new temporal object containing the times ``self`` is not at its maximum value.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_minus_max
        """
        result = temporal_minus_max(self._inner)
        return Temporal._factory(result)

    def minus_min(self) -> TG:
        """
        Returns a new temporal object containing the times ``self`` is not at its minimum value.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_minus_min
        """
        result = temporal_minus_min(self._inner)
        return Temporal._factory(result)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is adjacent to the bounding box of `other`.
        Temporal subclasses may override this method to provide more specific behavior related to their types and
        check adjacency over more dimensions.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if adjacent, False otherwise.

        See Also:
            :meth:`Period.is_adjacent`
        """
        return self.period().is_adjacent(other)

    def is_temporally_adjacent(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` is temporally adjacent to the bounding period of `other`.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if adjacent, False otherwise.

        See Also:
            :meth:`Period.is_adjacent`
        """
        return self.period().is_adjacent(other)

    def is_contained_in(self, container: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` is contained in the bounding period of `container`.
        Temporal subclasses may override this method to provide more specific behavior related to their types

        Args:
            container: A time or temporal object to compare to `self`.

        Returns:
            True if contained, False otherwise.

        See Also:
            :meth:`Period.is_contained_in`
        """
        return self.period().is_contained_in(container)

    def is_temporally_contained_in(self, container: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` is contained in the bounding period of `container`.

        Args:
            container: A time or temporal object to compare to `self`.

        Returns:
            True if contained, False otherwise.

        See Also:
            :meth:`Period.is_contained_in`
        """
        return self.period().is_contained_in(container)

    def contains(self, content: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` contains the bounding period of `content`.
        Temporal subclasses may override this method to provide more specific behavior related to their types

        Args:
            content: A time or temporal object to compare to `self`.

        Returns:
            True if contains, False otherwise.

        See Also:
            :meth:`Period.contains`
        """
        return self.period().contains(content)

    def __contains__(self, item):
        """
        Returns whether the bounding period of `self` contains the bounding period of `content`.

        Args:
            item: A time or temporal object to compare to `self`.

        Returns:
            True if contains, False otherwise.

        See Also:
            :meth:`Period.contains`
        """
        return self.contains(item)

    def temporally_contains(self, content: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` contains the bounding period of `content`.

        Args:
            content: A time or temporal object to compare to `self`.

        Returns:
            True if contains, False otherwise.

        See Also:
            :meth:`Period.contains`
        """
        return self.period().contains(content)

    def overlaps(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` overlaps the bounding period of `other`.
        Temporal subclasses may override this method to provide more specific behavior related to their types

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if overlaps, False otherwise.

        See Also:
            :meth:`Period.overlaps`
        """
        return self.period().overlaps(other)

    def temporally_overlaps(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` overlaps the bounding period of `other`.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if overlaps, False otherwise.

        See Also:
            :meth:`Period.overlaps`
        """
        return self.period().overlaps(other)

    def is_same(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` is the same as the bounding period of `other`.
        Temporal subclasses may override this method to provide more specific behavior related to their types

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if same, False otherwise.

        See Also:
            :meth:`Period.is_same`
        """
        return self.period().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether `self` is after `other`.

        Args:
            other: A time or temporal object to compare `self` to.

        Returns:
            True if `self` is after `other`, False otherwise.

        See Also:
            :meth:`Period.is_after`
        """
        return self.period().is_after(other)

    def is_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether `self` is before `other`.

        Args:
            other: A time or temporal object to compare `self` to.

        Returns:
            True if `self` is before `other`, False otherwise.

        See Also:
            :meth:`Period.is_before`
        """
        return self.period().is_before(other)

    def is_over_or_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether `self` is after `other` allowing overlap. That is, `self` doesn't extend before `other`.

        Args:
            other: A time or temporal object to compare `self` to.

        Returns:
            True if `self` is after `other` allowing overlap, False otherwise.

        See Also:
            :meth:`Period.is_over_or_after`
        """
        return self.period().is_over_or_after(other)

    def is_over_or_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether `self` is before `other` allowing overlap. That is, `self` doesn't extend after `other`.

        Args:
            other: A time or temporal object to compare `self` to.

        Returns:
            True if `self` is before `other` allowing overlap, False otherwise.

        See Also:
            :meth:`Period.is_over_or_before`
        """
        return self.period().is_over_or_before(other)

    # ------------------------- Similarity Operations -------------------------
    def frechet_distance(self, other: Temporal) -> float:
        """
        Returns the Frechet distance between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`float` with the Frechet distance.

        MEOS Functions:
            temporal_frechet_distance
        """
        return temporal_frechet_distance(self._inner, other._inner)

    def dyntimewarp_distance(self, other: Temporal) -> float:
        """
        Returns the Dynamic Time Warp distance between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`float` with the Dynamic Time Warp distance.

        MEOS Functions:
            temporal_dyntimewarp_distance
        """
        return temporal_dyntimewarp_distance(self._inner, other._inner)

    def hausdorff_distance(self, other: Temporal) -> float:
        """
        Returns the Hausdorff distance between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`float` with the Hausdorff distance.

        MEOS Functions:
            temporal_hausdorff_distance
        """
        return temporal_hausdorff_distance(self._inner, other._inner)

    # ------------------------- Split Operations ------------------------------
    def time_split(self, duration: Union[str, timedelta], start: Optional[Union[str, datetime]] = None) -> List[TG]:
        """
        Returns a list of temporal objects of the same subtype as `self` with the same values as `self` but split in
        temporal tiles of duration `duration` starting at `start`.

        Args:
            duration: A :class:`str` or :class:`timedelta` with the duration of the temporal tiles.
            start: A :class:`str` or :class:`datetime` with the start time of the temporal tiles. If None, the start
                time of `self` is used.

        Returns:
            A list of temporal objects of the same subtype as `self`.

        MEOS Functions:
            temporal_time_split
        """
        if start is None:
            st = temporal_start_timestamp(self._inner)
        else:
            st = datetime_to_timestamptz(start) if isinstance(start, datetime) else pg_timestamptz_in(start, -1)
        dt = timedelta_to_interval(duration) if isinstance(duration, timedelta) else pg_interval_in(duration, -1)
        tiles, new_count = temporal_time_split(self._inner, dt, st)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(tiles[i]) for i in range(new_count)]

    def time_split_n(self, n: int) -> List[TG]:
        """
        Returns a list of temporal objects of the same subtype as `self` with the same values as `self` but split in
        n temporal tiles of equal duration.

        Args:
            n: An :class:`int` with the number of temporal tiles.

        Returns:
            A list of temporal objects of the same subtype as `self`.

        MEOS Functions:
            temporal_time_split
        """
        st = temporal_start_timestamp(self._inner)
        dt = timedelta_to_interval((self.end_timestamp() - self.start_timestamp()) / n)
        tiles, new_count = temporal_time_split(self._inner, dt, st)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(tiles[i]) for i in range(new_count)]

    def stops(self, max_distance: float, min_duration: timedelta) -> TSS:
        """
        Return the subsequences where the objects stay within an area with a given maximum size for at least
        the specified duration.

        Args:
            max_distance: A :class:`float` with the maximum distance of a stop.
            min_duration: A :class:`timedelta` with the minimum duration of a stop.

        Returns:
            A :class:`SequenceSet` of the same subtype as `self` with the stops.

        MEOS Functions:
            temporal_stops
        """
        new_inner = temporal_stops(self._inner, max_distance, timedelta_to_interval(min_duration))
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(new_inner)

    def __comparable(self, other: Temporal) -> bool:
        if not isinstance(other, Temporal):
            return False
        if self.BaseClass == other.BaseClass:
            return True
        if self.BaseClass in [int, float] and other.BaseClass in [int, float]:
            return True
        return False

    def __assert_comparable(self, other: Temporal) -> None:
        if not self.__comparable(other):
            raise TypeError(f'Operation not supported with type {other.__class__}. '
                            f'{self.BaseClass} and {other.BaseClass} are not comparable.')

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Temporal) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_temporal_temporal
        """
        self.__assert_comparable(other)
        result = teq_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Temporal) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_temporal_temporal
        """
        self.__assert_comparable(other)
        result = tne_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_less(self, other: Temporal) -> TBool:
        """
        Returns the temporal less than relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less than relation.

        MEOS Functions:
            tlt_temporal_temporal
        """
        self.__assert_comparable(other)
        result = tlt_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Temporal) -> TBool:
        """
        Returns the temporal less or equal relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less or equal relation.

        MEOS Functions:
            tle_temporal_temporal
        """
        self.__assert_comparable(other)
        result = tle_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Temporal) -> TBool:
        """
        Returns the temporal greater or equal relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater or equal relation.

        MEOS Functions:
            tge_temporal_temporal
        """
        self.__assert_comparable(other)
        result = tge_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_greater(self, other: Temporal) -> TBool:
        """
        Returns the temporal greater than relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater than relation.

        MEOS Functions:
            tgt_temporal_temporal
        """
        self.__assert_comparable(other)
        result = tgt_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    # ------------------------- Comparisons -----------------------------------
    def __lt__(self, other):
        """
        Returns whether `self` is less than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the less than relation.

        MEOS Functions:
            temporal_lt
        """
        return temporal_lt(self._inner, other._inner)

    def __le__(self, other):
        """
        Returns whether `self` is less or equal than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the less or equal than relation.

        MEOS Functions:
            temporal_le
        """
        return temporal_le(self._inner, other._inner)

    def __eq__(self, other):
        """
        Returns whether `self` is equal to `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the equality relation.

        MEOS Functions:
            temporal_eq
        """
        return temporal_eq(self._inner, other._inner)

    def __ne__(self, other):
        """
        Returns whether `self` is not equal to `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the not equal relation.

        MEOS Functions:
            temporal_ne
        """
        return temporal_ne(self._inner, other._inner)

    def __ge__(self, other):
        """
        Returns whether `self` is greater or equal than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the greater or equal than relation.

        MEOS Functions:
            temporal_ge
        """
        return temporal_ge(self._inner, other._inner)

    def __gt__(self, other):
        """
        Returns whether `self` is greater than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the greater than relation.

        MEOS Functions:
            temporal_gt
        """
        return temporal_gt(self._inner, other._inner)

    def __hash__(self) -> int:
        """
        Returns the hash of the temporal object.

        Returns:
            The hash of the temporal object.

        MEOS Functions:
            temporal_hash
        """
        return temporal_hash(self._inner)

    def __str__(self) -> str:
        """
        Returns the string representation of the `self`.
        """
        pass

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}'
                f'({self})')

    def __copy__(self) -> Self:
        """
        Returns a copy of the temporal object.
        """
        inner_copy = temporal_copy(self._inner)
        return self.__class__._factory(inner_copy)

