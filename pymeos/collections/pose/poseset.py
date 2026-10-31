from __future__ import annotations

from typing import overload

from pymeos_cffi import *

from ..base import Set
from .pose import Pose


class PoseSet(Set[Pose]):
    """
    Class for representing a set of pose values.

    ``PoseSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> PoseSet(string='{"Pose(Point(1 1), 0.5)", "Pose(Point(2 2), 0.3)"}')

    Another possibility is to create a ``PoseSet`` object from a list of
    :class:`Pose` instances.

        >>> PoseSet(elements=[Pose('Pose(Point(1 1), 0.5)')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "poseset"

    _parse_function = poseset_in
    _parse_value_function = lambda pose: pose._inner if isinstance(pose, Pose) else pose_in(pose)
    _make_function = poseset_make

    # ------------------------- Constructors ----------------------------------

    @classmethod
    def from_ewkb(cls: type[Self], ewkb: bytes) -> Self:
        """
        Returns a :class:`PoseSet` from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB representation.

        Returns:
            A new :class:`PoseSet` instance.

        MEOS Functions:
            set_from_wkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_wkb(ewkb))

    @classmethod
    def from_hexewkb(cls: type[Self], hexewkb: str) -> Self:
        """
        Returns a :class:`PoseSet` from its HEXEWKB, the inverse of :meth:`as_hexewkb`.

        Args:
            hexewkb: The HEXEWKB representation.

        Returns:
            A new :class:`PoseSet` instance.

        MEOS Functions:
            set_from_hexwkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_hexwkb(hexewkb))

    @classmethod
    def from_ewkt(cls: type[Self], ewkt: str) -> Self:
        """
        Returns a :class:`PoseSet` from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT representation.

        Returns:
            A new :class:`PoseSet` instance.

        MEOS Functions:
            <type>_in
        """
        return cls.from_text(ewkt)

    def as_ewkb(self, endian: str = "") -> bytes:
        """
        Returns the EWKB representation of ``self``, carrying its SRID.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` instance.

        MEOS Functions:
            spatialset_as_ewkb, wkb_variant_from_endian
        """
        return spatialset_as_ewkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexewkb(self, endian: str = "") -> str:
        """
        Returns the HEXEWKB representation of ``self``, carrying its SRID.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_hexewkb, wkb_variant_from_endian
        """
        return spatialset_as_hexewkb(self._inner, wkb_variant_from_endian(endian))[0]

    # ------------------------- Output ----------------------------------------

    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            spatialset_as_text
        """
        return self.as_text(max_decimals)

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the EWKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_ewkt
        """
        return spatialset_as_ewkt(self._inner, max_decimals)

    def as_wkt(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_text
        """
        return spatialset_as_text(self._inner, max_decimals)

    def as_text(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_text
        """
        return spatialset_as_text(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self):
        raise NotImplementedError()

    def to_span(self):
        raise NotImplementedError()

    # ------------------------- Accessors -------------------------------------

    def start_element(self) -> Pose:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`Pose` instance

        MEOS Functions:
            poseset_start_value
        """
        return Pose(_inner=poseset_start_value(self._inner))

    def end_element(self) -> Pose:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`Pose` instance

        MEOS Functions:
            poseset_end_value
        """
        return Pose(_inner=poseset_end_value(self._inner))

    def element_n(self, n: int) -> Pose:
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`Pose` instance

        MEOS Functions:
            poseset_value_n
        """
        super().element_n(n)
        return Pose(_inner=poseset_value_n(self._inner, n + 1)[0])

    def elements(self) -> list[Pose]:
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`Pose` instances

        MEOS Functions:
            poseset_values
        """
        elems = poseset_values(self._inner)
        return [Pose(_inner=elems[i]) for i in range(self.num_elements())]

    # ------------------------- Topological Operations ------------------------

    def contains(self, content: PoseSet | Pose) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set, contains_set_pose
        """
        if isinstance(content, Pose):
            return contains_set_pose(self._inner, content._inner)
        else:
            return super().contains(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: Pose) -> Pose | None: ...

    @overload
    def intersection(self, other: PoseSet) -> PoseSet | None: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`PoseSet` or :class:`Pose` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the
            intersection is empty.

        MEOS Functions:
            intersection_set_pose, intersection_set_set
        """
        if isinstance(other, Pose):
            result = intersection_set_pose(self._inner, other._inner)
            return Pose(_inner=result) if result is not None else None
        elif isinstance(other, PoseSet):
            result = intersection_set_set(self._inner, other._inner)
            return PoseSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: PoseSet | Pose) -> PoseSet | None:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`PoseSet` or :class:`Pose` instance

        Returns:
            A :class:`PoseSet` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_set_pose, minus_set_set
        """
        if isinstance(other, Pose):
            result = minus_set_pose(self._inner, other._inner)
            return PoseSet(_inner=result) if result is not None else None
        elif isinstance(other, PoseSet):
            result = minus_set_set(self._inner, other._inner)
            return PoseSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: Pose) -> Pose | None:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`Pose` instance

        Returns:
            A :class:`Pose` instance.

        MEOS Functions:
            minus_pose_set

        See Also:
            :meth:`minus`
        """
        result = minus_pose_set(other._inner, self._inner)
        return Pose(_inner=result) if result is not None else None

    def union(self, other: PoseSet | Pose) -> PoseSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`PoseSet` or :class:`Pose` instance

        Returns:
            A :class:`PoseSet` instance.

        MEOS Functions:
            union_set_pose, union_set_set
        """
        if isinstance(other, Pose):
            result = union_set_pose(self._inner, other._inner)
            return PoseSet(_inner=result) if result is not None else None
        elif isinstance(other, PoseSet):
            result = union_set_set(self._inner, other._inner)
            return PoseSet(_inner=result) if result is not None else None
        else:
            return super().union(other)
