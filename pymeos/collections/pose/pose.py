from __future__ import annotations

from typing import TYPE_CHECKING

import shapely.geometry.base as shp
from pymeos_cffi import *

if TYPE_CHECKING:
    from ...boxes import STBox


class Pose:
    """
    Class for representing a pose, i.e. a point with an orientation.

    ``Pose`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> Pose('Pose(Point(1 1), 0.5)')

    Another possibility is to provide the spatial point and the orientation
    with the corresponding parameters. For 2D poses the orientation is given
    by a single angle ``theta``.

        >>> Pose(point='Point(1 1)', theta=0.5)

    For 3D poses the orientation is given by a unit quaternion
    ``(W, X, Y, Z)``.

        >>> Pose(point='Point(1 1 1)', W=1.0, X=0.0, Y=0.0, Z=0.0)

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "pose"

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: str | None = None,
        *,
        point: str | shp.BaseGeometry | None = None,
        theta: float | None = None,
        W: float | None = None,
        X: float | None = None,
        Y: float | None = None,
        Z: float | None = None,
        srid: int | None = 0,
        geodetic: bool = False,
        _inner=None,
    ):
        assert (_inner is not None) or (string is not None) != (point is not None), (
            "Either string must be not None or point must be not None"
        )
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = pose_in(string)
        else:
            gs = geo_to_gserialized(point, geodetic)
            if W is not None and X is not None and Y is not None and Z is not None:
                self._inner = pose_make_point3d(gs, W, X, Y, Z)
            else:
                self._inner = pose_make_point2d(gs, float(theta or 0))
            if srid is not None:
                pose_set_srid(self._inner, srid)

    def __copy__(self) -> Pose:
        """
        Returns a copy of ``self``.

        Returns:
            A :class:`Pose` instance.

        MEOS Functions:
            pose_copy
        """
        inner_copy = pose_copy(self._inner)
        return Pose(_inner=inner_copy)

    @staticmethod
    def from_wkb(wkb: bytes) -> Pose:
        """
        Returns a `Pose` from its WKB representation.

        Args:
            wkb: WKB representation

        Returns:
            A new :class:`Pose` instance

        MEOS Functions:
            pose_from_wkb
        """
        result = pose_from_wkb(wkb)
        return Pose(_inner=result)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> Pose:
        """
        Returns a `Pose` from its WKB representation in hex-encoded ASCII.

        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`Pose` instance

        MEOS Functions:
            pose_from_hexwkb
        """
        result = pose_from_hexwkb(hexwkb)
        return Pose(_inner=result)

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Returns the string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            pose_as_text
        """
        return self.as_text(max_decimals)

    def __repr__(self):
        """
        Returns a string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            pose_out
        """
        return f"{self.__class__.__name__}({self})"

    def as_wkt(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the
            coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            pose_as_text
        """
        return pose_as_text(self._inner, max_decimals)

    def as_text(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the
            coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            pose_as_text
        """
        return pose_as_text(self._inner, max_decimals)

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the EWKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the
            coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            pose_as_ewkt
        """
        return pose_as_ewkt(self._inner, max_decimals)

    def as_wkb(self, endian: str = "") -> bytes:
        """
        Returns the WKB representation of ``self``.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` object with the WKB representation of ``self``.

        MEOS Functions:
            pose_as_wkb, wkb_variant_from_endian
        """
        return pose_as_wkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexwkb(self, endian: str = "") -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` object with the WKB representation of ``self`` in
            hex-encoded ASCII.

        MEOS Functions:
            pose_as_hexwkb, wkb_variant_from_endian
        """
        return pose_as_hexwkb(self._inner, wkb_variant_from_endian(endian))

    @staticmethod
    def from_text(string: str) -> Pose:
        """
        Returns a :class:`Pose` from its text, the inverse of :meth:`as_text`.

        Args:
            string: The text representation.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_from_text
        """
        return Pose(_inner=pose_from_text(string))

    @staticmethod
    def from_ewkt(ewkt: str) -> Pose:
        """
        Returns a :class:`Pose` from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT representation.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_from_text
        """
        return Pose(_inner=pose_from_text(ewkt))

    @staticmethod
    def from_ewkb(ewkb: bytes) -> Pose:
        """
        Returns a :class:`Pose` from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB representation.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_from_wkb
        """
        return Pose(_inner=pose_from_wkb(ewkb))

    @staticmethod
    def from_hexewkb(hexewkb: str) -> Pose:
        """
        Returns a :class:`Pose` from its hex-encoded EWKB, the inverse of :meth:`as_hexewkb`.

        Args:
            hexewkb: The HEXEWKB representation.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_from_hexwkb
        """
        return Pose(_inner=pose_from_hexwkb(hexewkb))

    def as_ewkb(self, endian: str = "") -> bytes:
        """
        Returns its Extended Well-Known Binary, its WKB carrying its SRID.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` instance.

        MEOS Functions:
            pose_as_ewkb, wkb_variant_from_endian
        """
        return pose_as_ewkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexewkb(self, endian: str = "") -> str:
        """
        Returns its Extended Well-Known Binary as a hex-encoded string.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            pose_as_hexewkb, wkb_variant_from_endian
        """
        return pose_as_hexewkb(self._inner, wkb_variant_from_endian(endian))

    # ------------------------- Conversions -----------------------------------
    def to_geometry(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns the point of ``self`` as a `shapely`
        :class:`~shapely.BaseGeometry` instance.

        Args:
            precision: The precision of the geometry coordinates.

        Returns:
            A new :class:`~shapely.BaseGeometry` instance.

        MEOS Functions:
            pose_to_point
        """
        return gserialized_to_shapely_geometry(pose_to_point(self._inner), precision)

    def to_stbox(self) -> STBox:
        """
        Returns the bounding box of ``self`` as an :class:`STBox` instance.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            pose_to_stbox
        """
        from ...boxes import STBox

        return STBox(_inner=pose_to_stbox(self._inner))

    # ------------------------- Accessors -------------------------------------
    def quaternion(self) -> shp.BaseGeometry:
        """
        Returns the orientation of ``self`` as a unit quaternion.

        Returns:
            The orientation of ``self``.

        MEOS Functions:
            pose_quaternion
        """
        return pose_quaternion(self._inner)

    def yaw(self) -> float:
        """
        Returns the rotation angle of ``self``.

        Returns:
            A :class:`float` instance.

        MEOS Functions:
            pose_yaw
        """
        return pose_yaw(self._inner)

    def __hash__(self) -> int:
        """
        Returns the hash of ``self``.

        Returns:
            A new :class:`int` instance.

        MEOS Functions:
            pose_hash
        """
        return pose_hash(self._inner)

    # ------------------------- Spatial Reference System ----------------------
    def srid(self) -> int:
        """
        Returns the SRID of ``self``.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            pose_srid
        """
        return pose_srid(self._inner)

    def set_srid(self, srid: int) -> Pose:
        """
        Returns a new :class:`Pose` with the SRID set to ``srid``.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_set_srid
        """
        result = pose_copy(self._inner)
        pose_set_srid(result, srid)
        return Pose(_inner=result)

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> Pose:
        """
        Returns a new :class:`Pose` with the coordinate values of ``self``
        rounded to ``max_decimals`` decimal places.

        Args:
            max_decimals: The number of decimal places.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_round
        """
        return Pose(_inner=pose_round(self._inner, max_decimals))

    def transform(self, srid: int) -> Pose:
        """
        Returns a new :class:`Pose` transformed to another SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_transform
        """
        return Pose(_inner=pose_transform(self._inner, srid))

    def transform_pipeline(self, pipeline: str, srid: int, is_forward: bool = True) -> Pose:
        """
        Returns a new :class:`Pose` transformed using a transformation
        pipeline.

        Args:
            pipeline: The transformation pipeline.
            srid: The desired SRID.
            is_forward: Whether to apply the pipeline in the forward direction.

        Returns:
            A new :class:`Pose` instance.

        MEOS Functions:
            pose_transform_pipeline
        """
        return Pose(_inner=pose_transform_pipeline(self._inner, pipeline, srid, is_forward))

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: shp.BaseGeometry | Pose | STBox) -> float:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: An object to check the distance to.

        Returns:
            A :class:`float` instance.

        MEOS Functions:
            distance_pose_geo, distance_pose_pose, distance_pose_stbox
        """
        from ...boxes import STBox

        if isinstance(other, shp.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            return distance_pose_geo(self._inner, gs)
        elif isinstance(other, Pose):
            return distance_pose_pose(self._inner, other._inner)
        elif isinstance(other, STBox):
            return distance_pose_stbox(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Returns whether ``self`` is equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if equal, ``False`` otherwise.

        MEOS Functions:
            pose_eq
        """
        if isinstance(other, self.__class__):
            return pose_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Returns whether ``self`` is not equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if not equal, ``False`` otherwise.

        MEOS Functions:
            pose_ne
        """
        if isinstance(other, self.__class__):
            return pose_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Returns whether ``self`` is less than ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if less than, ``False`` otherwise.

        MEOS Functions:
            pose_lt
        """
        if isinstance(other, self.__class__):
            return pose_lt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __le__(self, other):
        """
        Returns whether ``self`` is less than or equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if less than or equal, ``False`` otherwise.

        MEOS Functions:
            pose_le
        """
        if isinstance(other, self.__class__):
            return pose_le(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __gt__(self, other):
        """
        Returns whether ``self`` is greater than ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if greater than, ``False`` otherwise.

        MEOS Functions:
            pose_gt
        """
        if isinstance(other, self.__class__):
            return pose_gt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __ge__(self, other):
        """
        Returns whether ``self`` is greater than or equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if greater than or equal, ``False`` otherwise.

        MEOS Functions:
            pose_ge
        """
        if isinstance(other, self.__class__):
            return pose_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def cmp(self, other: Pose) -> int:
        """
        Returns the comparison value between ``self`` and ``other``.

        Args:
            other: The :class:`Pose` to compare with ``self``.

        Returns:
            An :class:`int` instance: -1, 0 or 1.

        MEOS Functions:
            pose_cmp
        """
        return pose_cmp(self._inner, other._inner)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`Pose` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return Pose(string=value)
