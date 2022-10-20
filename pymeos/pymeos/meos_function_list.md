
## Initialization of the MEOS library
 

- [x] `extern void meos_initialize(const char *tz_str);`
- [x] `extern void meos_finish(void);`

## Functions for input/output PostgreSQL time types
 

- [ ] `extern bool bool_in(const char *in_str);`
- [ ] `extern char *bool_out(bool b);`
- [ ] `extern DateADT pg_date_in(const char *str);`
- [ ] `extern char *pg_date_out(DateADT date);`
- [ ] `extern int pg_interval_cmp(const Interval *interval1, const Interval *interval2);`
- [ ] `extern Interval *pg_interval_in(const char *str, int32 typmod);`
- [ ] `extern Interval *pg_interval_make(int32 years, int32 months, int32 weeks, int32 days, int32 hours, int32 mins, double secs);`
- [ ] `extern char *pg_interval_out(Interval *span);`
- [ ] `extern Interval *pg_interval_pl(const Interval *span1, const Interval *span2);`
- [ ] `extern TimeADT pg_time_in(const char *str, int32 typmod);`
- [ ] `extern char *pg_time_out(TimeADT time);`
- [ ] `extern Timestamp pg_timestamp_in(const char *str, int32 typmod);`
- [ ] `extern Interval *pg_timestamp_mi(TimestampTz dt1, TimestampTz dt2);`
- [ ] `extern TimestampTz pg_timestamp_mi_interval(TimestampTz timestamp, const Interval *span);`
- [ ] `extern char *pg_timestamp_out(Timestamp dt);`
- [ ] `extern TimestampTz pg_timestamp_pl_interval(TimestampTz timestamp, const Interval *span);`
- [ ] `extern TimestampTz pg_timestamptz_in(const char *str, int32 typmod);`
- [ ] `extern char *pg_timestamptz_out(TimestampTz dt);`

## Functions for input/output and manipulation of PostGIS types
 

- [ ] `extern bytea *gserialized_as_ewkb(const GSERIALIZED *geom, char *type);`
- [ ] `extern char *gserialized_as_geojson(const GSERIALIZED *geom, int option, int precision, char *srs);`
- [ ] `extern char *gserialized_as_hexewkb(const GSERIALIZED *geom, const char *type);`
- [ ] `extern char *gserialized_as_text(const GSERIALIZED *geom, int precision);`
- [ ] `extern GSERIALIZED *gserialized_from_ewkb(const bytea *bytea_wkb, int32 srid);`
- [ ] `extern GSERIALIZED *gserialized_from_geojson(const char *geojson);`
- [ ] `extern GSERIALIZED *gserialized_from_hexewkb(const char *wkt);`
- [ ] `extern GSERIALIZED *gserialized_from_text(char *wkt, int srid);`
- [ ] `extern GSERIALIZED *gserialized_in(char *input, int32 geom_typmod);`
- [ ] `extern char *gserialized_out(const GSERIALIZED *geom);`
- [ ] `extern bool gserialized_same(const GSERIALIZED *geom1, const GSERIALIZED *geom2);`

## Functions for span and time types
 

### Input/output functions for span and time types

- [ ] `extern Span *floatspan_in(const char *str);` Class not defined in PyMEOS
- [ ] `extern char *floatspan_out(const Span *s, int maxdd);` Class not defined in PyMEOS
- [ ] `extern Span *intspan_in(const char *str);` Class not defined in PyMEOS
- [ ] `extern char *intspan_out(const Span *s);` Class not defined in PyMEOS
- [x] `extern Period *period_in(const char *str);`
- [x] `extern char *period_out(const Span *s);`
- [x] `extern char *periodset_as_hexwkb(const PeriodSet *ps, uint8_t variant, size_t *size_out);`
- [ ] `extern uint8_t *periodset_as_wkb(const PeriodSet *ps, uint8_t variant, size_t *size_out);` WKB is not being implemented directly (only HexWKB)
- [x] `extern PeriodSet *periodset_from_hexwkb(const char *hexwkb);`
- [ ] `extern PeriodSet *periodset_from_wkb(const uint8_t *wkb, int size);` WKB is not being implemented directly (only HexWKB)
- [x] `extern PeriodSet *periodset_in(const char *str);`
- [x] `extern char *periodset_out(const PeriodSet *ps);`
- [x] `extern char *span_as_hexwkb(const Span *s, uint8_t variant, size_t *size_out);`
- [ ] `extern uint8_t *span_as_wkb(const Span *s, uint8_t variant, size_t *size_out);` WKB is not being implemented directly (only HexWKB)
- [x] `extern Span *span_from_hexwkb(const char *hexwkb);`
- [ ] `extern Span *span_from_wkb(const uint8_t *wkb, int size);` WKB is not being implemented directly (only HexWKB)
- [x] `extern char *span_out(const Span *s, Datum arg);`
- [x] `extern char *timestampset_as_hexwkb(const TimestampSet *ts, uint8_t variant, size_t *size_out);`
- [ ] `extern uint8_t *timestampset_as_wkb(const TimestampSet *ts, uint8_t variant, size_t *size_out);` WKB is not being implemented directly (only HexWKB)
- [x] `extern TimestampSet *timestampset_from_hexwkb(const char *hexwkb);`
- [ ] `extern TimestampSet *timestampset_from_wkb(const uint8_t *wkb, int size);` WKB is not being implemented directly (only HexWKB)
- [x] `extern TimestampSet *timestampset_in(const char *str);`
- [x] `extern char *timestampset_out(const TimestampSet *ts);`



### Constructor functions for span and time types

- [ ] `extern Span *floatspan_make(double lower, double upper, bool lower_inc, bool upper_inc);` Class not defined in PyMEOS
- [ ] `extern Span *intspan_make(int lower, int upper, bool lower_inc, bool upper_inc);` Class not defined in PyMEOS
- [x] `extern Period *period_make(TimestampTz lower, TimestampTz upper, bool lower_inc, bool upper_inc);`
- [x] `extern PeriodSet *periodset_copy(const PeriodSet *ps);`
- [x] `extern PeriodSet *periodset_make(const Period **periods, int count, bool normalize);`
- [ ] `extern PeriodSet *periodset_make_free(Period **periods, int count, bool normalize);` Not necessary in PyMEOS
- [x] `extern Span *span_copy(const Span *s);`
- [x] `extern TimestampSet *timestampset_copy(const TimestampSet *ts);`
- [x] `extern TimestampSet *timestampset_make(const TimestampTz *times, int count);`
- [ ] `extern TimestampSet *timestampset_make_free(TimestampTz *times, int count);` Not necessary in PyMEOS



### Cast functions for span and time types

- [ ] `extern Span *float_to_floaspan(double d);` Class not defined in PyMEOS
- [ ] `extern Span *int_to_intspan(int i);` Class not defined in PyMEOS
- [x] `extern PeriodSet *period_to_periodset(const Period *period);`
- [x] `extern Period *periodset_to_period(const PeriodSet *ps);`
- [x] `extern Period *timestamp_to_period(TimestampTz t);`
- [x] `extern PeriodSet *timestamp_to_periodset(TimestampTz t);`
- [x] `extern TimestampSet *timestamp_to_timestampset(TimestampTz t);`
- [x] `extern PeriodSet *timestampset_to_periodset(const TimestampSet *ts);`



### Accessor functions for span and time types

- [ ] `extern double floatspan_lower(const Span *s);` Class not defined in PyMEOS
- [ ] `extern double floatspan_upper(const Span *s);` Class not defined in PyMEOS
- [ ] `extern int intspan_lower(const Span *s);` Class not defined in PyMEOS
- [ ] `extern int intspan_upper(const Span *s);` Class not defined in PyMEOS
- [ ] `extern Interval *period_duration(const Span *s);` Implemented in python
- [x] `extern TimestampTz period_lower(const Period *p);`
- [x] `extern TimestampTz period_upper(const Period *p);`
- [x] `extern Interval *periodset_duration(const PeriodSet *ps);`
- [x] `extern Period *periodset_end_period(const PeriodSet *ps);`
- [x] `extern TimestampTz periodset_end_timestamp(const PeriodSet *ps);`
- [x] `extern uint32 periodset_hash(const PeriodSet *ps);`
- [ ] `extern uint64 periodset_hash_extended(const PeriodSet *ps, uint64 seed);`
- [ ] `extern int periodset_mem_size(const PeriodSet *ps);`
- [x] `extern int periodset_num_periods(const PeriodSet *ps);`
- [x] `extern int periodset_num_timestamps(const PeriodSet *ps);`
- [x] `extern Period *periodset_period_n(const PeriodSet *ps, int i);`
- [x] `extern const Period **periodset_periods(const PeriodSet *ps, int *count);`
- [x] `extern Period *periodset_start_period(const PeriodSet *ps);`
- [x] `extern TimestampTz periodset_start_timestamp(const PeriodSet *ps);`
- [ ] `extern Interval *periodset_timespan(const PeriodSet *ps);` Implemented in python
- [x] `extern bool periodset_timestamp_n(const PeriodSet *ps, int n, TimestampTz *result);`
- [x] `extern TimestampTz *periodset_timestamps(const PeriodSet *ps, int *count);`
- [x] `extern uint32 span_hash(const Span *s);`
- [ ] `extern uint64 span_hash_extended(const Span *s, uint64 seed);`
- [ ] `extern bool span_lower_inc(const Span *s);` Access information directly
- [ ] `extern bool span_upper_inc(const Span *s);` Access information directly
- [x] `extern double span_width(const Span *s);`
- [x] `extern TimestampTz timestampset_end_timestamp(const TimestampSet *ss);`
- [x] `extern uint32 timestampset_hash(const TimestampSet *ss);`
- [ ] `extern uint64 timestampset_hash_extended(const TimestampSet *ss, uint64 seed);`
- [ ] `extern int timestampset_mem_size(const TimestampSet *ss);`
- [x] `extern int timestampset_num_timestamps(const TimestampSet *ss);`
- [x] `extern TimestampTz timestampset_start_timestamp(const TimestampSet *ss);`
- [x] `extern Interval *timestampset_timespan(const TimestampSet *ss);`
- [x] `extern bool timestampset_timestamp_n(const TimestampSet *ss, int n, TimestampTz *result);`
- [x] `extern TimestampTz *timestampset_timestamps(const TimestampSet *ss);`



