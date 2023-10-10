from pymeos import TBool, TInt, TFloat, TText, TGeomPoint, TGeogPoint, TBox, STBox, TimestampSet, Period, PeriodSet, \
    GeometrySet, GeographySet, TextSet, IntSet, IntSpan, IntSpanSet, FloatSpan, FloatSet, FloatSpanSet

db_objects = [
    # Temporal
    TBool, TInt, TFloat, TText, TGeomPoint, TGeogPoint,
    # Boxes
    TBox, STBox,
    # Collections
    TimestampSet, Period, PeriodSet,
    GeometrySet, GeographySet,
    TextSet,
    IntSet, IntSpan, IntSpanSet,
    FloatSet, FloatSpan, FloatSpanSet
]
