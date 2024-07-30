from __future__ import annotations

from abc import ABC
from typing import List, overload, Optional, Union, TypeVar

import shapely as shp
from pymeos_cffi import (
    geoset_start_value,
    gserialized_to_shapely_geometry,
    geoset_end_value,
    geoset_value_n,
    geoset_values,
    intersection_set_geo,
    minus_set_geo,
    union_set_geo,
    geoset_as_ewkt,
    geoset_as_text,
    geoset_out,
    geoset_make,
    geoset_srid,
    geoset_round,
    minus_geo_set,
    geomset_in,
    geogset_in,
    pgis_geometry_in,
    geometry_to_gserialized,
    pgis_geography_in,
    geography_to_gserialized,
    intersection_set_set,
    minus_set_set,
    union_set_set,
)

from ..base import Set

Self = TypeVar("Self", bound="GeoSet")


class GeoSet(Set[shp.Geometry], ABC):
    __slots__ = ["_inner"]

    _make_function = geoset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            geoset_out
        """
        return geoset_out(self._inner, max_decimals)

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the EWKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            geoset_as_ewkt
        """
        return geoset_as_ewkt(self._inner, max_decimals)

    def as_wkt(self, max_decimals: int = 15):
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            geoset_as_text
        """
        return geoset_as_text(self._inner, max_decimals)

    def as_text(self, max_decimals: int = 15):
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            geoset_as_text
        """
        return geoset_as_text(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self):
        raise NotImplementedError()

    def to_span(self):
        raise NotImplementedError()

    # ------------------------- Accessors -------------------------------------

    def start_element(self) -> shp.Geometry:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`Geometry` instance

        MEOS Functions:
            geoset_start_value
        """
        return gserialized_to_shapely_geometry(geoset_start_value(self._inner))

    def end_element(self) -> shp.Geometry:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`Geometry` instance

        MEOS Functions:
            geoset_end_value
        """
        return gserialized_to_shapely_geometry(geoset_end_value(self._inner))

    def element_n(self, n: int) -> shp.Geometry:
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`Geometry` instance

        MEOS Functions:
            geoset_value_n
        """
        super().element_n(n)
        return gserialized_to_shapely_geometry(geoset_value_n(self._inner, n + 1)[0])

    def elements(self) -> List[shp.Geometry]:
        """
        Returns a list of all elements in ``self``.

        Returns:
            A list of :class:`Geometry` instances

        MEOS Functions:
            geoset_values
        """
        elems = geoset_values(self._inner)
        return [
            gserialized_to_shapely_geometry(elems[i])
            for i in range(self.num_elements())
        ]

    def srid(self) -> int:
        """
        Returns the SRID of ``self``.

        Returns:
            An integer

        MEOS Functions:
            geoset_srid
        """
        return geoset_srid(self._inner)

    # ------------------------- Topological Operations --------------------------------

    def contains(self, content: Union[GeoSet, str]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise
        """
        return super().contains(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: shp.Geometry) -> Optional[shp.Geometry]: ...

    @overload
    def intersection(self, other: GeoSet) -> Optional[GeoSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`GeoSet` or :class:`Geometry` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the intersection is empty.

        MEOS Functions:
            intersection_set_geo, intersection_set_set
        """
        if isinstance(other, shp.Geometry):
            return gserialized_to_shapely_geometry(
                intersection_set_geo(self._inner, geometry_to_gserialized(other))[0]
            )
        elif isinstance(other, GeoSet):
            result = intersection_set_set(self._inner, other._inner)
            return GeoSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[GeoSet, shp.Geometry]) -> Optional[GeoSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`GeoSet` or :class:`Geometry` instance

        Returns:
            A :class:`GeoSet` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_set_geo, minus_set_set

        See Also:
            :meth:`subtract_from`
        """
        if isinstance(other, shp.Geometry):
            result = minus_set_geo(self._inner, geometry_to_gserialized(other))
            return GeoSet(_inner=result) if result is not None else None
        elif isinstance(other, GeoSet):
            result = minus_set_set(self._inner, other._inner)
            return GeoSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: shp.Geometry) -> Optional[shp.Geometry]:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`Geometry` instance

        Returns:
            A :class:`Geometry` instance.

        MEOS Functions:
            minus_geo_set

        See Also:
            :meth:`minus`
        """
        result = minus_geo_set(geometry_to_gserialized(other), self._inner)
        return (
            gserialized_to_shapely_geometry(result[0]) if result is not None else None
        )

    def union(self, other: Union[GeoSet, shp.Geometry]) -> GeoSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`GeoSet` or :class:`Geometry` instance

        Returns:
            A :class:`GeoSet` instance.

        MEOS Functions:
            union_set_geo, union_set_set
        """
        if isinstance(other, shp.Geometry):
            result = union_set_geo(self._inner, geometry_to_gserialized(other))
            return GeoSet(_inner=result) if result is not None else None
        elif isinstance(other, GeoSet):
            result = union_set_set(self._inner, other._inner)
            return GeoSet(_inner=result) if result is not None else None
        else:
            return super().union(other)

    # ------------------------- Transformations ------------------------------------

    def round(self: Self, max_decimals: int) -> Self:
        """
        Rounds the coordinate values to a number of decimal places.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A new :class:`GeoSet` object of the same subtype of ``self``.

        MEOS Functions:
            tpoint_roundgeoset_round
        """
        return self.__class__(_inner=geoset_round(self._inner, max_decimals))


class GeometrySet(GeoSet):
    _mobilitydb_name = "geomset"

    _parse_function = geomset_in
    _parse_value_function = lambda x: (
        pgis_geometry_in(x, -1) if isinstance(x, str) else geometry_to_gserialized(x)
    )


class GeographySet(GeoSet):
    _mobilitydb_name = "geogset"

    _parse_function = geogset_in
    _parse_value_function = lambda x: (
        pgis_geography_in(x, -1) if isinstance(x, str) else geography_to_gserialized(x)
    )