### Transformation functions for span and time types

- [x] `extern PeriodSet *periodset_shift_tscale(const PeriodSet *ps, const Interval *start, const Interval *duration);`
- [x] `extern void span_expand(const Span *s1, Span *s2);`
- [x] `extern void period_shift_tscale(const Interval *start, const Interval *duration, Period *result);`
- [x] `extern TimestampSet *timestampset_shift_tscale(const TimestampSet *ss, const Interval *start, const Interval *duration);`

## Bounding box functions for span and time types
 

### Topological functions for span and time types

- [ ] `extern bool adjacent_floatspan_float(const Span *s, double d);` Class not defined in PyMEOS
- [ ] `extern bool adjacent_intspan_int(const Span *s, int i);` Class not defined in PyMEOS
- [x] `extern bool adjacent_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool adjacent_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern bool adjacent_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern bool adjacent_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool adjacent_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool adjacent_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern bool adjacent_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [x] `extern bool adjacent_span_span(const Span *s1, const Span *s2);`
- [x] `extern bool adjacent_timestamp_period(TimestampTz t, const Period *p);`
- [x] `extern bool adjacent_timestamp_periodset(TimestampTz t, const PeriodSet *ps);`
- [x] `extern bool adjacent_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern bool adjacent_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [ ] `extern bool contained_float_floatspan(double d, const Span *s);` Class not defined in PyMEOS
- [ ] `extern bool contained_int_intspan(int i, const Span *s);` Class not defined in PyMEOS
- [x] `extern bool contained_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool contained_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool contained_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool contained_span_span(const Span *s1, const Span *s2);`
- [x] `extern bool contained_timestamp_period(TimestampTz t, const Period *p);`
- [x] `extern bool contained_timestamp_periodset(TimestampTz t, const PeriodSet *ps);`
- [x] `extern bool contained_timestamp_timestampset(TimestampTz t, const TimestampSet *ts);`
- [x] `extern bool contained_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern bool contained_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern bool contained_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [ ] `extern bool contains_floatspan_float(const Span *s, double d);` Class not defined in PyMEOS
- [ ] `extern bool contains_intspan_int(const Span *s, int i);` Class not defined in PyMEOS
- [x] `extern bool contains_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool contains_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern bool contains_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern bool contains_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool contains_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool contains_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern bool contains_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [x] `extern bool contains_span_span(const Span *s1, const Span *s2);`
- [x] `extern bool contains_timestampset_timestamp(const TimestampSet *ts, TimestampTz t);`
- [x] `extern bool contains_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [x] `extern bool overlaps_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool overlaps_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern bool overlaps_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool overlaps_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool overlaps_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [x] `extern bool overlaps_span_span(const Span *s1, const Span *s2);`
- [x] `extern bool overlaps_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern bool overlaps_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern bool overlaps_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`


### Position functions for span and time types

- [x] `extern bool after_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool after_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern bool after_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern bool after_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool after_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool after_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern bool after_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [ ] `extern bool after_timestamp_period(TimestampTz t, const Period *p);` Class not defined in PyMEOS
- [ ] `extern bool after_timestamp_periodset(TimestampTz t, const PeriodSet *ps);` Class not defined in PyMEOS
- [ ] `extern bool after_timestamp_timestampset(TimestampTz t, const TimestampSet *ts);` Class not defined in PyMEOS
- [x] `extern bool after_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern bool after_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern bool after_timestampset_timestamp(const TimestampSet *ts, TimestampTz t);`
- [x] `extern bool after_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [x] `extern bool before_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool before_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern bool before_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern bool before_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool before_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool before_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern bool before_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [ ] `extern bool before_timestamp_period(TimestampTz t, const Period *p);` Class not defined in PyMEOS
- [ ] `extern bool before_timestamp_periodset(TimestampTz t, const PeriodSet *ps);` Class not defined in PyMEOS
- [ ] `extern bool before_timestamp_timestampset(TimestampTz t, const TimestampSet *ts);` Class not defined in PyMEOS
- [x] `extern bool before_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern bool before_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern bool before_timestampset_timestamp(const TimestampSet *ts, TimestampTz t);`
- [x] `extern bool before_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [ ] `extern bool left_float_floatspan(double d, const Span *s);` Class not defined in PyMEOS
- [ ] `extern bool left_floatspan_float(const Span *s, double d);` Class not defined in PyMEOS
- [ ] `extern bool left_int_intspan(int i, const Span *s);` Class not defined in PyMEOS
- [ ] `extern bool left_intspan_int(const Span *s, int i);` Class not defined in PyMEOS
- [x] `extern bool left_span_span(const Span *s1, const Span *s2);`
- [x] `extern bool overafter_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool overafter_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern bool overafter_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern bool overafter_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool overafter_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool overafter_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern bool overafter_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [ ] `extern bool overafter_timestamp_period(TimestampTz t, const Period *p);` Class not defined in PyMEOS
- [ ] `extern bool overafter_timestamp_periodset(TimestampTz t, const PeriodSet *ps);` Class not defined in PyMEOS
- [ ] `extern bool overafter_timestamp_timestampset(TimestampTz t, const TimestampSet *ts);` Class not defined in PyMEOS
- [x] `extern bool overafter_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern bool overafter_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern bool overafter_timestampset_timestamp(const TimestampSet *ts, TimestampTz t);`
- [x] `extern bool overafter_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [x] `extern bool overbefore_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool overbefore_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern bool overbefore_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern bool overbefore_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern bool overbefore_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool overbefore_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern bool overbefore_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [x] `extern bool overbefore_timestamp_period(TimestampTz t, const Period *p);`
- [ ] `extern bool overbefore_timestamp_periodset(TimestampTz t, const PeriodSet *ps);` Class not defined in PyMEOS
- [ ] `extern bool overbefore_timestamp_timestampset(TimestampTz t, const TimestampSet *ts);` Class not defined in PyMEOS
- [ ] `extern bool overbefore_timestampset_period(const TimestampSet *ts, const Period *p);` Class not defined in PyMEOS
- [x] `extern bool overbefore_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern bool overbefore_timestampset_timestamp(const TimestampSet *ts, TimestampTz t);`
- [x] `extern bool overbefore_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [ ] `extern bool overleft_float_floatspan(double d, const Span *s);` Class not defined in PyMEOS 
- [ ] `extern bool overleft_floatspan_float(const Span *s, double d);` Class not defined in PyMEOS 
- [ ] `extern bool overleft_int_intspan(int i, const Span *s);` Class not defined in PyMEOS 
- [ ] `extern bool overleft_intspan_int(const Span *s, int i);` Class not defined in PyMEOS 
- [x] `extern bool overleft_span_span(const Span *s1, const Span *s2);`
- [ ] `extern bool overright_float_floatspan(double d, const Span *s);` Class not defined in PyMEOS
- [ ] `extern bool overright_floatspan_float(const Span *s, double d);` Class not defined in PyMEOS
- [ ] `extern bool overright_int_intspan(int i, const Span *s);` Class not defined in PyMEOS
- [ ] `extern bool overright_intspan_int(const Span *s, int i);` Class not defined in PyMEOS
- [x] `extern bool overright_span_span(const Span *s1, const Span *s2);`
- [ ] `extern bool right_float_floatspan(double d, const Span *s);` Class not defined in PyMEOS
- [ ] `extern bool right_floatspan_float(const Span *s, double d);` Class not defined in PyMEOS
- [ ] `extern bool right_int_intspan(int i, const Span *s);` Class not defined in PyMEOS
- [ ] `extern bool right_intspan_int(const Span *s, int i);` Class not defined in PyMEOS
- [x] `extern bool right_span_span(const Span *s1, const Span *s2);`




### Set functions for span and time types

