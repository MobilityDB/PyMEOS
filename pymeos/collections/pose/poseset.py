from __future__ import annotations

from typing import Optional, overload, Union, List

from pymeos_cffi import *

from .pose import Pose
from ..base import Set


class PoseSet(Set[Pose]):
    """
    Class for representing a set of pose values.

    ``PoseSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> PoseSet(string='{Pose(Point(1 1), 0.5), Pose(Point(2 2), 0.3)}')

    Another possibility is to create a ``PoseSet`` object from a list of
    :class:`Pose` instances.

        >>> PoseSet(elements=[Pose('Pose(Point(1 1), 0.5)')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "poseset"

    _parse_function = poseset_in
    _parse_value_function = lambda pose: (
        pose._inner if isinstance(pose, Pose) else pose_in(pose)
    )
    _make_function = lambda elements: poseset_make(elements, len(elements))

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            poseset_out
        """
        return poseset_out(self._inner, max_decimals)

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

    def elements(self) -> List[Pose]:
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

    def contains(self, content: Union[PoseSet, Pose]) -> bool:
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
    def intersection(self, other: Pose) -> Optional[Pose]: ...

    @overload
    def intersection(self, other: PoseSet) -> Optional[PoseSet]: ...

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

    def minus(self, other: Union[PoseSet, Pose]) -> Optional[PoseSet]:
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

    def subtract_from(self, other: Pose) -> Optional[Pose]:
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

    def union(self, other: Union[PoseSet, Pose]) -> PoseSet:
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
