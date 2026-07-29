# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# VERBATIM oracle snapshot -- DO NOT EDIT, DO NOT IMPORT.
#
# The hand-written editorial dispatch methods extracted verbatim (AST,
# byte-for-byte bodies) from the hand-written PyMEOS sources on branch
# `feat/extended-temporal-types`, for geo (TPoint) + the four temporal
# concretes (TFloat/TInt/TBool/TText).
#
# This file is NEVER executed. It is parsed by tests/test_oo_codegen_
# coverage.py to A/B-prove that the metadata-driven consumer
# (codegen.py --mixin-from-dispatch, fed _d1-dispatch-extended-
# fixture.json == MEOS-API #10 objectModel.dispatch) reproduces these
# bodies' dispatch behaviour exactly -- equivalence by construction at
# the catalog level, the same gate the 4 derivable families pass via
# --verify-oo-roundtrip.


class _Oracle_tfloat:
    def always_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_tfloat_float, always_eq_temporal_temporal
        """
        if isinstance(value, float):
            return always_eq_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_tfloat_float, always_ne_temporal_temporal
        """
        if isinstance(value, float):
            return always_ne_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tfloat_float, ever_eq_temporal_temporal
        """
        if isinstance(value, float):
            return ever_eq_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tfloat_float, ever_ne_temporal_temporal
        """
        if isinstance(value, float):
            return ever_ne_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def temporal_equal(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tfloat_float, teq_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = teq_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_tfloat_float, tne_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tne_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def at(
        self,
        other: Union[
            float,
            int,
            FloatSet,
            IntSet,
            FloatSpan,
            IntSpan,
            FloatSpanSet,
            IntSpanSet,
            TBox,
            Time,
        ],
    ) -> TFloat:
        """
        Returns a new temporal float with the values of `self` restricted to
        the value or time `other`.

        Args:
            other: Value or time to restrict to.

        Returns:
            A new temporal float.

        MEOS Functions:
            tfloat_at_value, temporal_at_values, tnumber_at_span, tnumber_at_spanset,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan,
            temporal_at_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tfloat_at_value(self._inner, float(other))
        elif isinstance(other, IntSet):
            return super().at(other.to_floatset())
        elif isinstance(other, IntSpan):
            return super().at(other.to_floatspan())
        elif isinstance(other, IntSpanSet):
            return super().at(other.to_floatspanset())
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(
        self,
        other: Union[
            float,
            int,
            FloatSet,
            IntSet,
            FloatSpan,
            IntSpan,
            FloatSpanSet,
            IntSpanSet,
            TBox,
            Time,
        ],
    ) -> Temporal:
        """
        Returns a new temporal float with the values of `self` restricted to
        the complement of the time or value `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal float.

        MEOS Functions:
            tfloat_minus_value, temporal_minus_values, tnumber_minus_span, tnumber_minus_spanset,
            temporal_minus_timestamp, temporal_minus_tstzset,
            temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tfloat_minus_value(self._inner, float(other))
        elif isinstance(other, IntSet):
            return super().minus(other.to_floatset())
        elif isinstance(other, IntSpan):
            return super().minus(other.to_floatspan())
        elif isinstance(other, IntSpanSet):
            return super().minus(other.to_floatspanset())
        else:
            return super().minus(other)
        return Temporal._factory(result)


class _Oracle_tint:
    def always_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_tint_int, always_eq_temporal_temporal
        """
        if isinstance(value, int):
            return always_eq_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_tint_int, always_ne_temporal_temporal
        """
        if isinstance(value, int):
            return always_ne_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_eq_tint_int, ever_eq_temporal_temporal
        """
        if isinstance(value, int):
            return ever_eq_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tint_int, ever_ne_temporal_temporal
        """
        if isinstance(value, int):
            return ever_ne_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def temporal_equal(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tint_int, teq_temporal_temporal
        """
        if isinstance(other, int):
            result = teq_tint_int(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_tint_int, tne_temporal_temporal
        """
        if isinstance(other, int):
            result = tne_tint_int(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def at(
        self,
        other: Union[
            int,
            float,
            IntSet,
            FloatSet,
            IntSpan,
            FloatSpan,
            IntSpanSet,
            FloatSpanSet,
            TBox,
            Time,
        ],
    ) -> TInt:
        """
        Returns a new temporal int with th  e values of `self` restricted to
        the time or value `other`.

        Args:
            other: Time or value to restrict to.

        Returns:
            A new temporal int.

        MEOS Functions:
            tint_at_value, temporal_at_values, tnumber_at_span, tnumber_at_spanset,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan,
            temporal_at_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tint_at_value(self._inner, int(other))
        elif isinstance(other, FloatSet):
            return super().at(other.to_intset())
        elif isinstance(other, FloatSpan):
            return super().at(other.to_intspan())
        elif isinstance(other, FloatSpanSet):
            return super().at(other.to_intspanset())
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(
        self,
        other: Union[
            int,
            float,
            IntSet,
            FloatSet,
            IntSpan,
            FloatSpan,
            IntSpanSet,
            FloatSpanSet,
            TBox,
            Time,
        ],
    ) -> TInt:
        """
        Returns a new temporal int with the values of `self` restricted to the
        complement of the time or value `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal int.

        MEOS Functions:
            tint_minus_value, temporal_minus_values, tnumber_minus_span, tnumber_minus_spanset,
            temporal_minus_timestamp, temporal_minus_tstzset,
            temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tint_minus_value(self._inner, int(other))
        elif isinstance(other, FloatSet):
            return super().minus(other.to_intset())
        elif isinstance(other, FloatSpan):
            return super().minus(other.to_intspan())
        elif isinstance(other, FloatSpanSet):
            return super().minus(other.to_intspanset())
        else:
            return super().minus(other)
        return Temporal._factory(result)


class _Oracle_tbool:
    def temporal_equal(self, other: Union[bool, TBool]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A temporal or boolean object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tbool_tbool, teq_temporal_temporal
        """
        if isinstance(other, bool):
            result = teq_tbool_bool(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[bool, TBool]) -> TBool:
        """
        Returns the temporal inequality relation between `self` and `other`.

        Args:
            other: A temporal or boolean object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal inequality relation.

        MEOS Functions:
            tne_tbool_tbool, tne_temporal_temporal
        """
        if isinstance(other, bool):
            result = tne_tbool_bool(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def at(self, other: Union[bool, Time]) -> TBool:
        """
        Returns a new temporal boolean with the values of `self` restricted to
        the time or value `other`.

        Args:
            other: Time or value to restrict to.

        Returns:
            A new temporal boolean.

        MEOS Functions:
            tbool_at_value, temporal_at_timestamp, temporal_at_tstzset,
            temporal_at_tstzspan, temporal_at_tstzspanset
        """
        if isinstance(other, bool):
            result = tbool_at_value(self._inner, other)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[bool, Time]) -> TBool:
        """
        Returns a new temporal boolean with the values of `self` restricted to
        the complement of the time or value
        `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal boolean.

        MEOS Functions:
            tbool_minus_value, temporal_minus_timestamp,
            temporal_minus_tstzset, temporal_minus_tstzspan,
            temporal_minus_tstzspanset
        """
        if isinstance(other, bool):
            result = tbool_minus_value(self._inner, other)
        else:
            return super().minus(other)
        return Temporal._factory(result)


class _Oracle_ttext:
    def always_equal(self, value: Union[str, TText]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_ttext_text, always_eq_temporal_temporal
        """
        if isinstance(value, str):
            return always_eq_ttext_text(self._inner, value) > 0
        elif isinstance(value, TText):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[str, TText]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_ttext_text, always_ne_temporal_temporal
        """
        if isinstance(value, str):
            return always_ne_ttext_text(self._inner, value) > 0
        elif isinstance(value, TText):
            return always_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[str, TText]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_ttext_text, ever_eq_temporal_temporal
        """
        if isinstance(value, str):
            return ever_eq_ttext_text(self._inner, value) > 0
        elif isinstance(value, TText):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[str, TText]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_ttext_text, ever_ne_temporal_temporal
        """
        if isinstance(value, str):
            return ever_ne_ttext_text(self._inner, value) > 0
        elif isinstance(value, TText):
            return ever_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def temporal_equal(self, other: Union[str, TText]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_ttext_text, teq_temporal_temporal
        """
        if isinstance(other, str):
            result = teq_ttext_text(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[str, TText]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_ttext_text, tne_temporal_temporal
        """
        if isinstance(other, str):
            result = tne_ttext_text(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def at(
        self, other: Union[str, List[str], datetime, TsTzSet, TsTzSpan, TsTzSpanSet]
    ) -> TText:
        """
        Returns a new temporal string with the values of `self` restricted to
        the time or value `other`.

        Args:
            other: Time or value to restrict to.

        Returns:
            A new temporal string.

        MEOS Functions:
            ttext_at_value, temporal_at_timestamp, temporal_at_tstzset,
            temporal_at_tstzspan, temporal_at_tstzspanset
        """
        if isinstance(other, str):
            result = ttext_at_value(self._inner, other)
        elif isinstance(other, list) and isinstance(other[0], str):
            result = temporal_at_values(self._inner, textset_make(other))
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(
        self, other: Union[str, List[str], datetime, TsTzSet, TsTzSpan, TsTzSpanSet]
    ) -> TText:
        """
        Returns a new temporal string with the values of `self` restricted to
        the complement of the time or value `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal string.

        MEOS Functions:
            ttext_minus_value, temporal_minus_timestamp,
            temporal_minus_tstzset, temporal_minus_tstzspan,
            temporal_minus_tstzspanset
        """
        if isinstance(other, str):
            result = ttext_minus_value(self._inner, other)
        elif isinstance(other, list) and isinstance(other[0], str):
            result = temporal_minus_values(self._inner, textset_make(other))
        else:
            return super().minus(other)
        return Temporal._factory(result)


class _Oracle_tpoint:
    def at(self, other: Union[shpb.BaseGeometry, GeoSet, STBox, Time]) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to `other`.

        Args:
            other: An object to restrict the values of `self` to.

        Returns:
            A new :TPoint: with the values of `self` restricted to `other`.

        MEOS Functions:
            tpoint_at_value, tgeo_at_stbox, temporal_at_values,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan, temporal_at_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, shp.Point):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_at_value(self._inner, gs)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_at_geom(self._inner, gs)
        elif isinstance(other, GeoSet):
            result = temporal_at_values(self._inner, other._inner)
        elif isinstance(other, STBox):
            result = tgeo_at_stbox(self._inner, other._inner, True)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[shpb.BaseGeometry, GeoSet, STBox, Time]) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to the complement of `other`.

        Args:
            other: An object to restrict the values of `self` to the complement of.

        Returns:
            A new :TPoint: with the values of `self` restricted to the complement of `other`.

        MEOS Functions:
            tpoint_minus_value, tgeo_minus_stbox, temporal_minus_values,
            temporal_minus_timestamp, temporal_minus_tstzset, temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, shp.Point):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_minus_value(self._inner, gs)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_minus_geom(self._inner, gs)
        elif isinstance(other, GeoSet):
            result = temporal_minus_values(self._inner, other._inner)
        elif isinstance(other, STBox):
            result = tgeo_minus_stbox(self._inner, other._inner, True)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    def distance(self, other: Union[shpb.BaseGeometry, TPoint, STBox]) -> TFloat:
        """
        Returns the temporal distance between the temporal point and `other`.

        Args:
            other: An object to check the distance to.

        Returns:
            A new :class:`TFloat` indicating the temporal distance between the temporal point and `other`.

        MEOS Functions:
            tdistance_tgeo_geo, tdistance_tgeo_tgeo
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tdistance_tgeo_geo(self._inner, gs)
        elif isinstance(other, STBox):
            result = tdistance_tgeo_geo(self._inner, stbox_to_geo(other._inner))
        elif isinstance(other, TPoint):
            result = tdistance_tgeo_tgeo(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def nearest_approach_distance(
        self, other: Union[shpb.BaseGeometry, STBox, TPoint]
    ) -> float:
        """
        Returns the nearest approach distance between the temporal point and `other`.

        Args:
            other: An object to check the nearest approach distance to.

        Returns:
            A :class:`float` indicating the nearest approach distance between the temporal point and `other`.

        MEOS Functions:
            nad_tgeo_geo, nad_tgeo_stbox, nad_tgeo_tgeo
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            return nad_tgeo_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_tgeo_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return nad_tgeo_tgeo(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