- [x] `extern PeriodSet *intersection_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern bool intersection_period_timestamp(const Period *p, TimestampTz t, TimestampTz *result);`
- [x] `extern TimestampSet *intersection_period_timestampset(const Period *ps, const TimestampSet *ts);`
- [x] `extern PeriodSet *intersection_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern PeriodSet *intersection_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool intersection_periodset_timestamp(const PeriodSet *ps, TimestampTz t, TimestampTz *result);`
- [x] `extern TimestampSet *intersection_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [x] `extern Span *intersection_span_span(const Span *s1, const Span *s2);`
- [ ] `extern bool intersection_timestamp_period(TimestampTz t, const Period *p, TimestampTz *result);` Class not defined in PyMEOS
- [ ] `extern bool intersection_timestamp_periodset(TimestampTz t, const PeriodSet *ps, TimestampTz *result);` Class not defined in PyMEOS
- [ ] `extern bool intersection_timestamp_timestamp(TimestampTz t1, TimestampTz t2, TimestampTz *result);` Class not defined in PyMEOS
- [ ] `extern bool intersection_timestamp_timestampset(TimestampTz t, const TimestampSet *ts, TimestampTz *result);` Class not defined in PyMEOS
- [x] `extern TimestampSet *intersection_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern TimestampSet *intersection_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern bool intersection_timestampset_timestamp(const TimestampSet *ts, const TimestampTz t, TimestampTz *result);`
- [x] `extern TimestampSet *intersection_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [x] `extern PeriodSet *minus_period_period(const Period *p1, const Period *p2);`
- [x] `extern PeriodSet *minus_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern PeriodSet *minus_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern PeriodSet *minus_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern PeriodSet *minus_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern PeriodSet *minus_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern PeriodSet *minus_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern PeriodSet *minus_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [ ] `extern Span *minus_span_span(const Span *s1, const Span *s2);` `minus_period_period` used instead 
- [ ] `extern bool minus_timestamp_period(TimestampTz t, const Period *p, TimestampTz *result);` Class not defined in PyMEOS
- [ ] `extern bool minus_timestamp_periodset(TimestampTz t, const PeriodSet *ps, TimestampTz *result);` Class not defined in PyMEOS
- [ ] `extern bool minus_timestamp_timestamp(TimestampTz t1, TimestampTz t2, TimestampTz *result);` Class not defined in PyMEOS
- [ ] `extern bool minus_timestamp_timestampset(TimestampTz t, const TimestampSet *ts, TimestampTz *result);` Class not defined in PyMEOS
- [x] `extern TimestampSet *minus_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern TimestampSet *minus_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern TimestampSet *minus_timestampset_timestamp(const TimestampSet *ts, TimestampTz t);`
- [x] `extern TimestampSet *minus_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`
- [x] `extern PeriodSet *union_period_period(const Period *p1, const Period *p2);`
- [x] `extern PeriodSet *union_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern PeriodSet *union_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern PeriodSet *union_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern PeriodSet *union_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern PeriodSet *union_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern PeriodSet *union_periodset_timestamp(PeriodSet *ps, TimestampTz t);`
- [x] `extern PeriodSet *union_periodset_timestampset(PeriodSet *ps, TimestampSet *ts);`
- [ ] `extern Span *union_span_span(const Span *s1, const Span *s2, bool strict);` `union_period_period` used instead 
- [ ] `extern PeriodSet *union_timestamp_period(TimestampTz t, const Period *p);` Class not defined in PyMEOS
- [ ] `extern PeriodSet *union_timestamp_periodset(TimestampTz t, const PeriodSet *ps);` Class not defined in PyMEOS
- [ ] `extern TimestampSet *union_timestamp_timestamp(TimestampTz t1, TimestampTz t2);` Class not defined in PyMEOS
- [ ] `extern TimestampSet *union_timestamp_timestampset(TimestampTz t, const TimestampSet *ts);` Class not defined in PyMEOS
- [x] `extern PeriodSet *union_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern PeriodSet *union_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern TimestampSet *union_timestampset_timestamp(const TimestampSet *ts, const TimestampTz t);`
- [x] `extern TimestampSet *union_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`



### Distance functions for span and time types

- [ ] `extern double distance_floatspan_float(const Span *s, double d);` Class not defined in PyMEOS
- [ ] `extern double distance_intspan_int(const Span *s, int i);` Class not defined in PyMEOS
- [x] `extern double distance_period_periodset(const Period *p, const PeriodSet *ps);`
- [x] `extern double distance_period_timestamp(const Period *p, TimestampTz t);`
- [x] `extern double distance_period_timestampset(const Period *p, const TimestampSet *ts);`
- [x] `extern double distance_periodset_period(const PeriodSet *ps, const Period *p);`
- [x] `extern double distance_periodset_periodset(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern double distance_periodset_timestamp(const PeriodSet *ps, TimestampTz t);`
- [x] `extern double distance_periodset_timestampset(const PeriodSet *ps, const TimestampSet *ts);`
- [x] `extern double distance_span_span(const Span *s1, const Span *s2);`
- [ ] `extern double distance_timestamp_period(TimestampTz t, const Period *p);` Class not defined in PyMEOS
- [ ] `extern double distance_timestamp_periodset(TimestampTz t, const PeriodSet *ps);` Class not defined in PyMEOS
- [ ] `extern double distance_timestamp_timestamp(TimestampTz t1, TimestampTz t2);` Class not defined in PyMEOS
- [ ] `extern double distance_timestamp_timestampset(TimestampTz t, const TimestampSet *ts);` Class not defined in PyMEOS
- [x] `extern double distance_timestampset_period(const TimestampSet *ts, const Period *p);`
- [x] `extern double distance_timestampset_periodset(const TimestampSet *ts, const PeriodSet *ps);`
- [x] `extern double distance_timestampset_timestamp(const TimestampSet *ts, TimestampTz t);`
- [x] `extern double distance_timestampset_timestampset(const TimestampSet *ts1, const TimestampSet *ts2);`



### Comparison functions for span and time types

- [x] `extern bool periodset_eq(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool periodset_ne(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern int periodset_cmp(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool periodset_lt(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool periodset_le(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool periodset_ge(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool periodset_gt(const PeriodSet *ps1, const PeriodSet *ps2);`
- [x] `extern bool span_eq(const Span *s1, const Span *s2);`
- [x] `extern bool span_ne(const Span *s1, const Span *s2);`
- [x] `extern int span_cmp(const Span *s1, const Span *s2);`
- [x] `extern bool span_lt(const Span *s1, const Span *s2);`
- [x] `extern bool span_le(const Span *s1, const Span *s2);`
- [x] `extern bool span_ge(const Span *s1, const Span *s2);`
- [x] `extern bool span_gt(const Span *s1, const Span *s2);`
- [x] `extern bool timestampset_eq(const TimestampSet *ss1, const TimestampSet *ss2);`
- [x] `extern bool timestampset_ne(const TimestampSet *ss1, const TimestampSet *ss2);`
- [x] `extern int timestampset_cmp(const TimestampSet *ss1, const TimestampSet *ss2);`
- [x] `extern bool timestampset_lt(const TimestampSet *ss1, const TimestampSet *ss2);`
- [x] `extern bool timestampset_le(const TimestampSet *ss1, const TimestampSet *ss2);`
- [x] `extern bool timestampset_ge(const TimestampSet *ss1, const TimestampSet *ss2);`
- [x] `extern bool timestampset_gt(const TimestampSet *ss1, const TimestampSet *ss2);`

## Functions for box types
 

### Input/output functions for box types

- [x] `extern TBOX *tbox_in(const char *str);`
- [x] `extern char *tbox_out(const TBOX *box, int maxdd);`
- [ ] `extern TBOX *tbox_from_wkb(const uint8_t *wkb, int size);` WKB is not being implemented directly (only HexWKB)
- [x] `extern TBOX *tbox_from_hexwkb(const char *hexwkb);`
- [ ] `extern STBOX *stbox_from_wkb(const uint8_t *wkb, int size);` WKB is not being implemented directly (only HexWKB)
- [x] `extern STBOX *stbox_from_hexwkb(const char *hexwkb);`
- [ ] `extern uint8_t *tbox_as_wkb(const TBOX *box, uint8_t variant, size_t *size_out);` WKB is not being implemented directly (only HexWKB)
- [x] `extern char *tbox_as_hexwkb(const TBOX *box, uint8_t variant, size_t *size);`
- [ ] `extern uint8_t *stbox_as_wkb(const STBOX *box, uint8_t variant, size_t *size_out);` WKB is not being implemented directly (only HexWKB)
- [x] `extern char *stbox_as_hexwkb(const STBOX *box, uint8_t variant, size_t *size);`
- [x] `extern STBOX *stbox_in(const char *str);`
- [x] `extern char *stbox_out(const STBOX *box, int maxdd);`



### Constructor functions for box types

- [x] `extern TBOX *tbox_make(const Period *p, const Span *s);`
- [ ] `extern void tbox_set(const Period *p, const Span *s, TBOX *box);` Not necessary in PyMEOS
- [x] `extern TBOX *tbox_copy(const TBOX *box);`
- [x] `extern STBOX * stbox_make(const Period *p, bool hasx, bool hasz, bool geodetic, int32 srid,
  double xmin, double xmax, double ymin, double ymax, double zmin, double zmax);`
- [ ] `extern void stbox_set(const Period *p, bool hasx, bool hasz, bool geodetic, int32 srid, double xmin, double xmax,
  double ymin, double ymax, double zmin, double zmax, STBOX *box);` Not necessary in PyMEOS
- [x] `extern STBOX *stbox_copy(const STBOX *box);`



### Cast functions for box types

- [x] `extern TBOX *int_to_tbox(int i);`
- [x] `extern TBOX *float_to_tbox(double d);`
- [x] `extern TBOX *span_to_tbox(const Span *span);`
- [x] `extern TBOX *timestamp_to_tbox(TimestampTz t);`
- [x] `extern TBOX *timestampset_to_tbox(const TimestampSet *ss);`
- [x] `extern TBOX *period_to_tbox(const Period *p);`
- [x] `extern TBOX *periodset_to_tbox(const PeriodSet *ps);`
- [x] `extern TBOX *int_timestamp_to_tbox(int i, TimestampTz t);`
- [x] `extern TBOX *float_timestamp_to_tbox(double d, TimestampTz t);`
- [x] `extern TBOX *int_period_to_tbox(int i, const Period *p);`
- [x] `extern TBOX *float_period_to_tbox(double d, const Period *p);`
- [x] `extern TBOX *span_timestamp_to_tbox(const Span *span, TimestampTz t);`
- [x] `extern TBOX *span_period_to_tbox(const Span *span, const Period *p);`
- [x] `extern Span *tbox_to_floatspan(const TBOX *box);`
- [x] `extern Period *tbox_to_period(const TBOX *box);`
- [x] `extern Period *stbox_to_period(const STBOX *box);`
- [x] `extern TBOX *tnumber_to_tbox(const Temporal *temp);`
- [x] `extern GSERIALIZED *stbox_to_geo(const STBOX *box);`
- [x] `extern STBOX *tpoint_to_stbox(const Temporal *temp);`
- [x] `extern STBOX *geo_to_stbox(const GSERIALIZED *gs);`
- [x] `extern STBOX *timestamp_to_stbox(TimestampTz t);`
- [x] `extern STBOX *timestampset_to_stbox(const TimestampSet *ts);`
- [x] `extern STBOX *period_to_stbox(const Period *p);`
- [x] `extern STBOX *periodset_to_stbox(const PeriodSet *ps);`
- [x] `extern STBOX *geo_timestamp_to_stbox(const GSERIALIZED *gs, TimestampTz t);`
- [x] `extern STBOX *geo_period_to_stbox(const GSERIALIZED *gs, const Period *p);`



### Accessor functions for box types

- [x] `extern bool tbox_hasx(const TBOX *box);`
- [x] `extern bool tbox_hast(const TBOX *box);`
- [x] `extern bool tbox_xmin(const TBOX *box, double *result);`
- [x] `extern bool tbox_xmax(const TBOX *box, double *result);`
- [x] `extern bool tbox_tmin(const TBOX *box, TimestampTz *result);`
- [x] `extern bool tbox_tmax(const TBOX *box, TimestampTz *result);`
- [x] `extern bool stbox_hasx(const STBOX *box);`
- [x] `extern bool stbox_hasz(const STBOX *box);`
- [x] `extern bool stbox_hast(const STBOX *box);`
- [x] `extern bool stbox_isgeodetic(const STBOX *box);`
- [x] `extern bool stbox_xmin(const STBOX *box, double *result);`
- [x] `extern bool stbox_xmax(const STBOX *box, double *result);`
- [x] `extern bool stbox_ymin(const STBOX *box, double *result);`
- [x] `extern bool stbox_ymax(const STBOX *box, double *result);`
- [x] `extern bool stbox_zmin(const STBOX *box, double *result);`
- [x] `extern bool stbox_zmax(const STBOX *box, double *result);`
- [x] `extern bool stbox_tmin(const STBOX *box, TimestampTz *result);`
- [x] `extern bool stbox_tmax(const STBOX *box, TimestampTz *result);`
- [ ] `extern int32 stbox_srid(const STBOX *box);` Access information directly 



### Transformation functions for box types

- [x] `extern void tbox_expand(const TBOX *box1, TBOX *box2);`
- [x] `extern void tbox_shift_tscale(const Interval *start, const Interval *duration, TBOX *box);`
- [x] `extern TBOX *tbox_expand_value(const TBOX *box, const double d);`
- [x] `extern TBOX *tbox_expand_temporal(const TBOX *box, const Interval *interval);`
- [x] `extern void stbox_expand(const STBOX *box1, STBOX *box2);`
- [x] `extern void stbox_shift_tscale(const Interval *start, const Interval *duration, STBOX *box);`
- [x] `extern STBOX *stbox_set_srid(const STBOX *box, int32 srid);`
- [x] `extern STBOX *stbox_expand_spatial(const STBOX *box, double d);`
- [x] `extern STBOX *stbox_expand_temporal(const STBOX *box, const Interval *interval);`



### Topological functions for box types

- [x] `extern bool contains_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool contained_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool overlaps_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool same_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool adjacent_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool contains_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool contained_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overlaps_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool same_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool adjacent_stbox_stbox(const STBOX *box1, const STBOX *box2);`



### Position functions for box types

- [x] `extern bool left_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool overleft_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool right_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool overright_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool before_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool overbefore_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool after_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool overafter_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool left_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overleft_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool right_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overright_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool below_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overbelow_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool above_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overabove_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool front_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overfront_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool back_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overback_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool before_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overbefore_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool after_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool overafter_stbox_stbox(const STBOX *box1, const STBOX *box2);`



### Set functions for box types

- [x] `extern TBOX *union_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [ ] `extern bool inter_tbox_tbox(const TBOX *box1, const TBOX *box2, TBOX *result);` `intersection_tbox_tbox` used instead 
- [x] `extern TBOX *intersection_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern STBOX *union_stbox_stbox(const STBOX *box1, const STBOX *box2, bool strict);`
- [ ] `extern bool inter_stbox_stbox(const STBOX *box1, const STBOX *box2, STBOX *result);` `intersection_stbox_stbox` used instead 
- [x] `extern STBOX *intersection_stbox_stbox(const STBOX *box1, const STBOX *box2);`



### Comparison functions for box types

- [x] `extern bool tbox_eq(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool tbox_ne(const TBOX *box1, const TBOX *box2);`
- [x] `extern int tbox_cmp(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool tbox_lt(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool tbox_le(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool tbox_ge(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool tbox_gt(const TBOX *box1, const TBOX *box2);`
- [x] `extern bool stbox_eq(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool stbox_ne(const STBOX *box1, const STBOX *box2);`
- [x] `extern int stbox_cmp(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool stbox_lt(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool stbox_le(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool stbox_ge(const STBOX *box1, const STBOX *box2);`
- [x] `extern bool stbox_gt(const STBOX *box1, const STBOX *box2);`

## Functions for temporal types
 

### Input/output functions for temporal types

- [x] `extern Temporal *tbool_in(const char *str);`
- [x] `extern char *tbool_out(const Temporal *temp);`
- [x] `extern char *temporal_as_hexwkb(const Temporal *temp, uint8_t variant, size_t *size_out);`
- [x] `extern char *temporal_as_mfjson(const Temporal *temp, bool with_bbox, int flags, int precision, char *srs);`
- [ ] `extern uint8_t *temporal_as_wkb(const Temporal *temp, uint8_t variant, size_t *size_out);` WKB is not being implemented directly (only HexWKB)
- [x] `extern Temporal *temporal_from_hexwkb(const char *hexwkb);`
- [x] `extern Temporal *temporal_from_mfjson(const char *mfjson);`
- [ ] `extern Temporal *temporal_from_wkb(const uint8_t *wkb, int size);` WKB is not being implemented directly (only HexWKB)
- [x] `extern Temporal *tfloat_in(const char *str);`
- [x] `extern char *tfloat_out(const Temporal *temp, int maxdd);`
- [x] `extern Temporal *tgeogpoint_in(const char *str);`
- [x] `extern Temporal *tgeompoint_in(const char *str);`
- [x] `extern Temporal *tint_in(const char *str);`
- [x] `extern char *tint_out(const Temporal *temp);`
- [x] `extern char *tpoint_as_ewkt(const Temporal *temp, int maxdd);`
- [ ] `extern char *tpoint_as_text(const Temporal *temp, int maxdd);` `tpoint_out` used instead
- [x] `extern char *tpoint_out(const Temporal *temp, int maxdd);`
- [x] `extern Temporal *ttext_in(const char *str);`
- [x] `extern char *ttext_out(const Temporal *temp);`



### Constructor functions for temporal types

- [x] `extern Temporal *tbool_from_base(bool b, const Temporal *temp);`
- [x] `extern TInstant *tboolinst_make(bool b, TimestampTz t);`
- [ ] `extern TSequence *tbooldiscseq_from_base(bool b, const TSequence *is);` Not implemented in MEOS
- [x] `extern TSequence *tbooldiscseq_from_base_time(bool b, const TimestampSet *ts);`
- [ ] `extern TSequence *tboolseq_from_base(bool b, const TSequence *seq);` `tbool_from_base` used instead
- [x] `extern TSequence *tboolseq_from_base_time(bool b, const Period *p);`
- [ ] `extern TSequenceSet *tboolseqset_from_base(bool b, const TSequenceSet *ss);` `tbool_from_base` used instead
- [x] `extern TSequenceSet *tboolseqset_from_base_time(bool b, const PeriodSet *ps);`
- [x] `extern Temporal *temporal_copy(const Temporal *temp);`
- [x] `extern Temporal *tfloat_from_base(double d, const Temporal *temp, interpType interp);`
- [x] `extern TInstant *tfloatinst_make(double d, TimestampTz t);`
- [x] `extern TSequence *tfloatdiscseq_from_base_time(double d, const TimestampSet *ts);`
- [ ] `extern TSequence *tfloatseq_from_base(double d, const TSequence *seq, interpType interp);` `tfloat_from_base` used instead
- [x] `extern TSequence *tfloatseq_from_base_time(double d, const Period *p, interpType interp);`
- [ ] `extern TSequenceSet *tfloatseqset_from_base(double d, const TSequenceSet *ss, interpType interp);` `tfloat_from_base` used instead
- [x] `extern TSequenceSet *tfloatseqset_from_base_time(double d, const PeriodSet *ps, interpType interp);`
- [x] `extern Temporal *tgeogpoint_from_base(const GSERIALIZED *gs, const Temporal *temp, interpType interp);`
- [x] `extern TInstant *tgeogpointinst_make(const GSERIALIZED *gs, TimestampTz t);`
- [x] `extern TSequence *tgeogpointdiscseq_from_base_time(const GSERIALIZED *gs, const TimestampSet *ts);`
- [ ] `extern TSequence *tgeogpointseq_from_base(const GSERIALIZED *gs, const TSequence *seq, interpType interp);` `tgeogpoint_from_base` used instead
- [x] `extern TSequence *tgeogpointseq_from_base_time(const GSERIALIZED *gs, const Period *p, interpType interp);`
- [ ] `extern TSequenceSet *tgeogpointseqset_from_base(const GSERIALIZED *gs, const TSequenceSet *ss, interpType interp);` `tgeogpoint_from_base` used instead
- [x] `extern TSequenceSet *tgeogpointseqset_from_base_time(const GSERIALIZED *gs, const PeriodSet *ps, interpType interp);`
- [x] `extern Temporal *tgeompoint_from_base(const GSERIALIZED *gs, const Temporal *temp, interpType interp);`
- [x] `extern TInstant *tgeompointinst_make(const GSERIALIZED *gs, TimestampTz t);`
- [x] `extern TSequence *tgeompointdiscseq_from_base_time(const GSERIALIZED *gs, const TimestampSet *ts);`
- [ ] `extern TSequence *tgeompointseq_from_base(const GSERIALIZED *gs, const TSequence *seq, interpType interp);` `tgeompoint_from_base` used instead
- [x] `extern TSequence *tgeompointseq_from_base_time(const GSERIALIZED *gs, const Period *p, interpType interp);`
- [ ] `extern TSequenceSet *tgeompointseqset_from_base(const GSERIALIZED *gs, const TSequenceSet *ss, interpType interp);` `tgeompoint_from_base` used instead
- [x] `extern TSequenceSet *tgeompointseqset_from_base_time(const GSERIALIZED *gs, const PeriodSet *ps, interpType interp);`
- [x] `extern Temporal *tint_from_base(int i, const Temporal *temp);`
- [x] `extern TInstant *tintinst_make(int i, TimestampTz t);`
- [x] `extern TSequence *tintdiscseq_from_base_time(int i, const TimestampSet *ts);`
- [ ] `extern TSequence *tintseq_from_base(int i, const TSequence *seq);` `tint_from_base` used instead
- [x] `extern TSequence *tintseq_from_base_time(int i, const Period *p);`
- [ ] `extern TSequenceSet *tintseqset_from_base(int i, const TSequenceSet *ss);` `tint_from_base` used instead
- [x] `extern TSequenceSet *tintseqset_from_base_time(int i, const PeriodSet *ps);`
- [x] `extern TSequence *tsequence_make(const TInstant **instants, int count,  int maxcount, bool lower_inc, bool upper_inc, interpType interp, bool normalize);`
- [x] `extern TSequence *tpointseq_make_coords(const double *xcoords, const double *ycoords, const double *zcoords,
  const TimestampTz *times, int count, int32 srid, bool geodetic, bool lower_inc, bool upper_inc, interpType interp, bool normalize);`
- [ ] `extern TSequence *tsequence_make_free(TInstant **instants, int count, int maxcount, bool lower_inc, bool upper_inc, interpType interp, bool normalize);` Not necessary in PyMEOS
- [x] `extern TSequenceSet *tsequenceset_make(const TSequence **sequences, int count, bool normalize);`
- [ ] `extern TSequenceSet *tsequenceset_make_free(TSequence **sequences, int count, bool normalize);` Not necessary in PyMEOS
- [ ] `extern TSequenceSet *tsequenceset_make_gaps(const TInstant **instants, int count, interpType interp, float maxdist, Interval *maxt);`
- [x] `extern Temporal *ttext_from_base(const text *txt, const Temporal *temp);`
- [x] `extern TInstant *ttextinst_make(const text *txt, TimestampTz t);`
- [x] `extern TSequence *ttextdiscseq_from_base_time(const text *txt, const TimestampSet *ts);`
- [ ] `extern TSequence *ttextseq_from_base(const text *txt, const TSequence *seq);` `ttext_from_base` used instead
- [x] `extern TSequence *ttextseq_from_base_time(const text *txt, const Period *p);`
- [ ] `extern TSequenceSet *ttextseqset_from_base(const text *txt, const TSequenceSet *ss);` `ttext_from_base` used instead
- [x] `extern TSequenceSet *ttextseqset_from_base_time(const text *txt, const PeriodSet *ps);`



### Cast functions for temporal types

- [x] `extern Temporal *tfloat_to_tint(const Temporal *temp);`
- [x] `extern Temporal *tint_to_tfloat(const Temporal *temp);`
- [x] `extern Span *tnumber_to_span(const Temporal *temp);`



### Accessor functions for temporal types

- [x] `extern bool tbool_end_value(const Temporal *temp);`
- [x] `extern bool tbool_start_value(const Temporal *temp);`
- [x] `extern bool *tbool_values(const Temporal *temp, int *count);`
- [x] `extern Interval *temporal_duration(const Temporal *temp);`
- [x] `extern const TInstant *temporal_end_instant(const Temporal *temp);`
- [x] `extern TSequence *temporal_end_sequence(const Temporal *temp);`
- [x] `extern TimestampTz temporal_end_timestamp(const Temporal *temp);`
- [x] `extern uint32 temporal_hash(const Temporal *temp);`
- [x] `extern const TInstant *temporal_instant_n(const Temporal *temp, int n);`
- [x] `extern const TInstant **temporal_instants(const Temporal *temp, int *count);`
- [x] `extern char *temporal_interpolation(const Temporal *temp);`
- [x] `extern const TInstant *temporal_max_instant(const Temporal *temp);`
- [x] `extern const TInstant *temporal_min_instant(const Temporal *temp);`
- [x] `extern int temporal_num_instants(const Temporal *temp);`
- [x] `extern int temporal_num_sequences(const Temporal *temp);`
- [x] `extern int temporal_num_timestamps(const Temporal *temp);`
- [x] `extern TSequence **temporal_segments(const Temporal *temp, int *count);`
- [x] `extern TSequence *temporal_sequence_n(const Temporal *temp, int i);`
- [x] `extern TSequence **temporal_sequences(const Temporal *temp, int *count);`
- [x] `extern const TInstant *temporal_start_instant(const Temporal *temp);`
- [x] `extern TSequence *temporal_start_sequence(const Temporal *temp);`
- [x] `extern TimestampTz temporal_start_timestamp(const Temporal *temp);`
- [ ] `extern char *temporal_subtype(const Temporal *temp);` Not necessary in PyMEOS
- [x] `extern PeriodSet *temporal_time(const Temporal *temp);`
- [x] `extern Interval *temporal_timespan(const Temporal *temp);`
- [x] `extern bool temporal_timestamp_n(const Temporal *temp, int n, TimestampTz *result);`
- [x] `extern TimestampTz *temporal_timestamps(const Temporal *temp, int *count);`
- [x] `extern double tfloat_end_value(const Temporal *temp);`
- [x] `extern double tfloat_max_value(const Temporal *temp);`
- [x] `extern double tfloat_min_value(const Temporal *temp);`
- [x] `extern Span **tfloat_spans(const Temporal *temp, int *count);`
- [x] `extern double tfloat_start_value(const Temporal *temp);`
- [x] `extern double *tfloat_values(const Temporal *temp, int *count);`
- [x] `extern int tint_end_value(const Temporal *temp);`
- [x] `extern int tint_max_value(const Temporal *temp);`
- [x] `extern int tint_min_value(const Temporal *temp);`
- [x] `extern int tint_start_value(const Temporal *temp);`
- [x] `extern int *tint_values(const Temporal *temp, int *count);`
- [x] `extern GSERIALIZED *tpoint_end_value(const Temporal *temp);`
- [x] `extern GSERIALIZED *tpoint_start_value(const Temporal *temp);`
- [x] `extern GSERIALIZED **tpoint_values(const Temporal *temp, int *count);`
- [x] `extern text *ttext_end_value(const Temporal *temp);`
- [x] `extern text *ttext_max_value(const Temporal *temp);`
- [x] `extern text *ttext_min_value(const Temporal *temp);`
- [x] `extern text *ttext_start_value(const Temporal *temp);`
- [x] `extern text **ttext_values(const Temporal *temp, int *count);`



### Transformation functions for temporal types

- [x] `extern TSequence *tsequence_compact(const TSequence *seq);`
- [x] `extern Temporal *temporal_append_tinstant(Temporal *temp, const TInstant *inst, bool expand);`
- [x] `extern Temporal *temporal_merge(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern Temporal *temporal_merge_array(Temporal **temparr, int count);`
- [x] `extern Temporal *temporal_shift_tscale(const Temporal *temp, const Interval *shift, const Interval *duration);`
- [x] `extern Temporal *temporal_step_to_linear(const Temporal *temp);`
- [x] `extern Temporal *temporal_to_tinstant(const Temporal *temp);`
- [x] `extern Temporal *temporal_to_tdiscseq(const Temporal *temp);`
- [x] `extern Temporal *temporal_to_tsequence(const Temporal *temp);`
- [x] `extern Temporal *temporal_to_tsequenceset(const Temporal *temp);`



### Restriction functions for temporal types

- [x] `extern Temporal *tbool_at_value(const Temporal *temp, bool b);`
- [ ] `extern Temporal *tbool_at_values(const Temporal *temp, bool *values, int count);` Is it useful?
- [x] `extern Temporal *tbool_minus_value(const Temporal *temp, bool b);`
- [ ] `extern Temporal *tbool_minus_values(const Temporal *temp, bool *values, int count);` Is it useful?
- [x] `extern bool tbool_value_at_timestamp(const Temporal *temp, TimestampTz t, bool strict, bool *value);`
- [x] `extern Temporal *temporal_at_max(const Temporal *temp);`
- [x] `extern Temporal *temporal_at_min(const Temporal *temp);`
- [x] `extern Temporal *temporal_at_period(const Temporal *temp, const Period *p);`
- [x] `extern Temporal *temporal_at_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern Temporal *temporal_at_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern Temporal *temporal_at_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [x] `extern Temporal *temporal_minus_max(const Temporal *temp);`
- [x] `extern Temporal *temporal_minus_min(const Temporal *temp);`
- [x] `extern Temporal *temporal_minus_period(const Temporal *temp, const Period *p);`
- [x] `extern Temporal *temporal_minus_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern Temporal *temporal_minus_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern Temporal *temporal_minus_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [x] `extern Temporal *tfloat_at_value(const Temporal *temp, double d);`
- [x] `extern Temporal *tfloat_at_values(const Temporal *temp, double *values, int count);`
- [x] `extern Temporal *tfloat_minus_value(const Temporal *temp, double d);`
- [x] `extern Temporal *tfloat_minus_values(const Temporal *temp, double *values, int count);`
- [x] `extern bool tfloat_value_at_timestamp(const Temporal *temp, TimestampTz t, bool strict, double *value);`
- [x] `extern Temporal *tint_at_value(const Temporal *temp, int i);`
- [x] `extern Temporal *tint_at_values(const Temporal *temp, int *values, int count);`
- [x] `extern Temporal *tint_minus_value(const Temporal *temp, int i);`
- [x] `extern Temporal *tint_minus_values(const Temporal *temp, int *values, int count);`
- [x] `extern bool tint_value_at_timestamp(const Temporal *temp, TimestampTz t, bool strict, int *value);`
- [x] `extern Temporal *tnumber_at_span(const Temporal *temp, const Span *span);`
- [x] `extern Temporal *tnumber_at_spans(const Temporal *temp, Span **spans, int count);`
- [x] `extern Temporal *tnumber_at_tbox(const Temporal *temp, const TBOX *box);`
- [x] `extern Temporal *tnumber_minus_span(const Temporal *temp, const Span *span);`
- [x] `extern Temporal *tnumber_minus_spans(const Temporal *temp, Span **spans, int count);`
- [x] `extern Temporal *tnumber_minus_tbox(const Temporal *temp, const TBOX *box);`
- [x] `extern Temporal *tpoint_at_geometry(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern Temporal *tpoint_at_stbox(const Temporal *temp, const STBOX *box);`
- [ ] `extern Temporal *tpoint_at_value(const Temporal *temp, GSERIALIZED *gs);` `tpoint_at_geometry` used instead
- [x] `extern Temporal *tpoint_at_values(const Temporal *temp, GSERIALIZED **values, int count);`
- [x] `extern Temporal *tpoint_minus_geometry(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern Temporal *tpoint_minus_stbox(const Temporal *temp, const STBOX *box);`
- [ ] `extern Temporal *tpoint_minus_value(const Temporal *temp, GSERIALIZED *gs);` `tpoint_minus_geometry` used instead
- [x] `extern Temporal *tpoint_minus_values(const Temporal *temp, GSERIALIZED **values, int count);`
- [x] `extern bool tpoint_value_at_timestamp(const Temporal *temp, TimestampTz t, bool strict, GSERIALIZED **value);`
- [x] `extern Temporal *ttext_at_value(const Temporal *temp, text *txt);`
- [x] `extern Temporal *ttext_at_values(const Temporal *temp, text **values, int count);`
- [x] `extern Temporal *ttext_minus_value(const Temporal *temp, text *txt);`
- [x] `extern Temporal *ttext_minus_values(const Temporal *temp, text **values, int count);`
- [x] `extern bool ttext_value_at_timestamp(const Temporal *temp, TimestampTz t, bool strict, text **value);`



### Boolean functions for temporal types

- [ ] `extern Temporal *tand_bool_tbool(bool b, const Temporal *temp);` `tand_tbool_bool` used instead
- [x] `extern Temporal *tand_tbool_bool(const Temporal *temp, bool b);`
- [x] `extern Temporal *tand_tbool_tbool(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern Temporal *tnot_tbool(const Temporal *temp);`
- [ ] `extern Temporal *tor_bool_tbool(bool b, const Temporal *temp);` `tor_tbool_bool` used instead
- [x] `extern Temporal *tor_tbool_bool(const Temporal *temp, bool b);`
- [x] `extern Temporal *tor_tbool_tbool(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern PeriodSet *tbool_when_true(const Temporal *temp);`



### Mathematical functions for temporal types

- [x] `extern Temporal *add_float_tfloat(double d, const Temporal *tnumber);`
- [x] `extern Temporal *add_int_tint(int i, const Temporal *tnumber);`
- [x] `extern Temporal *add_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern Temporal *add_tint_int(const Temporal *tnumber, int i);`
- [x] `extern Temporal *add_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern Temporal *div_float_tfloat(double d, const Temporal *tnumber);`
- [x] `extern Temporal *div_int_tint(int i, const Temporal *tnumber);`
- [x] `extern Temporal *div_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern Temporal *div_tint_int(const Temporal *tnumber, int i);`
- [x] `extern Temporal *div_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern Temporal *mult_float_tfloat(double d, const Temporal *tnumber);`
- [x] `extern Temporal *mult_int_tint(int i, const Temporal *tnumber);`
- [x] `extern Temporal *mult_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern Temporal *mult_tint_int(const Temporal *tnumber, int i);`
- [x] `extern Temporal *mult_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern Temporal *sub_float_tfloat(double d, const Temporal *tnumber);`
- [x] `extern Temporal *sub_int_tint(int i, const Temporal *tnumber);`
- [x] `extern Temporal *sub_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern Temporal *sub_tint_int(const Temporal *tnumber, int i);`
- [x] `extern Temporal *sub_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern Temporal *tfloat_degrees(const Temporal *temp);`
- [x] `extern Temporal *tfloat_radians(const Temporal *temp);`
- [x] `extern Temporal *tfloat_derivative(const Temporal *temp);`




### Text functions for temporal types

- [x] `extern Temporal *textcat_text_ttext(const text *txt, const Temporal *temp);`
- [x] `extern Temporal *textcat_ttext_text(const Temporal *temp, const text *txt);`
- [x] `extern Temporal *textcat_ttext_ttext(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern Temporal *ttext_upper(const Temporal *temp);`
- [x] `extern Temporal *ttext_lower(const Temporal *temp);`

## Bounding box functions for temporal types
 

### Topological functions for temporal types

- [ ] `extern bool adjacent_float_tfloat(double d, const Temporal *tnumber);` `adjacent_tfloat_float` used instead
- [ ] `extern bool adjacent_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `adjacent_tpoint_geo` used instead
- [ ] `extern bool adjacent_int_tint(int i, const Temporal *tnumber);` `adjacent_tint_int` used instead
- [x] `extern bool adjacent_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool adjacent_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [ ] `extern bool adjacent_span_tnumber(const Span *span, const Temporal *tnumber);` `adjacent_tnumber_span` used instead
- [x] `extern bool adjacent_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool adjacent_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool adjacent_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool adjacent_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool adjacent_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool adjacent_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool adjacent_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [x] `extern bool adjacent_tfloat_float(const Temporal *tnumber, double d);`
- [ ] `extern bool adjacent_timestamp_temporal(TimestampTz t, const Temporal *temp);`
- [x] `extern bool adjacent_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool adjacent_tint_int(const Temporal *tnumber, int i);`
- [x] `extern bool adjacent_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool adjacent_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool adjacent_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool adjacent_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool adjacent_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool adjacent_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool contained_float_tfloat(double d, const Temporal *tnumber);` `contains_tfloat_float` used instead 
- [ ] `extern bool contained_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `contains_tpoint_geo` used instead 
- [ ] `extern bool contained_int_tint(int i, const Temporal *tnumber);` `contains_tint_int` used instead 
- [x] `extern bool contained_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool contained_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [ ] `extern bool contained_span_tnumber(const Span *span, const Temporal *tnumber);` `contains_tnumber_span` used instead 
- [x] `extern bool contained_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool contained_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool contained_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool contained_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool contained_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool contained_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool contained_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [x] `extern bool contained_tfloat_float(const Temporal *tnumber, double d);`
- [ ] `extern bool contained_timestamp_temporal(TimestampTz t, const Temporal *temp);`
- [x] `extern bool contained_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool contained_tint_int(const Temporal *tnumber, int i);`
- [x] `extern bool contained_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool contained_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool contained_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool contained_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool contained_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool contained_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool contains_bbox_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `contained_tpoint_geo` used omstead
- [ ] `extern bool contains_float_tfloat(double d, const Temporal *tnumber);` `contained_tfloat_float` used instead
- [ ] `extern bool contains_int_tint(int i, const Temporal *tnumber);` `contained_tint_int` used instead
- [x] `extern bool contains_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool contains_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [ ] `extern bool contains_span_tnumber(const Span *span, const Temporal *tnumber);` `contained_tnumber_span` used instead
- [x] `extern bool contains_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool contains_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool contains_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool contains_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool contains_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool contains_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool contains_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [x] `extern bool contains_tfloat_float(const Temporal *tnumber, double d);`
- [ ] `extern bool contains_timestamp_temporal(TimestampTz t, const Temporal *temp);`
- [x] `extern bool contains_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool contains_tint_int(const Temporal *tnumber, int i);`
- [x] `extern bool contains_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool contains_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool contains_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool contains_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool contains_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool contains_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool left_float_tfloat(double d, const Temporal *tnumber);` `overright_tfloat_float` used instead
- [ ] `extern bool left_int_tint(int i, const Temporal *tnumber);` `overright_tint_int` used instead
- [x] `extern bool left_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern bool left_tint_int(const Temporal *tnumber, int i);`
- [ ] `extern bool overlaps_float_tfloat(double d, const Temporal *tnumber);` `overlaps_tfloat_float` used instead
- [ ] `extern bool overlaps_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `overlaps_tpoint_geo` used instead
- [ ] `extern bool overlaps_int_tint(int i, const Temporal *tnumber);` `overlaps_tint_int` used instead
- [x] `extern bool overlaps_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool overlaps_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [ ] `extern bool overlaps_span_tnumber(const Span *span, const Temporal *tnumber);` `overlaps_tnumber_span` used instead
- [x] `extern bool overlaps_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overlaps_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool overlaps_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool overlaps_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool overlaps_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool overlaps_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool overlaps_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [x] `extern bool overlaps_tfloat_float(const Temporal *tnumber, double d);`
- [ ] `extern bool overlaps_timestamp_temporal(TimestampTz t, const Temporal *temp);`
- [x] `extern bool overlaps_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool overlaps_tint_int(const Temporal *tnumber, int i);`
- [x] `extern bool overlaps_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool overlaps_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool overlaps_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool overlaps_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool overlaps_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overlaps_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool overleft_float_tfloat(double d, const Temporal *tnumber);` `right_float_tfloat` used instead
- [ ] `extern bool overleft_int_tint(int i, const Temporal *tnumber);` `right_int_tint` used instead
- [x] `extern bool overleft_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern bool overleft_tint_int(const Temporal *tnumber, int i);`
- [ ] `extern bool overright_float_tfloat(double d, const Temporal *tnumber);` `left_float_tfloat` used instead
- [ ] `extern bool overright_int_tint(int i, const Temporal *tnumber);` `left_int_tint` used instead
- [x] `extern bool overright_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern bool overright_tint_int(const Temporal *tnumber, int i);`
- [ ] `extern bool right_float_tfloat(double d, const Temporal *tnumber);` `overleft_float_tfloat` used instead
- [ ] `extern bool right_int_tint(int i, const Temporal *tnumber);` `overleft_int_tint` used instead
- [x] `extern bool right_tfloat_float(const Temporal *tnumber, double d);`
- [x] `extern bool right_tint_int(const Temporal *tnumber, int i);`
- [ ] `extern bool same_float_tfloat(double d, const Temporal *tnumber);` `same_tfloat_float` used instead
- [ ] `extern bool same_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `same_tpoint_geo` used instead
- [ ] `extern bool same_int_tint(int i, const Temporal *tnumber);` `same_tint_int` used instead
- [x] `extern bool same_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool same_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [ ] `extern bool same_span_tnumber(const Span *span, const Temporal *tnumber);` `same_tnumber_span` used instead
- [x] `extern bool same_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool same_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool same_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool same_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool same_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool same_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool same_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [x] `extern bool same_tfloat_float(const Temporal *tnumber, double d);`
- [ ] `extern bool same_timestamp_temporal(TimestampTz t, const Temporal *temp);`
- [x] `extern bool same_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool same_tint_int(const Temporal *tnumber, int i);`
- [x] `extern bool same_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool same_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool same_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool same_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool same_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool same_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`



### Position functions for temporal types

- [ ] `extern bool above_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `overbelow_tpoint_geo` used instead
- [x] `extern bool above_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool above_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool above_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool above_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [x] `extern bool after_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool after_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [x] `extern bool after_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool after_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool after_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool after_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool after_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool after_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool after_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [ ] `extern bool after_timestamp_temporal(TimestampTz t, const Temporal *temp);` `overbefore_temporal_timestamp` used instead
- [x] `extern bool after_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool after_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool after_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool after_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool after_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool back_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `overfront_tpoint_geo` used instead
- [x] `extern bool back_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool back_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool back_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool back_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [x] `extern bool before_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool before_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [x] `extern bool before_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool before_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool before_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool before_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool before_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool before_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool before_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [ ] `extern bool before_timestamp_temporal(TimestampTz t, const Temporal *temp);` `overafter_temporal_timestamp` used instead
- [x] `extern bool before_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool before_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool before_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool before_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool before_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool below_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `overabove_tpoint_geo` used instead
- [x] `extern bool below_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool below_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool below_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool below_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool front_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `overback_tpoint_geo` used instead
- [x] `extern bool front_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool front_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool front_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool front_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool left_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `overright_tpoint_geo` used instead
- [ ] `extern bool left_span_tnumber(const Span *span, const Temporal *tnumber);` `overright_span_tnumber` used instead
- [x] `extern bool left_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool left_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool left_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool left_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool left_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool left_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool left_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool left_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool overabove_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `below_tpoint_geo` used instead
- [x] `extern bool overabove_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overabove_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool overabove_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overabove_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [x] `extern bool overafter_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool overafter_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [x] `extern bool overafter_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overafter_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool overafter_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool overafter_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool overafter_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool overafter_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool overafter_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [ ] `extern bool overafter_timestamp_temporal(TimestampTz t, const Temporal *temp);` `before_temporal_timestamp` used instead
- [x] `extern bool overafter_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool overafter_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool overafter_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool overafter_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overafter_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool overback_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `front_tpoint_geo` used instead
- [x] `extern bool overback_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overback_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool overback_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overback_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [x] `extern bool overbefore_period_temporal(const Period *p, const Temporal *temp);`
- [x] `extern bool overbefore_periodset_temporal(const PeriodSet *ps, const Temporal *temp);`
- [x] `extern bool overbefore_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overbefore_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool overbefore_temporal_period(const Temporal *temp, const Period *p);`
- [x] `extern bool overbefore_temporal_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool overbefore_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool overbefore_temporal_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool overbefore_temporal_timestampset(const Temporal *temp, const TimestampSet *ts);`
- [ ] `extern bool overbefore_timestamp_temporal(TimestampTz t, const Temporal *temp);` `after_temporal_timestamp` used instead
- [x] `extern bool overbefore_timestampset_temporal(const TimestampSet *ts, const Temporal *temp);`
- [x] `extern bool overbefore_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool overbefore_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool overbefore_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overbefore_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool overbelow_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `above_tpoint_geo` used instead
- [x] `extern bool overbelow_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overbelow_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool overbelow_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overbelow_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool overfront_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `back_tpoint_geo` used instead
- [x] `extern bool overfront_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overfront_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool overfront_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overfront_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool overleft_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `right_tpoint_geo` used instead
- [ ] `extern bool overleft_span_tnumber(const Span *span, const Temporal *tnumber);` `right_span_tnumber` used instead
- [x] `extern bool overleft_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overleft_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool overleft_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool overleft_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool overleft_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool overleft_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool overleft_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overleft_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool overright_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `left_tpoint_geo` used instead
- [ ] `extern bool overright_span_tnumber(const Span *span, const Temporal *tnumber);` `left_span_tnumber` used instead
- [x] `extern bool overright_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool overright_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool overright_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool overright_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool overright_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool overright_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool overright_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool overright_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`
- [ ] `extern bool right_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `overright_tpoint_geo` used instead
- [ ] `extern bool right_span_tnumber(const Span *span, const Temporal *tnumber);` `overleft_span_tnumber` used instead
- [x] `extern bool right_stbox_tpoint(const STBOX *stbox, const Temporal *tpoint);`
- [x] `extern bool right_tbox_tnumber(const TBOX *tbox, const Temporal *tnumber);`
- [x] `extern bool right_tnumber_span(const Temporal *tnumber, const Span *span);`
- [x] `extern bool right_tnumber_tbox(const Temporal *tnumber, const TBOX *tbox);`
- [x] `extern bool right_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);`
- [x] `extern bool right_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);`
- [x] `extern bool right_tpoint_stbox(const Temporal *tpoint, const STBOX *stbox);`
- [x] `extern bool right_tpoint_tpoint(const Temporal *tpoint1, const Temporal *tpoint2);`



### Distance functions for temporal types

- [x] `extern Temporal *distance_tfloat_float(const Temporal *temp, double d);`
- [x] `extern Temporal *distance_tint_int(const Temporal *temp, int i);`
- [x] `extern Temporal *distance_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern Temporal *distance_tpoint_geo(const Temporal *temp, const GSERIALIZED *geo);`
- [x] `extern Temporal *distance_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern double nad_stbox_geo(const STBOX *box, const GSERIALIZED *gs);`
- [x] `extern double nad_stbox_stbox(const STBOX *box1, const STBOX *box2);`
- [x] `extern double nad_tbox_tbox(const TBOX *box1, const TBOX *box2);`
- [x] `extern double nad_tfloat_float(const Temporal *temp, double d);`
- [x] `extern double nad_tfloat_tfloat(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern int nad_tint_int(const Temporal *temp, int i);`
- [x] `extern int nad_tint_tint(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern double nad_tnumber_tbox(const Temporal *temp, const TBOX *box);`
- [x] `extern double nad_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern double nad_tpoint_stbox(const Temporal *temp, const STBOX *box);`
- [x] `extern double nad_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern TInstant *nai_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern TInstant *nai_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern bool shortestline_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, GSERIALIZED **result);`
- [x] `extern bool shortestline_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2, GSERIALIZED **result);`



### Ever/always functions for temporal types

- [x] `extern bool tbool_always_eq(const Temporal *temp, bool b);`
- [x] `extern bool tbool_ever_eq(const Temporal *temp, bool b);`
- [x] `extern bool tfloat_always_eq(const Temporal *temp, double d);`
- [x] `extern bool tfloat_always_le(const Temporal *temp, double d);`
- [x] `extern bool tfloat_always_lt(const Temporal *temp, double d);`
- [x] `extern bool tfloat_ever_eq(const Temporal *temp, double d);`
- [x] `extern bool tfloat_ever_le(const Temporal *temp, double d);`
- [x] `extern bool tfloat_ever_lt(const Temporal *temp, double d);`
- [x] `extern bool tgeogpoint_always_eq(const Temporal *temp, GSERIALIZED *gs);`;`
- [x] `extern bool tgeogpoint_ever_eq(const Temporal *temp, GSERIALIZED *gs);`;`
- [x] `extern bool tgeompoint_always_eq(const Temporal *temp, GSERIALIZED *gs);`
- [x] `extern bool tgeompoint_ever_eq(const Temporal *temp, GSERIALIZED *gs);`;`
- [x] `extern bool tint_always_eq(const Temporal *temp, int i);`
- [x] `extern bool tint_always_le(const Temporal *temp, int i);`
- [x] `extern bool tint_always_lt(const Temporal *temp, int i);`
- [x] `extern bool tint_ever_eq(const Temporal *temp, int i);`
- [x] `extern bool tint_ever_le(const Temporal *temp, int i);`
- [x] `extern bool tint_ever_lt(const Temporal *temp, int i);`
- [x] `extern bool ttext_always_eq(const Temporal *temp, text *txt);`
- [x] `extern bool ttext_always_le(const Temporal *temp, text *txt);`
- [x] `extern bool ttext_always_lt(const Temporal *temp, text *txt);`
- [x] `extern bool ttext_ever_eq(const Temporal *temp, text *txt);`
- [x] `extern bool ttext_ever_le(const Temporal *temp, text *txt);`
- [x] `extern bool ttext_ever_lt(const Temporal *temp, text *txt);`



### Comparison functions for temporal types

- [ ] `extern int temporal_cmp(const Temporal *temp1, const Temporal *temp2);` Not used in PyMEOS (used for B-Tree index in MEOS)
- [ ] `extern bool temporal_eq(const Temporal *temp1, const Temporal *temp2);` Not used in PyMEOS (used for B-Tree index in MEOS)
- [ ] `extern bool temporal_ge(const Temporal *temp1, const Temporal *temp2);` Not used in PyMEOS (used for B-Tree index in MEOS)
- [ ] `extern bool temporal_gt(const Temporal *temp1, const Temporal *temp2);` Not used in PyMEOS (used for B-Tree index in MEOS)
- [ ] `extern bool temporal_le(const Temporal *temp1, const Temporal *temp2);` Not used in PyMEOS (used for B-Tree index in MEOS)
- [ ] `extern bool temporal_lt(const Temporal *temp1, const Temporal *temp2);` Not used in PyMEOS (used for B-Tree index in MEOS)
- [ ] `extern bool temporal_ne(const Temporal *temp1, const Temporal *temp2);` Not used in PyMEOS (used for B-Tree index in MEOS)
- [ ] `extern Temporal *teq_bool_tbool(bool b, const Temporal *temp);` `teq_tbool_bool` used instead
- [ ] `extern Temporal *teq_float_tfloat(double d, const Temporal *temp);` `teq_tfloat_float` used instead
- [ ] `extern Temporal *teq_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `teq_tpoint_geo` used instead
- [ ] `extern Temporal *teq_int_tint(int i, const Temporal *temp);` `teq_tint_int` used instead
- [ ] `extern Temporal *teq_point_tgeogpoint(const GSERIALIZED *gs, const Temporal *temp);` `teq_tgeogpoint_point` used instead
- [ ] `extern Temporal *teq_point_tgeompoint(const GSERIALIZED *gs, const Temporal *temp);` `teq_tgeompoint_point` used instead
- [x] `extern Temporal *teq_tbool_bool(const Temporal *temp, bool b);`
- [x] `extern Temporal *teq_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [ ] `extern Temporal *teq_text_ttext(const text *txt, const Temporal *temp);` `teq_ttext_text` used instead
- [x] `extern Temporal *teq_tfloat_float(const Temporal *temp, double d);`
- [x] `extern Temporal *teq_tgeogpoint_point(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern Temporal *teq_tgeompoint_point(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern Temporal *teq_tint_int(const Temporal *temp, int i);`
- [ ] `extern Temporal *teq_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);` `teq_tgeogpoint_point` and `teq_tgeompoint_point` used instead
- [x] `extern Temporal *teq_ttext_text(const Temporal *temp, const text *txt);`
- [ ] `extern Temporal *tge_float_tfloat(double d, const Temporal *temp);` `tlt_tfloat_float` used instead
- [ ] `extern Temporal *tge_int_tint(int i, const Temporal *temp);` `tlt_tint_int` used instead
- [x] `extern Temporal *tge_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [ ] `extern Temporal *tge_text_ttext(const text *txt, const Temporal *temp);` `tlt_ttext_text` used instead
- [x] `extern Temporal *tge_tfloat_float(const Temporal *temp, double d);`
- [x] `extern Temporal *tge_tint_int(const Temporal *temp, int i);`
- [x] `extern Temporal *tge_ttext_text(const Temporal *temp, const text *txt);`
- [ ] `extern Temporal *tgt_float_tfloat(double d, const Temporal *temp);` `tle_tfloat_float` used instead
- [ ] `extern Temporal *tgt_int_tint(int i, const Temporal *temp);` `tle_tint_int` used instead
- [x] `extern Temporal *tgt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [ ] `extern Temporal *tgt_text_ttext(const text *txt, const Temporal *temp);` `tle_ttext_text` used instead
- [x] `extern Temporal *tgt_tfloat_float(const Temporal *temp, double d);`
- [x] `extern Temporal *tgt_tint_int(const Temporal *temp, int i);`
- [x] `extern Temporal *tgt_ttext_text(const Temporal *temp, const text *txt);`
- [ ] `extern Temporal *tle_float_tfloat(double d, const Temporal *temp);` `tgt_tfloat_float` used instead
- [ ] `extern Temporal *tle_int_tint(int i, const Temporal *temp);` `tgt_tint_int` used instead
- [x] `extern Temporal *tle_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [ ] `extern Temporal *tle_text_ttext(const text *txt, const Temporal *temp);` `tgt_ttext_text` used instead
- [x] `extern Temporal *tle_tfloat_float(const Temporal *temp, double d);`
- [x] `extern Temporal *tle_tint_int(const Temporal *temp, int i);`
- [x] `extern Temporal *tle_ttext_text(const Temporal *temp, const text *txt);`
- [ ] `extern Temporal *tlt_float_tfloat(double d, const Temporal *temp);` `tge_tfloat_float` used instead
- [ ] `extern Temporal *tlt_int_tint(int i, const Temporal *temp);` `tge_tint_int` used instead
- [x] `extern Temporal *tlt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [ ] `extern Temporal *tlt_text_ttext(const text *txt, const Temporal *temp);` `tge_ttext_text` used instead
- [x] `extern Temporal *tlt_tfloat_float(const Temporal *temp, double d);`
- [x] `extern Temporal *tlt_tint_int(const Temporal *temp, int i);`
- [x] `extern Temporal *tlt_ttext_text(const Temporal *temp, const text *txt);`
- [ ] `extern Temporal *tne_bool_tbool(bool b, const Temporal *temp);` `tne_tbool_bool` used instead
- [ ] `extern Temporal *tne_float_tfloat(double d, const Temporal *temp);` `tne_tfloat_float` used instead
- [ ] `extern Temporal *tne_geo_tpoint(const GSERIALIZED *geo, const Temporal *tpoint);` `tne_tpoint_geo` used instead
- [ ] `extern Temporal *tne_int_tint(int i, const Temporal *temp);` `tne_tint_int` used instead
- [ ] `extern Temporal *tne_point_tgeogpoint(const GSERIALIZED *gs, const Temporal *temp);` `tne_tgeogpoint_point` used instead
- [ ] `extern Temporal *tne_point_tgeompoint(const GSERIALIZED *gs, const Temporal *temp);` `tne_tgeompoint_point` used instead
- [x] `extern Temporal *tne_tbool_bool(const Temporal *temp, bool b);`
- [x] `extern Temporal *tne_temporal_temporal(const Temporal *temp1, const Temporal *temp2);`
- [ ] `extern Temporal *tne_text_ttext(const text *txt, const Temporal *temp);` `tne_ttext_text` used instead
- [x] `extern Temporal *tne_tfloat_float(const Temporal *temp, double d);`
- [x] `extern Temporal *tne_tgeogpoint_point(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern Temporal *tne_tgeompoint_point(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern Temporal *tne_tint_int(const Temporal *temp, int i);`
- [ ] `extern Temporal *tne_tpoint_geo(const Temporal *tpoint, const GSERIALIZED *geo);` `tne_tgeogpoint_point` and `tne_tgeompoint_point` used instead
- [x] `extern Temporal *tne_ttext_text(const Temporal *temp, const text *txt);`

##  Spatial functions for temporal point types

### Spatial accessor functions for temporal point types

- [ ] `extern bool bearing_point_point(const GSERIALIZED *geo1, const GSERIALIZED *geo2, double *result);` Class not defined in PyMEOS 
- [x] `extern Temporal *bearing_tpoint_point(const Temporal *temp, const GSERIALIZED *gs, bool invert);`
- [x] `extern Temporal *bearing_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern Temporal *tpoint_azimuth(const Temporal *temp);`
- [x] `extern Temporal *tpoint_cumulative_length(const Temporal *temp);`
- [x] `extern Temporal *tpoint_get_coord(const Temporal *temp, int coord);`
- [x] `extern bool tpoint_is_simple(const Temporal *temp);`
- [x] `extern double tpoint_length(const Temporal *temp);`
- [x] `extern Temporal *tpoint_speed(const Temporal *temp);`
- [x] `extern int tpoint_srid(const Temporal *temp);`
- [x] `extern STBOX *tpoint_stboxes(const Temporal *temp, int *count);`
- [x] `extern GSERIALIZED *tpoint_trajectory(const Temporal *temp);`



### Spatial transformation functions for temporal point types

- [x] `extern STBOX *geo_expand_spatial(const GSERIALIZED *gs, double d);`
- [x] `extern Temporal *tgeompoint_tgeogpoint(const Temporal *temp, bool oper);`
- [x] `extern STBOX *tpoint_expand_spatial(const Temporal *temp, double d);`
- [x] `extern Temporal **tpoint_make_simple(const Temporal *temp, int *count);`
- [x] `extern Temporal *tpoint_set_srid(const Temporal *temp, int32 srid);`



### Spatial relationship functions for temporal point types

- [x] `extern int contains_geo_tpoint(const GSERIALIZED *geo, const Temporal *temp);`
- [x] `extern int disjoint_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern int disjoint_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern int dwithin_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, double dist);`
- [x] `extern int dwithin_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2, double dist);`
- [x] `extern int intersects_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern int intersects_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern Temporal *tcontains_geo_tpoint(const GSERIALIZED *gs, const Temporal *temp, bool restr, bool atvalue);`
- [x] `extern Temporal *tdisjoint_tpoint_geo(const Temporal *temp, const GSERIALIZED *geo, bool restr, bool atvalue);`
- [x] `extern Temporal *tdwithin_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, double dist, bool restr, bool atvalue);`
- [x] `extern Temporal *tdwithin_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2, double dist, bool restr, bool atvalue);`
- [x] `extern Temporal *tintersects_tpoint_geo(const Temporal *temp, const GSERIALIZED *geo, bool restr, bool atvalue);`
- [x] `extern int touches_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);`
- [x] `extern Temporal *ttouches_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, bool restr, bool atvalue);`



### Time functions for temporal types

- [x] `extern bool temporal_intersects_period(const Temporal *temp, const Period *p);`
- [x] `extern bool temporal_intersects_periodset(const Temporal *temp, const PeriodSet *ps);`
- [x] `extern bool temporal_intersects_timestamp(const Temporal *temp, TimestampTz t);`
- [x] `extern bool temporal_intersects_timestampset(const Temporal *temp, const TimestampSet *ss);`



### Local aggregate functions for temporal types

- [x] `extern double tnumber_integral(const Temporal *temp);`
- [x] `extern double tnumber_twavg(const Temporal *temp);`
- [x] `extern GSERIALIZED *tpoint_twcentroid(const Temporal *temp);`

### Temporal aggregate functions for temporal types

- [ ] `extern void skiplist_free(SkipList *list);` Not necessary in PyMEOS

- [x] `extern Period *temporal_extent_transfn(Period *p, Temporal *temp);`
- [x] `extern TBOX *tnumber_extent_transfn(TBOX *box, Temporal *temp);`
- [ ] `extern STBOX *tpoint_extent_transfn(STBOX *box, Temporal *temp);`

- [x] `extern SkipList *temporal_tcount_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tbool_tand_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tbool_tor_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tint_tmin_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tfloat_tmin_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tint_tmax_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tfloat_tmax_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tint_tsum_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tfloat_tsum_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *tnumber_tavg_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *ttext_tmin_transfn(SkipList *state, Temporal *temp);`
- [x] `extern SkipList *ttext_tmax_transfn(SkipList *state, Temporal *temp);`

- [x] `extern Temporal *temporal_tagg_finalfn(SkipList *state);`
- [x] `extern Temporal *tnumber_tavg_finalfn(SkipList *state);`



### Tile functions for temporal types

- [x] `extern Temporal **temporal_time_split(const Temporal *temp, TimestampTz start,
  TimestampTz end, int64 tunits, TimestampTz torigin, int count,
  TimestampTz **buckets, int *newcount);`
- [x] `extern Temporal **tint_value_split(const Temporal *temp, int start_bucket,
  int size, int count, int **buckets, int *newcount);`
- [x] `extern Temporal **tfloat_value_split(const Temporal *temp, double start_bucket,
  double size, int count, float **buckets, int *newcount);`



### Similarity functions for temporal types

- [x] `extern double temporal_frechet_distance(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern double temporal_dyntimewarp_distance(const Temporal *temp1, const Temporal *temp2);`
- [x] `extern Match *temporal_frechet_path(const Temporal *temp1, const Temporal *temp2, int *count);`
- [x] `extern Match *temporal_dyntimewarp_path(const Temporal *temp1, const Temporal *temp2, int *count);`



### Analytics functions for temporal types

- [ ] `extern Temporal *geo_to_tpoint(const GSERIALIZED *geo);`
- [x] `extern Temporal *temporal_simplify(const Temporal *temp, double eps_dist, bool synchronized);`
- [ ] `extern bool tpoint_AsMVTGeom(const Temporal *temp, const STBOX *bounds, int32_t extent,
  int32_t buffer, bool clip_geom, GSERIALIZED **geom, int64 **timesarr, int *count);`
- [ ] `extern bool tpoint_to_geo_measure(const Temporal *tpoint, const Temporal *measure, bool segmentize, GSERIALIZED **result);`


