//-------------------- meos.h --------------------


//#include <stdbool.h>
//#include <stdint.h>
//#include <stdio.h>

typedef char *Pointer;
typedef uintptr_t Datum;

typedef signed char int8;
typedef signed short int16;
typedef signed int int32;
typedef long int int64;

typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned long int uint64;

typedef int32 DateADT;
typedef int64 TimeADT;
typedef int64 Timestamp;
typedef int64 TimestampTz;
typedef int64 TimeOffset;
typedef int32 fsec_t;      

typedef struct
{
  TimeOffset time;  
  int32 day;        
  int32 month;      
} Interval;

typedef struct varlena
{
  char vl_len_[4];  
  char vl_dat[];    
} varlena;

typedef varlena text;
typedef struct varlena bytea;

              

typedef uint16_t lwflags_t;

typedef struct {
    double afac, bfac, cfac, dfac, efac, ffac, gfac, hfac, ifac, xoff, yoff, zoff;
} AFFINE;

typedef struct
{
    double xmin, ymin, zmin;
    double xmax, ymax, zmax;
    int32_t srid;
}
BOX3D;

typedef struct
{
    lwflags_t flags;
    double xmin;
    double xmax;
    double ymin;
    double ymax;
    double zmin;
    double zmax;
    double mmin;
    double mmax;
} GBOX;

typedef struct
{
    double  a;  
    double  b;  
    double  f;  
    double  e;  
    double  e_sq;   
    double  radius;  
    char    name[20];  
}
SPHEROID;

typedef struct
{
    double x, y;
}
POINT2D;

typedef struct
{
    double x, y, z;
}
POINT3DZ;

typedef struct
{
    double x, y, z;
}
POINT3D;

typedef struct
{
    double x, y, m;
}
POINT3DM;

typedef struct
{
    double x, y, z, m;
}
POINT4D;

typedef struct
{
    uint32_t npoints;   
    uint32_t maxpoints; 

    
    lwflags_t flags;

    
    uint8_t *serialized_pointlist;
}
POINTARRAY;

typedef struct
{
    uint32_t size; 
    uint8_t srid[3]; 
    uint8_t gflags; 
    uint8_t data[1]; 
} GSERIALIZED;

typedef struct
{
    GBOX *bbox;
    void *data;
    int32_t srid;
    lwflags_t flags;
    uint8_t type;
    char pad[1]; 
}
LWGEOM;

typedef struct
{
    GBOX *bbox;
    POINTARRAY *point;  
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
}
LWPOINT; 

typedef struct
{
    GBOX *bbox;
    POINTARRAY *points; 
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
}
LWLINE; 

typedef struct
{
    GBOX *bbox;
    POINTARRAY *points;
    int32_t srid;
    lwflags_t flags;
    uint8_t type;
    char pad[1]; 
}
LWTRIANGLE;

typedef struct
{
    GBOX *bbox;
    POINTARRAY *points; 
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
}
LWCIRCSTRING; 

typedef struct
{
    GBOX *bbox;
    POINTARRAY **rings; 
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t nrings;   
    uint32_t maxrings; 
}
LWPOLY; 

typedef struct
{
    GBOX *bbox;
    LWPOINT **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWMPOINT;

typedef struct
{
    GBOX *bbox;
    LWLINE **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWMLINE;

typedef struct
{
    GBOX *bbox;
    LWPOLY **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWMPOLY;

typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWCOLLECTION;

typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWCOMPOUND; 

typedef struct
{
    GBOX *bbox;
    LWGEOM **rings;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t nrings;    
    uint32_t maxrings;  
}
LWCURVEPOLY; 

typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWMCURVE;

typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWMSURFACE;

typedef struct
{
    GBOX *bbox;
    LWPOLY **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWPSURFACE;

typedef struct
{
    GBOX *bbox;
    LWTRIANGLE **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; 
    char pad[1]; 
    uint32_t ngeoms;   
    uint32_t maxgeoms; 
}
LWTIN;

extern LWPOINT *lwpoint_make(int32_t srid, int hasz, int hasm, const POINT4D *p);

extern LWGEOM *lwgeom_from_gserialized(const GSERIALIZED *g);
/* extern GSERIALIZED *geo_from_lwgeom(LWGEOM *geom, size_t *size);  (undefined) */

extern int32_t lwgeom_get_srid(const LWGEOM *geom);

extern double lwpoint_get_x(const LWPOINT *point);
extern double lwpoint_get_y(const LWPOINT *point);
extern double lwpoint_get_z(const LWPOINT *point);
extern double lwpoint_get_m(const LWPOINT *point);

extern int lwgeom_has_z(const LWGEOM *geom);
extern int lwgeom_has_m(const LWGEOM *geom);

              

typedef struct
{
  int32 vl_len_;        
  uint8 settype;        
  uint8 basetype;       
  int16 flags;          
  int32 count;          
  int32 maxcount;       
  int16 bboxsize;       
} Set;

typedef struct
{
  uint8 spantype;       
  uint8 basetype;       
  bool lower_inc;       
  bool upper_inc;       
  char padding[4];      
  Datum lower;          
  Datum upper;          
} Span;

typedef struct
{
  int32 vl_len_;        
  uint8 spansettype;    
  uint8 spantype;       
  uint8 basetype;       
  char padding;         
  int32 count;          
  int32 maxcount;       
  Span span;            
  Span elems[1];        
} SpanSet;

typedef struct
{
  Span period;          
  Span span;            
  int16 flags;          
} TBox;

typedef struct
{
  Span period;          
  double xmin;          
  double ymin;          
  double zmin;          
  double xmax;          
  double ymax;          
  double zmax;          
  int32  srid;          
  int16  flags;         
} STBox;

typedef enum
{
  ANYTEMPSUBTYPE =   0,  
  TINSTANT =         1,  
  TSEQUENCE =        2,  
  TSEQUENCESET =     3,  
} tempSubtype;

typedef enum
{
  INTERP_NONE =    0,
  DISCRETE =       1,
  STEP =           2,
  LINEAR =         3,
} interpType;

typedef enum
{
  INTERSECTS =     0,
  CONTAINS =       1,
  TOUCHES =        2,
} spatialRel;

typedef struct
{
  int32 vl_len_;        
  uint8 temptype;       
  uint8 subtype;        
  int16 flags;          
  
} Temporal;

typedef struct
{
  int32 vl_len_;        
  uint8 temptype;       
  uint8 subtype;        
  int16 flags;          
  TimestampTz t;        
  Datum value;          
  
} TInstant;

typedef struct
{
  int32 vl_len_;        
  uint8 temptype;       
  uint8 subtype;        
  int16 flags;          
  int32 count;          
  int32 maxcount;       
  int16 bboxsize;       
  char padding[6];      
  Span period;          
  
} TSequence;

typedef struct
{
  int32 vl_len_;        
  uint8 temptype;       
  uint8 subtype;        
  int16 flags;          
  int32 count;          
  int32 totalcount;     
  int32 maxcount;       
  int16 bboxsize;       
  int16 padding;        
  Span period;          
  
} TSequenceSet;

typedef struct
{
  int i;
  int j;
} Match;

#define SKIPLIST_MAXLEVEL 32
typedef struct
{
  void *value;
  int height;
  int next[SKIPLIST_MAXLEVEL];
} SkipListElem;

typedef struct
{
  int capacity;
  int next;
  int length;
  int *freed;
  int freecount;
  int freecap;
  int tail;
  void *extra;
  size_t extrasize;
  SkipListElem *elems;
} SkipList;

typedef enum
{
  MEOS_SUCCESS                  = 0,  

  MEOS_ERR_INTERNAL_ERROR       = 1,  
  MEOS_ERR_INTERNAL_TYPE_ERROR  = 2,  
  MEOS_ERR_VALUE_OUT_OF_RANGE   = 3,  
  MEOS_ERR_DIVISION_BY_ZERO     = 4,  
  MEOS_ERR_MEMORY_ALLOC_ERROR   = 5,  
  MEOS_ERR_AGGREGATION_ERROR    = 6,  
  MEOS_ERR_DIRECTORY_ERROR      = 7,  
  MEOS_ERR_FILE_ERROR           = 8,  

  MEOS_ERR_INVALID_ARG          = 10, 
  MEOS_ERR_INVALID_ARG_TYPE     = 11, 
  MEOS_ERR_INVALID_ARG_VALUE    = 12, 

  MEOS_ERR_MFJSON_INPUT         = 20, 
  MEOS_ERR_MFJSON_OUTPUT        = 21, 
  MEOS_ERR_TEXT_INPUT           = 22, 
  MEOS_ERR_TEXT_OUTPUT          = 23, 
  MEOS_ERR_WKB_INPUT            = 24, 
  MEOS_ERR_WKB_OUTPUT           = 25, 
  MEOS_ERR_GEOJSON_INPUT        = 26, 
  MEOS_ERR_GEOJSON_OUTPUT       = 27, 

} errorCode;

extern void meos_error(int errlevel, int errcode, char *format, ...);

extern int meos_errno(void);
extern int meos_errno_set(int err);
extern int meos_errno_restore(int err);
extern int meos_errno_reset(void);

typedef void (*error_handler_fn)(int, int, char *);

extern void meos_initialize_timezone(const char *name);
extern void meos_initialize_error_handler(error_handler_fn err_handler);
extern void meos_finalize_timezone(void);

extern bool meos_set_datestyle(char *newval, void *extra);
extern bool meos_set_intervalstyle(char *newval, int extra);
extern char *meos_get_datestyle(void);
extern char *meos_get_intervalstyle(void);

extern void meos_initialize(const char *tz_str, error_handler_fn err_handler);
extern void meos_finalize(void);

extern DateADT add_date_int(DateADT d, int32 days);
extern Interval *add_interval_interval(const Interval *interv1, const Interval *interv2);
extern TimestampTz add_timestamptz_interval(TimestampTz t, const Interval *interv);
extern bool bool_in(const char *str);
extern char *bool_out(bool b);
extern text *cstring2text(const char *str);
extern TimestampTz date_to_timestamptz(DateADT d);
extern Interval *minus_date_date(DateADT d1, DateADT d2);
extern DateADT minus_date_int(DateADT d, int32 days);
extern TimestampTz minus_timestamptz_interval(TimestampTz t, const Interval *interv);
extern Interval *minus_timestamptz_timestamptz(TimestampTz t1, TimestampTz t2);
extern Interval *mult_interval_double(const Interval *interv, double factor);
extern DateADT pg_date_in(const char *str);
extern char *pg_date_out(DateADT d);
extern int pg_interval_cmp(const Interval *interv1, const Interval *interv2);
extern Interval *pg_interval_in(const char *str, int32 typmod);
extern Interval *pg_interval_make(int32 years, int32 months, int32 weeks, int32 days, int32 hours, int32 mins, double secs);
extern char *pg_interval_out(const Interval *interv);
extern TimeADT pg_time_in(const char *str, int32 typmod);
extern char *pg_time_out(TimeADT t);
extern Timestamp pg_timestamp_in(const char *str, int32 typmod);
extern char *pg_timestamp_out(Timestamp t);
extern TimestampTz pg_timestamptz_in(const char *str, int32 typmod);
extern char *pg_timestamptz_out(TimestampTz t);
extern char *text2cstring(const text *txt);
extern int text_cmp(const text *txt1, const text *txt2);
extern text *text_copy(const text *txt);
/* extern text *text_initcap(const text *txt);  (undefined) */
/* extern text *text_lower(const text *txt);  (undefined) */
extern char *text_out(const text *txt);
/* extern text *text_upper(const text *txt);  (undefined) */
extern text *textcat_text_text(const text *txt1, const text *txt2);
extern DateADT timestamptz_to_date(TimestampTz t);

extern bytea *geo_as_ewkb(const GSERIALIZED *gs, char *endian);
extern char *geo_as_ewkt(const GSERIALIZED *gs, int precision);
extern char *geo_as_geojson(const GSERIALIZED *gs, int option, int precision, char *srs);
extern char *geo_as_hexewkb(const GSERIALIZED *gs, const char *endian);
extern char *geo_as_text(const GSERIALIZED *gs, int precision);
extern GSERIALIZED *geo_from_ewkb(const bytea *bytea_wkb, int32 srid);
extern GSERIALIZED *geo_from_geojson(const char *geojson);
extern char *geo_out(const GSERIALIZED *gs);
extern bool geo_same(const GSERIALIZED *gs1, const GSERIALIZED *gs2);
extern GSERIALIZED *geography_from_hexewkb(const char *wkt);
extern GSERIALIZED *geography_from_text(char *wkt, int srid);
extern GSERIALIZED *geometry_from_hexewkb(const char *wkt);
extern GSERIALIZED *geometry_from_text(char *wkt, int srid);
extern GSERIALIZED *pgis_geography_in(char *str, int32 geog_typmod);
extern GSERIALIZED *pgis_geometry_in(char *str, int32 typmod);

extern Set *bigintset_in(const char *str);
extern char *bigintset_out(const Set *set);
extern Span *bigintspan_in(const char *str);
extern char *bigintspan_out(const Span *s);
extern SpanSet *bigintspanset_in(const char *str);
extern char *bigintspanset_out(const SpanSet *ss);
extern Set *dateset_in(const char *str);
extern char *dateset_out(const Set *s);
extern Span *datespan_in(const char *str);
extern char *datespan_out(const Span *s);
extern SpanSet *datespanset_in(const char *str);
extern char *datespanset_out(const SpanSet *ss);
extern Set *floatset_in(const char *str);
extern char *floatset_out(const Set *set, int maxdd);
extern Span *floatspan_in(const char *str);
extern char *floatspan_out(const Span *s, int maxdd);
extern SpanSet *floatspanset_in(const char *str);
extern char *floatspanset_out(const SpanSet *ss, int maxdd);
extern Set *geogset_in(const char *str);
extern Set *geomset_in(const char *str);
extern char *geoset_as_ewkt(const Set *set, int maxdd);
extern char *geoset_as_text(const Set *set, int maxdd);
extern char *geoset_out(const Set *set, int maxdd);
extern Set *intset_in(const char *str);
extern char *intset_out(const Set *set);
extern Span *intspan_in(const char *str);
extern char *intspan_out(const Span *s);
extern SpanSet *intspanset_in(const char *str);
extern char *intspanset_out(const SpanSet *ss);
extern char *set_as_hexwkb(const Set *s, uint8_t variant, size_t *size_out);
extern uint8_t *set_as_wkb(const Set *s, uint8_t variant, size_t *size_out);
extern Set *set_from_hexwkb(const char *hexwkb);
extern Set *set_from_wkb(const uint8_t *wkb, size_t size);
extern char *span_as_hexwkb(const Span *s, uint8_t variant, size_t *size_out);
extern uint8_t *span_as_wkb(const Span *s, uint8_t variant, size_t *size_out);
extern Span *span_from_hexwkb(const char *hexwkb);
extern Span *span_from_wkb(const uint8_t *wkb, size_t size);
extern char *spanset_as_hexwkb(const SpanSet *ss, uint8_t variant, size_t *size_out);
extern uint8_t *spanset_as_wkb(const SpanSet *ss, uint8_t variant, size_t *size_out);
extern SpanSet *spanset_from_hexwkb(const char *hexwkb);
extern SpanSet *spanset_from_wkb(const uint8_t *wkb, size_t size);
extern Set *textset_in(const char *str);
extern char *textset_out(const Set *set);
extern Set *tstzset_in(const char *str);
extern char *tstzset_out(const Set *set);
extern Span *tstzspan_in(const char *str);
extern char *tstzspan_out(const Span *s);
extern SpanSet *tstzspanset_in(const char *str);
extern char *tstzspanset_out(const SpanSet *ss);

extern Set *bigintset_make(const int64 *values, int count);
extern Span *bigintspan_make(int64 lower, int64 upper, bool lower_inc, bool upper_inc);
extern Set *dateset_make(const DateADT *values, int count);
extern Span *datespan_make(DateADT lower, DateADT upper, bool lower_inc, bool upper_inc);
extern Set *floatset_make(const double *values, int count);
extern Span *floatspan_make(double lower, double upper, bool lower_inc, bool upper_inc);
extern Set *geoset_make(const GSERIALIZED **values, int count);
extern Set *intset_make(const int *values, int count);
extern Span *intspan_make(int lower, int upper, bool lower_inc, bool upper_inc);
extern Set *set_copy(const Set *s);
extern Span *span_copy(const Span *s);
extern SpanSet *spanset_copy(const SpanSet *ss);
extern SpanSet *spanset_make(Span *spans, int count, bool normalize, bool ordered);
extern Set *textset_make(const text **values, int count);
extern Set *tstzset_make(const TimestampTz *values, int count);
extern Span *tstzspan_make(TimestampTz lower, TimestampTz upper, bool lower_inc, bool upper_inc);

extern Set *bigint_to_set(int64 i);
extern Span *bigint_to_span(int i);
extern SpanSet *bigint_to_spanset(int i);
extern Set *date_to_set(DateADT d);
extern Span *date_to_span(DateADT d);
extern SpanSet *date_to_spanset(DateADT d);
extern Set *dateset_to_tstzset(const Set *s);
extern Span *datespan_to_tstzspan(const Span *s);
extern SpanSet *datespanset_to_tstzspanset(const SpanSet *ss);
extern Set *float_to_set(double d);
extern Span *float_to_span(double d);
extern SpanSet *float_to_spanset(double d);
extern Set *floatset_to_intset(const Set *s);
extern Span *floatspan_to_intspan(const Span *s);
extern SpanSet *floatspanset_to_intspanset(const SpanSet *ss);
extern Set *geo_to_set(GSERIALIZED *gs);
extern Set *int_to_set(int i);
extern Span *int_to_span(int i);
extern SpanSet *int_to_spanset(int i);
extern Set *intset_to_floatset(const Set *s);
extern Span *intspan_to_floatspan(const Span *s);
extern SpanSet *intspanset_to_floatspanset(const SpanSet *ss);
extern SpanSet *set_to_spanset(const Set *s);
extern SpanSet *span_to_spanset(const Span *s);
extern Set *text_to_set(text *txt);
extern Set *timestamptz_to_set(TimestampTz t);
extern Span *timestamptz_to_span(TimestampTz t);
extern SpanSet *timestamptz_to_spanset(TimestampTz t);
extern Set *tstzset_to_dateset(const Set *s);
extern Span *tstzspan_to_datespan(const Span *s);
extern SpanSet *tstzspanset_to_datespanset(const SpanSet *ss);

extern int64 bigintset_end_value(const Set *s);
extern int64 bigintset_start_value(const Set *s);
extern bool bigintset_value_n(const Set *s, int n, int64 *result);
extern int64 *bigintset_values(const Set *s);
extern int64 bigintspan_lower(const Span *s);
extern int64 bigintspan_upper(const Span *s);
extern int64 bigintspan_width(const Span *s);
extern int64 bigintspanset_lower(const SpanSet *ss);
extern int64 bigintspanset_upper(const SpanSet *ss);
extern int64 bigintspanset_width(const SpanSet *ss, bool boundspan);
extern DateADT dateset_end_value(const Set *s);
extern DateADT dateset_start_value(const Set *s);
extern bool dateset_value_n(const Set *s, int n, DateADT *result);
extern DateADT *dateset_values(const Set *s);
extern Interval *datespan_duration(const Span *s);
extern DateADT datespan_lower(const Span *s);
extern DateADT datespan_upper(const Span *s);
extern bool datespanset_date_n(const SpanSet *ss, int n, DateADT *result);
extern DateADT *datespanset_dates(const SpanSet *ss, int *count);
extern Interval *datespanset_duration(const SpanSet *ss, bool boundspan);
extern DateADT datespanset_end_date(const SpanSet *ss);
extern int datespanset_num_dates(const SpanSet *ss);
extern DateADT datespanset_start_date(const SpanSet *ss);
extern double floatset_end_value(const Set *s);
extern double floatset_start_value(const Set *s);
extern bool floatset_value_n(const Set *s, int n, double *result);
extern double *floatset_values(const Set *s);
extern double floatspan_lower(const Span *s);
extern double floatspan_upper(const Span *s);
extern double floatspan_width(const Span *s);
extern double floatspanset_lower(const SpanSet *ss);
extern double floatspanset_upper(const SpanSet *ss);
extern double floatspanset_width(const SpanSet *ss, bool boundspan);
extern GSERIALIZED *geoset_end_value(const Set *s);
extern int geoset_srid(const Set *s);
extern GSERIALIZED *geoset_start_value(const Set *s);
extern bool geoset_value_n(const Set *s, int n, GSERIALIZED **result);
extern GSERIALIZED **geoset_values(const Set *s);
extern int intset_end_value(const Set *s);
extern int intset_start_value(const Set *s);
extern bool intset_value_n(const Set *s, int n, int *result);
extern int *intset_values(const Set *s);
extern int intspan_lower(const Span *s);
extern int intspan_upper(const Span *s);
extern int intspan_width(const Span *s);
extern int intspanset_lower(const SpanSet *ss);
extern int intspanset_upper(const SpanSet *ss);
extern int intspanset_width(const SpanSet *ss, bool boundspan);
extern uint32 set_hash(const Set *s);
extern uint64 set_hash_extended(const Set *s, uint64 seed);
extern int set_num_values(const Set *s);
extern Span *set_to_span(const Set *s);
extern uint32 span_hash(const Span *s);
extern uint64 span_hash_extended(const Span *s, uint64 seed);
extern bool span_lower_inc(const Span *s);
extern bool span_upper_inc(const Span *s);
extern Span *spanset_end_span(const SpanSet *ss);
extern uint32 spanset_hash(const SpanSet *ss);
extern uint64 spanset_hash_extended(const SpanSet *ss, uint64 seed);
extern bool spanset_lower_inc(const SpanSet *ss);
extern int spanset_num_spans(const SpanSet *ss);
extern Span *spanset_span(const SpanSet *ss);
extern Span *spanset_span_n(const SpanSet *ss, int i);
extern Span **spanset_spans(const SpanSet *ss);
extern Span *spanset_start_span(const SpanSet *ss);
extern bool spanset_upper_inc(const SpanSet *ss);
extern text *textset_end_value(const Set *s);
extern text *textset_start_value(const Set *s);
extern bool textset_value_n(const Set *s, int n, text **result);
extern text **textset_values(const Set *s);
extern TimestampTz tstzset_end_value(const Set *s);
extern TimestampTz tstzset_start_value(const Set *s);
extern bool tstzset_value_n(const Set *s, int n, TimestampTz *result);
extern TimestampTz *tstzset_values(const Set *s);
extern Interval *tstzspan_duration(const Span *s);
extern TimestampTz tstzspan_lower(const Span *s);
extern TimestampTz tstzspan_upper(const Span *s);
extern Interval *tstzspanset_duration(const SpanSet *ss, bool boundspan);
extern TimestampTz tstzspanset_end_timestamptz(const SpanSet *ss);
extern TimestampTz tstzspanset_lower(const SpanSet *ss);
extern int tstzspanset_num_timestamps(const SpanSet *ss);
extern TimestampTz tstzspanset_start_timestamptz(const SpanSet *ss);
extern bool tstzspanset_timestamptz_n(const SpanSet *ss, int n, TimestampTz *result);
extern TimestampTz *tstzspanset_timestamps(const SpanSet *ss, int *count);
extern TimestampTz tstzspanset_upper(const SpanSet *ss);

extern Set *bigintset_shift_scale(const Set *s, int64 shift, int64 width, bool hasshift, bool haswidth);
extern Span *bigintspan_shift_scale(const Span *s, int64 shift, int64 width, bool hasshift, bool haswidth);
extern SpanSet *bigintspanset_shift_scale(const SpanSet *ss, int64 shift, int64 width, bool hasshift, bool haswidth);
extern Set *dateset_shift_scale(const Set *s, int shift, int width, bool hasshift, bool haswidth);
extern Span *datespan_shift_scale(const Span *s, int shift, int width, bool hasshift, bool haswidth);
extern SpanSet *datespanset_shift_scale(const SpanSet *ss, int shift, int width, bool hasshift, bool haswidth);
extern Set *floatset_degrees(const Set *s, bool normalize);
extern Set *floatset_radians(const Set *s);
extern Set *floatset_round(const Set *s, int maxdd);
extern Set *floatset_shift_scale(const Set *s, double shift, double width, bool hasshift, bool haswidth);
extern Span *floatspan_round(const Span *s, int maxdd);
extern Span *floatspan_shift_scale(const Span *s, double shift, double width, bool hasshift, bool haswidth);
extern SpanSet *floatspanset_round(const SpanSet *ss, int maxdd);
extern SpanSet *floatspanset_shift_scale(const SpanSet *ss, double shift, double width, bool hasshift, bool haswidth);
extern Set *geoset_round(const Set *s, int maxdd);
extern Set *geoset_set_srid(const Set *s, int32 srid);
extern Set *geoset_transform(const Set *s, int32 srid);
extern Set *geoset_transform_pipeline(const Set *s, char *pipelinestr, int32 srid, bool is_forward);
extern GSERIALIZED *point_transform(const GSERIALIZED *gs, int32 srid);
extern GSERIALIZED *point_transform_pipeline(const GSERIALIZED *gs, char *pipelinestr, int32 srid, bool is_forward);
extern Set *intset_shift_scale(const Set *s, int shift, int width, bool hasshift, bool haswidth);
extern Span *intspan_shift_scale(const Span *s, int shift, int width, bool hasshift, bool haswidth);
extern SpanSet *intspanset_shift_scale(const SpanSet *ss, int shift, int width, bool hasshift, bool haswidth);
extern Set *textset_initcap(const Set *s);
extern Set *textset_lower(const Set *s);
extern Set *textset_upper(const Set *s);
extern Set *textcat_textset_text(const Set *s, const text *txt);
extern Set *textcat_text_textset(const text *txt, const Set *s);
extern TimestampTz timestamptz_tprecision(TimestampTz t, const Interval *duration, TimestampTz torigin);
extern Set *tstzset_shift_scale(const Set *s, const Interval *shift, const Interval *duration);
extern Set *tstzset_tprecision(const Set *s, const Interval *duration, TimestampTz torigin);
extern Span *tstzspan_shift_scale(const Span *s, const Interval *shift, const Interval *duration);
extern Span *tstzspan_tprecision(const Span *s, const Interval *duration, TimestampTz torigin);
extern SpanSet *tstzspanset_shift_scale(const SpanSet *ss, const Interval *shift, const Interval *duration);
extern SpanSet *tstzspanset_tprecision(const SpanSet *ss, const Interval *duration, TimestampTz torigin);

extern int set_cmp(const Set *s1, const Set *s2);
extern bool set_eq(const Set *s1, const Set *s2);
extern bool set_ge(const Set *s1, const Set *s2);
extern bool set_gt(const Set *s1, const Set *s2);
extern bool set_le(const Set *s1, const Set *s2);
extern bool set_lt(const Set *s1, const Set *s2);
extern bool set_ne(const Set *s1, const Set *s2);
extern int span_cmp(const Span *s1, const Span *s2);
extern bool span_eq(const Span *s1, const Span *s2);
extern bool span_ge(const Span *s1, const Span *s2);
extern bool span_gt(const Span *s1, const Span *s2);
extern bool span_le(const Span *s1, const Span *s2);
extern bool span_lt(const Span *s1, const Span *s2);
extern bool span_ne(const Span *s1, const Span *s2);
extern int spanset_cmp(const SpanSet *ss1, const SpanSet *ss2);
extern bool spanset_eq(const SpanSet *ss1, const SpanSet *ss2);
extern bool spanset_ge(const SpanSet *ss1, const SpanSet *ss2);
extern bool spanset_gt(const SpanSet *ss1, const SpanSet *ss2);
extern bool spanset_le(const SpanSet *ss1, const SpanSet *ss2);
extern bool spanset_lt(const SpanSet *ss1, const SpanSet *ss2);
extern bool spanset_ne(const SpanSet *ss1, const SpanSet *ss2);

extern bool adjacent_span_bigint(const Span *s, int64 i);
extern bool adjacent_span_date(const Span *s, DateADT d);
extern bool adjacent_span_float(const Span *s, double d);
extern bool adjacent_span_int(const Span *s, int i);
extern bool adjacent_span_span(const Span *s1, const Span *s2);
extern bool adjacent_span_spanset(const Span *s, const SpanSet *ss);
extern bool adjacent_span_timestamptz(const Span *s, TimestampTz t);
extern bool adjacent_spanset_bigint(const SpanSet *ss, int64 i);
extern bool adjacent_spanset_date(const SpanSet *ss, DateADT d);
extern bool adjacent_spanset_float(const SpanSet *ss, double d);
extern bool adjacent_spanset_int(const SpanSet *ss, int i);
extern bool adjacent_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern bool adjacent_spanset_span(const SpanSet *ss, const Span *s);
extern bool adjacent_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern bool contained_bigint_set(int64 i, const Set *s);
extern bool contained_bigint_span(int64 i, const Span *s);
extern bool contained_bigint_spanset(int64 i, const SpanSet *ss);
extern bool contained_date_set(DateADT d, const Set *s);
extern bool contained_date_span(DateADT d, const Span *s);
extern bool contained_date_spanset(DateADT d, const SpanSet *ss);
extern bool contained_float_set(double d, const Set *s);
extern bool contained_float_span(double d, const Span *s);
extern bool contained_float_spanset(double d, const SpanSet *ss);
extern bool contained_geo_set(GSERIALIZED *gs, const Set *s);
extern bool contained_int_set(int i, const Set *s);
extern bool contained_int_span(int i, const Span *s);
extern bool contained_int_spanset(int i, const SpanSet *ss);
extern bool contained_set_set(const Set *s1, const Set *s2);
extern bool contained_span_span(const Span *s1, const Span *s2);
extern bool contained_span_spanset(const Span *s, const SpanSet *ss);
extern bool contained_spanset_span(const SpanSet *ss, const Span *s);
extern bool contained_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern bool contained_text_set(text *txt, const Set *s);
extern bool contained_timestamptz_set(TimestampTz t, const Set *s);
extern bool contained_timestamptz_span(TimestampTz t, const Span *s);
extern bool contained_timestamptz_spanset(TimestampTz t, const SpanSet *ss);
extern bool contains_set_bigint(const Set *s, int64 i);
extern bool contains_set_date(const Set *s, DateADT d);
extern bool contains_set_float(const Set *s, double d);
extern bool contains_set_geo(const Set *s, GSERIALIZED *gs);
extern bool contains_set_int(const Set *s, int i);
extern bool contains_set_set(const Set *s1, const Set *s2);
extern bool contains_set_text(const Set *s, text *t);
extern bool contains_set_timestamptz(const Set *s, TimestampTz t);
extern bool contains_span_bigint(const Span *s, int64 i);
extern bool contains_span_date(const Span *s, DateADT d);
extern bool contains_span_float(const Span *s, double d);
extern bool contains_span_int(const Span *s, int i);
extern bool contains_span_span(const Span *s1, const Span *s2);
extern bool contains_span_spanset(const Span *s, const SpanSet *ss);
extern bool contains_span_timestamptz(const Span *s, TimestampTz t);
extern bool contains_spanset_bigint(const SpanSet *ss, int64 i);
extern bool contains_spanset_date(const SpanSet *ss, DateADT d);
extern bool contains_spanset_float(const SpanSet *ss, double d);
extern bool contains_spanset_int(const SpanSet *ss, int i);
extern bool contains_spanset_span(const SpanSet *ss, const Span *s);
extern bool contains_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern bool contains_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern bool overlaps_set_set(const Set *s1, const Set *s2);
extern bool overlaps_span_span(const Span *s1, const Span *s2);
extern bool overlaps_span_spanset(const Span *s, const SpanSet *ss);
extern bool overlaps_spanset_span(const SpanSet *ss, const Span *s);
extern bool overlaps_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);

extern bool after_date_set(DateADT d, const Set *s);
extern bool after_date_span(DateADT d, const Span *s);
extern bool after_date_spanset(DateADT d, const SpanSet *ss);
extern bool after_set_date(const Set *s, DateADT d);
extern bool after_set_timestamptz(const Set *s, TimestampTz t);
extern bool after_span_date(const Span *s, DateADT d);
extern bool after_span_timestamptz(const Span *s, TimestampTz t);
extern bool after_spanset_date(const SpanSet *ss, DateADT d);
extern bool after_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern bool after_timestamptz_set(TimestampTz t, const Set *s);
extern bool after_timestamptz_span(TimestampTz t, const Span *s);
extern bool after_timestamptz_spanset(TimestampTz t, const SpanSet *ss);
extern bool before_date_set(DateADT d, const Set *s);
extern bool before_date_span(DateADT d, const Span *s);
extern bool before_date_spanset(DateADT d, const SpanSet *ss);
extern bool before_set_date(const Set *s, DateADT d);
extern bool before_set_timestamptz(const Set *s, TimestampTz t);
extern bool before_span_date(const Span *s, DateADT d);
extern bool before_span_timestamptz(const Span *s, TimestampTz t);
extern bool before_spanset_date(const SpanSet *ss, DateADT d);
extern bool before_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern bool before_timestamptz_set(TimestampTz t, const Set *s);
extern bool before_timestamptz_span(TimestampTz t, const Span *s);
extern bool before_timestamptz_spanset(TimestampTz t, const SpanSet *ss);
extern bool left_bigint_set(int64 i, const Set *s);
extern bool left_bigint_span(int64 i, const Span *s);
extern bool left_bigint_spanset(int64 i, const SpanSet *ss);
extern bool left_float_set(double d, const Set *s);
extern bool left_float_span(double d, const Span *s);
extern bool left_float_spanset(double d, const SpanSet *ss);
extern bool left_int_set(int i, const Set *s);
extern bool left_int_span(int i, const Span *s);
extern bool left_int_spanset(int i, const SpanSet *ss);
extern bool left_set_bigint(const Set *s, int64 i);
extern bool left_set_float(const Set *s, double d);
extern bool left_set_int(const Set *s, int i);
extern bool left_set_set(const Set *s1, const Set *s2);
extern bool left_set_text(const Set *s, text *txt);
extern bool left_span_bigint(const Span *s, int64 i);
extern bool left_span_float(const Span *s, double d);
extern bool left_span_int(const Span *s, int i);
extern bool left_span_span(const Span *s1, const Span *s2);
extern bool left_span_spanset(const Span *s, const SpanSet *ss);
extern bool left_spanset_bigint(const SpanSet *ss, int64 i);
extern bool left_spanset_float(const SpanSet *ss, double d);
extern bool left_spanset_int(const SpanSet *ss, int i);
extern bool left_spanset_span(const SpanSet *ss, const Span *s);
extern bool left_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern bool left_text_set(text *txt, const Set *s);
extern bool overafter_date_set(DateADT d, const Set *s);
extern bool overafter_date_span(DateADT d, const Span *s);
extern bool overafter_date_spanset(DateADT d, const SpanSet *ss);
extern bool overafter_set_date(const Set *s, DateADT d);
extern bool overafter_set_timestamptz(const Set *s, TimestampTz t);
extern bool overafter_span_date(const Span *s, DateADT d);
extern bool overafter_span_timestamptz(const Span *s, TimestampTz t);
extern bool overafter_spanset_date(const SpanSet *ss, DateADT d);
extern bool overafter_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern bool overafter_timestamptz_set(TimestampTz t, const Set *s);
extern bool overafter_timestamptz_span(TimestampTz t, const Span *s);
extern bool overafter_timestamptz_spanset(TimestampTz t, const SpanSet *ss);
extern bool overbefore_date_set(DateADT d, const Set *s);
extern bool overbefore_date_span(DateADT d, const Span *s);
extern bool overbefore_date_spanset(DateADT d, const SpanSet *ss);
extern bool overbefore_set_date(const Set *s, DateADT d);
extern bool overbefore_set_timestamptz(const Set *s, TimestampTz t);
extern bool overbefore_span_date(const Span *s, DateADT d);
extern bool overbefore_span_timestamptz(const Span *s, TimestampTz t);
extern bool overbefore_spanset_date(const SpanSet *ss, DateADT d);
extern bool overbefore_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern bool overbefore_timestamptz_set(TimestampTz t, const Set *s);
extern bool overbefore_timestamptz_span(TimestampTz t, const Span *s);
extern bool overbefore_timestamptz_spanset(TimestampTz t, const SpanSet *ss);
extern bool overleft_bigint_set(int64 i, const Set *s);
extern bool overleft_bigint_span(int64 i, const Span *s);
extern bool overleft_bigint_spanset(int64 i, const SpanSet *ss);
extern bool overleft_float_set(double d, const Set *s);
extern bool overleft_float_span(double d, const Span *s);
extern bool overleft_float_spanset(double d, const SpanSet *ss);
extern bool overleft_int_set(int i, const Set *s);
extern bool overleft_int_span(int i, const Span *s);
extern bool overleft_int_spanset(int i, const SpanSet *ss);
extern bool overleft_set_bigint(const Set *s, int64 i);
extern bool overleft_set_float(const Set *s, double d);
extern bool overleft_set_int(const Set *s, int i);
extern bool overleft_set_set(const Set *s1, const Set *s2);
extern bool overleft_set_text(const Set *s, text *txt);
extern bool overleft_span_bigint(const Span *s, int64 i);
extern bool overleft_span_float(const Span *s, double d);
extern bool overleft_span_int(const Span *s, int i);
extern bool overleft_span_span(const Span *s1, const Span *s2);
extern bool overleft_span_spanset(const Span *s, const SpanSet *ss);
extern bool overleft_spanset_bigint(const SpanSet *ss, int64 i);
extern bool overleft_spanset_float(const SpanSet *ss, double d);
extern bool overleft_spanset_int(const SpanSet *ss, int i);
extern bool overleft_spanset_span(const SpanSet *ss, const Span *s);
extern bool overleft_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern bool overleft_text_set(text *txt, const Set *s);
extern bool overright_bigint_set(int64 i, const Set *s);
extern bool overright_bigint_span(int64 i, const Span *s);
extern bool overright_bigint_spanset(int64 i, const SpanSet *ss);
extern bool overright_float_set(double d, const Set *s);
extern bool overright_float_span(double d, const Span *s);
extern bool overright_float_spanset(double d, const SpanSet *ss);
extern bool overright_int_set(int i, const Set *s);
extern bool overright_int_span(int i, const Span *s);
extern bool overright_int_spanset(int i, const SpanSet *ss);
extern bool overright_set_bigint(const Set *s, int64 i);
extern bool overright_set_float(const Set *s, double d);
extern bool overright_set_int(const Set *s, int i);
extern bool overright_set_set(const Set *s1, const Set *s2);
extern bool overright_set_text(const Set *s, text *txt);
extern bool overright_span_bigint(const Span *s, int64 i);
extern bool overright_span_float(const Span *s, double d);
extern bool overright_span_int(const Span *s, int i);
extern bool overright_span_span(const Span *s1, const Span *s2);
extern bool overright_span_spanset(const Span *s, const SpanSet *ss);
extern bool overright_spanset_bigint(const SpanSet *ss, int64 i);
extern bool overright_spanset_float(const SpanSet *ss, double d);
extern bool overright_spanset_int(const SpanSet *ss, int i);
extern bool overright_spanset_span(const SpanSet *ss, const Span *s);
extern bool overright_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern bool overright_text_set(text *txt, const Set *s);
extern bool right_bigint_set(int64 i, const Set *s);
extern bool right_bigint_span(int64 i, const Span *s);
extern bool right_bigint_spanset(int64 i, const SpanSet *ss);
extern bool right_float_set(double d, const Set *s);
extern bool right_float_span(double d, const Span *s);
extern bool right_float_spanset(double d, const SpanSet *ss);
extern bool right_int_set(int i, const Set *s);
extern bool right_int_span(int i, const Span *s);
extern bool right_int_spanset(int i, const SpanSet *ss);
extern bool right_set_bigint(const Set *s, int64 i);
extern bool right_set_float(const Set *s, double d);
extern bool right_set_int(const Set *s, int i);
extern bool right_set_set(const Set *s1, const Set *s2);
extern bool right_set_text(const Set *s, text *txt);
extern bool right_span_bigint(const Span *s, int64 i);
extern bool right_span_float(const Span *s, double d);
extern bool right_span_int(const Span *s, int i);
extern bool right_span_span(const Span *s1, const Span *s2);
extern bool right_span_spanset(const Span *s, const SpanSet *ss);
extern bool right_spanset_bigint(const SpanSet *ss, int64 i);
extern bool right_spanset_float(const SpanSet *ss, double d);
extern bool right_spanset_int(const SpanSet *ss, int i);
extern bool right_spanset_span(const SpanSet *ss, const Span *s);
extern bool right_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern bool right_text_set(text *txt, const Set *s);

extern Set *intersection_bigint_set(int64 i, const Set *s);
extern Set *intersection_date_set(const DateADT d, const Set *s);
extern Set *intersection_float_set(double d, const Set *s);
extern Set *intersection_geo_set(const GSERIALIZED *gs, const Set *s);
extern Set *intersection_int_set(int i, const Set *s);
extern Set *intersection_set_bigint(const Set *s, int64 i);
extern Set *intersection_set_date(const Set *s, DateADT d);
extern Set *intersection_set_float(const Set *s, double d);
extern Set *intersection_set_geo(const Set *s, const GSERIALIZED *gs);
extern Set *intersection_set_int(const Set *s, int i);
extern Set *intersection_set_set(const Set *s1, const Set *s2);
extern Set *intersection_set_text(const Set *s, const text *txt);
extern Set *intersection_set_timestamptz(const Set *s, TimestampTz t);
extern Span *intersection_span_bigint(const Span *s, int64 i);
extern Span *intersection_span_date(const Span *s, DateADT d);
extern Span *intersection_span_float(const Span *s, double d);
extern Span *intersection_span_int(const Span *s, int i);
extern Span *intersection_span_span(const Span *s1, const Span *s2);
extern SpanSet *intersection_span_spanset(const Span *s, const SpanSet *ss);
extern Span *intersection_span_timestamptz(const Span *s, TimestampTz t);
extern SpanSet *intersection_spanset_bigint(const SpanSet *ss, int64 i);
extern SpanSet *intersection_spanset_date(const SpanSet *ss, DateADT d);
extern SpanSet *intersection_spanset_float(const SpanSet *ss, double d);
extern SpanSet *intersection_spanset_int(const SpanSet *ss, int i);
extern SpanSet *intersection_spanset_span(const SpanSet *ss, const Span *s);
extern SpanSet *intersection_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern SpanSet *intersection_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern Set *intersection_text_set(const text *txt, const Set *s);
extern Set *intersection_timestamptz_set(const TimestampTz t, const Set *s);
extern Set *minus_bigint_set(int64 i, const Set *s);
extern SpanSet *minus_bigint_span(int64 i, const Span *s);
extern SpanSet *minus_bigint_spanset(int64 i, const SpanSet *ss);
extern Set *minus_date_set(DateADT d, const Set *s);
extern SpanSet *minus_date_span(DateADT d, const Span *s);
extern SpanSet *minus_date_spanset(DateADT d, const SpanSet *ss);
extern Set *minus_float_set(double d, const Set *s);
extern SpanSet *minus_float_span(double d, const Span *s);
extern SpanSet *minus_float_spanset(double d, const SpanSet *ss);
extern Set *minus_geo_set(const GSERIALIZED *gs, const Set *s);
extern Set *minus_int_set(int i, const Set *s);
extern SpanSet *minus_int_span(int i, const Span *s);
extern SpanSet *minus_int_spanset(int i, const SpanSet *ss);
extern Set *minus_set_bigint(const Set *s, int64 i);
extern Set *minus_set_date(const Set *s, DateADT d);
extern Set *minus_set_float(const Set *s, double d);
extern Set *minus_set_geo(const Set *s, const GSERIALIZED *gs);
extern Set *minus_set_int(const Set *s, int i);
extern Set *minus_set_set(const Set *s1, const Set *s2);
extern Set *minus_set_text(const Set *s, const text *txt);
extern Set *minus_set_timestamptz(const Set *s, TimestampTz t);
extern SpanSet *minus_span_bigint(const Span *s, int64 i);
extern SpanSet *minus_span_date(const Span *s, DateADT d);
extern SpanSet *minus_span_float(const Span *s, double d);
extern SpanSet *minus_span_int(const Span *s, int i);
extern SpanSet *minus_span_span(const Span *s1, const Span *s2);
extern SpanSet *minus_span_spanset(const Span *s, const SpanSet *ss);
extern SpanSet *minus_span_timestamptz(const Span *s, TimestampTz t);
extern SpanSet *minus_spanset_bigint(const SpanSet *ss, int64 i);
extern SpanSet *minus_spanset_date(const SpanSet *ss, DateADT d);
extern SpanSet *minus_spanset_float(const SpanSet *ss, double d);
extern SpanSet *minus_spanset_int(const SpanSet *ss, int i);
extern SpanSet *minus_spanset_span(const SpanSet *ss, const Span *s);
extern SpanSet *minus_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern SpanSet *minus_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern Set *minus_text_set(const text *txt, const Set *s);
extern Set *minus_timestamptz_set(TimestampTz t, const Set *s);
extern SpanSet *minus_timestamptz_span(TimestampTz t, const Span *s);
extern SpanSet *minus_timestamptz_spanset(TimestampTz t, const SpanSet *ss);
extern Set *union_bigint_set(int64 i, const Set *s);
extern SpanSet *union_bigint_span(const Span *s, int64 i);
extern SpanSet *union_bigint_spanset(int64 i, SpanSet *ss);
extern Set *union_date_set(const DateADT d, const Set *s);
extern SpanSet *union_date_span(const Span *s, DateADT d);
extern SpanSet *union_date_spanset(DateADT d, SpanSet *ss);
extern Set *union_float_set(double d, const Set *s);
extern SpanSet *union_float_span(const Span *s, double d);
extern SpanSet *union_float_spanset(double d, SpanSet *ss);
extern Set *union_geo_set(const GSERIALIZED *gs, const Set *s);
extern Set *union_int_set(int i, const Set *s);
extern SpanSet *union_int_span(int i, const Span *s);
extern SpanSet *union_int_spanset(int i, SpanSet *ss);
extern Set *union_set_bigint(const Set *s, int64 i);
extern Set *union_set_date(const Set *s, DateADT d);
extern Set *union_set_float(const Set *s, double d);
extern Set *union_set_geo(const Set *s, const GSERIALIZED *gs);
extern Set *union_set_int(const Set *s, int i);
extern Set *union_set_set(const Set *s1, const Set *s2);
extern Set *union_set_text(const Set *s, const text *txt);
extern Set *union_set_timestamptz(const Set *s, const TimestampTz t);
extern SpanSet *union_span_bigint(const Span *s, int64 i);
extern SpanSet *union_span_date(const Span *s, DateADT d);
extern SpanSet *union_span_float(const Span *s, double d);
extern SpanSet *union_span_int(const Span *s, int i);
extern SpanSet *union_span_span(const Span *s1, const Span *s2);
extern SpanSet *union_span_spanset(const Span *s, const SpanSet *ss);
extern SpanSet *union_span_timestamptz(const Span *s, TimestampTz t);
extern SpanSet *union_spanset_bigint(const SpanSet *ss, int64 i);
extern SpanSet *union_spanset_date(const SpanSet *ss, DateADT d);
extern SpanSet *union_spanset_float(const SpanSet *ss, double d);
extern SpanSet *union_spanset_int(const SpanSet *ss, int i);
extern SpanSet *union_spanset_span(const SpanSet *ss, const Span *s);
extern SpanSet *union_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern SpanSet *union_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern Set *union_text_set(const text *txt, const Set *s);
extern Set *union_timestamptz_set(const TimestampTz t, const Set *s);
extern SpanSet *union_timestamptz_span(TimestampTz t, const Span *s);
extern SpanSet *union_timestamptz_spanset(TimestampTz t, SpanSet *ss);

extern int64 distance_bigintset_bigintset(const Set *s1, const Set *s2);
extern int64 distance_bigintspan_bigintspan(const Span *s1, const Span *s2);
extern int64 distance_bigintspanset_bigintspan(const SpanSet *ss, const Span *s);
extern int64 distance_bigintspanset_bigintspanset(const SpanSet *ss1, const SpanSet *ss2);
extern int distance_dateset_dateset(const Set *s1, const Set *s2);
extern int distance_datespan_datespan(const Span *s1, const Span *s2);
extern int distance_datespanset_datespan(const SpanSet *ss, const Span *s);
extern int distance_datespanset_datespanset(const SpanSet *ss1, const SpanSet *ss2);
extern double distance_floatset_floatset(const Set *s1, const Set *s2);
extern double distance_floatspan_floatspan(const Span *s1, const Span *s2);
extern double distance_floatspanset_floatspan(const SpanSet *ss, const Span *s);
extern double distance_floatspanset_floatspanset(const SpanSet *ss1, const SpanSet *ss2);
extern int distance_intset_intset(const Set *s1, const Set *s2);
extern int distance_intspan_intspan(const Span *s1, const Span *s2);
extern int distance_intspanset_intspan(const SpanSet *ss, const Span *s);
extern int distance_intspanset_intspanset(const SpanSet *ss1, const SpanSet *ss2);
extern int64 distance_set_bigint(const Set *s, int64 i);
extern int distance_set_date(const Set *s, DateADT d);
extern double distance_set_float(const Set *s, double d);
extern int distance_set_int(const Set *s, int i);
extern double distance_set_timestamptz(const Set *s, TimestampTz t);
extern int64 distance_span_bigint(const Span *s, int64 i);
extern int distance_span_date(const Span *s, DateADT d);
extern double distance_span_float(const Span *s, double d);
extern int distance_span_int(const Span *s, int i);
extern double distance_span_timestamptz(const Span *s, TimestampTz t);
extern int64 distance_spanset_bigint(const SpanSet *ss, int64 i);
extern int distance_spanset_date(const SpanSet *ss, DateADT d);
extern double distance_spanset_float(const SpanSet *ss, double d);
extern int distance_spanset_int(const SpanSet *ss, int i);
extern double distance_spanset_timestamptz(const SpanSet *ss, TimestampTz t);
extern double distance_tstzset_tstzset(const Set *s1, const Set *s2);
extern double distance_tstzspan_tstzspan(const Span *s1, const Span *s2);
extern double distance_tstzspanset_tstzspan(const SpanSet *ss, const Span *s);
extern double distance_tstzspanset_tstzspanset(const SpanSet *ss1, const SpanSet *ss2);

extern Span *bigint_extent_transfn(Span *state, int64 i);
extern Set *bigint_union_transfn(Set *state, int64 i);
extern Span *date_extent_transfn(Span *state, DateADT d);
extern Set *date_union_transfn(Set *state, DateADT d);
extern Span *float_extent_transfn(Span *state, double d);
extern Set *float_union_transfn(Set *state, double d);
extern Span *int_extent_transfn(Span *state, int i);
extern Set *int_union_transfn(Set *state, int32 i);
extern Span *set_extent_transfn(Span *state, const Set *s);
extern Set *set_union_finalfn(Set *state);
extern Set *set_union_transfn(Set *state, Set *s);
extern Span *span_extent_transfn(Span *state, const Span *s);
extern SpanSet *span_union_transfn(SpanSet *state, const Span *s);
extern Span *spanset_extent_transfn(Span *state, const SpanSet *ss);
extern SpanSet *spanset_union_finalfn(SpanSet *state);
extern SpanSet *spanset_union_transfn(SpanSet *state, const SpanSet *ss);
extern Set *text_union_transfn(Set *state, const text *txt);
extern Span *timestamptz_extent_transfn(Span *state, TimestampTz t);
extern Set *timestamptz_union_transfn(Set *state, TimestampTz t);

extern TBox *tbox_in(const char *str);
extern char *tbox_out(const TBox *box, int maxdd);
extern TBox *tbox_from_wkb(const uint8_t *wkb, size_t size);
extern TBox *tbox_from_hexwkb(const char *hexwkb);
extern STBox *stbox_from_wkb(const uint8_t *wkb, size_t size);
extern STBox *stbox_from_hexwkb(const char *hexwkb);
extern uint8_t *tbox_as_wkb(const TBox *box, uint8_t variant, size_t *size_out);
extern char *tbox_as_hexwkb(const TBox *box, uint8_t variant, size_t *size);
extern uint8_t *stbox_as_wkb(const STBox *box, uint8_t variant, size_t *size_out);
extern char *stbox_as_hexwkb(const STBox *box, uint8_t variant, size_t *size);
extern STBox *stbox_in(const char *str);
extern char *stbox_out(const STBox *box, int maxdd);

extern TBox *float_tstzspan_to_tbox(double d, const Span *s);
extern TBox *float_timestamptz_to_tbox(double d, TimestampTz t);
extern STBox *geo_tstzspan_to_stbox(const GSERIALIZED *gs, const Span *s);
extern STBox *geo_timestamptz_to_stbox(const GSERIALIZED *gs, TimestampTz t);
extern TBox *int_tstzspan_to_tbox(int i, const Span *s);
extern TBox *int_timestamptz_to_tbox(int i, TimestampTz t);
extern TBox *numspan_tstzspan_to_tbox(const Span *span, const Span *s);
extern TBox *numspan_timestamptz_to_tbox(const Span *span, TimestampTz t);
extern STBox *stbox_copy(const STBox *box);
extern STBox *stbox_make(bool hasx, bool hasz, bool geodetic, int32 srid, double xmin, double xmax, double ymin, double ymax, double zmin, double zmax, const Span *s);
extern TBox *tbox_copy(const TBox *box);
extern TBox *tbox_make(const Span *s, const Span *p);

extern TBox *float_to_tbox(double d);
extern STBox *geo_to_stbox(const GSERIALIZED *gs);
extern TBox *int_to_tbox(int i);
extern TBox *set_to_tbox(const Set *s);
extern TBox *span_to_tbox(const Span *s);
extern TBox *spanset_to_tbox(const SpanSet *ss);
extern STBox *spatialset_to_stbox(const Set *s);
extern GBOX *stbox_to_gbox(const STBox *box);
extern BOX3D *stbox_to_box3d(const STBox *box);
extern GSERIALIZED *stbox_to_geo(const STBox *box);
extern Span *stbox_to_tstzspan(const STBox *box);
extern Span *tbox_to_intspan(const TBox *box);
extern Span *tbox_to_floatspan(const TBox *box);
extern Span *tbox_to_tstzspan(const TBox *box);
extern STBox *timestamptz_to_stbox(TimestampTz t);
extern TBox *timestamptz_to_tbox(TimestampTz t);
extern STBox *tstzset_to_stbox(const Set *s);
extern STBox *tstzspan_to_stbox(const Span *s);
extern STBox *tstzspanset_to_stbox(const SpanSet *ss);
extern TBox *tnumber_to_tbox(const Temporal *temp);
extern STBox *tpoint_to_stbox(const Temporal *temp);

extern bool stbox_hast(const STBox *box);
extern bool stbox_hasx(const STBox *box);
extern bool stbox_hasz(const STBox *box);
extern bool stbox_isgeodetic(const STBox *box);
extern int32 stbox_srid(const STBox *box);
extern bool stbox_tmax(const STBox *box, TimestampTz *result);
extern bool stbox_tmax_inc(const STBox *box, bool *result);
extern bool stbox_tmin(const STBox *box, TimestampTz *result);
extern bool stbox_tmin_inc(const STBox *box, bool *result);
extern bool stbox_xmax(const STBox *box, double *result);
extern bool stbox_xmin(const STBox *box, double *result);
extern bool stbox_ymax(const STBox *box, double *result);
extern bool stbox_ymin(const STBox *box, double *result);
extern bool stbox_zmax(const STBox *box, double *result);
extern bool stbox_zmin(const STBox *box, double *result);
extern bool tbox_hast(const TBox *box);
extern bool tbox_hasx(const TBox *box);
extern bool tbox_tmax(const TBox *box, TimestampTz *result);
extern bool tbox_tmax_inc(const TBox *box, bool *result);
extern bool tbox_tmin(const TBox *box, TimestampTz *result);
extern bool tbox_tmin_inc(const TBox *box, bool *result);
extern bool tbox_xmax(const TBox *box, double *result);
extern bool tbox_xmax_inc(const TBox *box, bool *result);
extern bool tbox_xmin(const TBox *box, double *result);
extern bool tbox_xmin_inc(const TBox *box, bool *result);
extern bool tboxfloat_xmax(const TBox *box, double *result);
extern bool tboxfloat_xmin(const TBox *box, double *result);
extern bool tboxint_xmax(const TBox *box, int *result);
extern bool tboxint_xmin(const TBox *box, int *result);

extern STBox *stbox_expand_space(const STBox *box, double d);
extern STBox *stbox_expand_time(const STBox *box, const Interval *interv);
extern STBox *stbox_get_space(const STBox *box);
extern STBox *stbox_quad_split(const STBox *box, int *count);
extern STBox *stbox_round(const STBox *box, int maxdd);
extern STBox *stbox_set_srid(const STBox *box, int32 srid);
extern STBox *stbox_shift_scale_time(const STBox *box, const Interval *shift, const Interval *duration);
extern STBox *stbox_transform(const STBox *box, int32 srid);
extern STBox *stbox_transform_pipeline(const STBox *box, char *pipelinestr, int32 srid, bool is_forward);
extern TBox *tbox_expand_time(const TBox *box, const Interval *interv);
extern TBox *tbox_expand_float(const TBox *box, const double d);
extern TBox *tbox_expand_int(const TBox *box, const int i);
extern TBox *tbox_round(const TBox *box, int maxdd);
extern TBox *tbox_shift_scale_float(const TBox *box, double shift, double width, bool hasshift, bool haswidth);
extern TBox *tbox_shift_scale_int(const TBox *box, int shift, int width, bool hasshift, bool haswidth);
extern TBox *tbox_shift_scale_time(const TBox *box, const Interval *shift, const Interval *duration);

extern TBox *union_tbox_tbox(const TBox *box1, const TBox *box2, bool strict);
extern TBox *intersection_tbox_tbox(const TBox *box1, const TBox *box2);
extern STBox *union_stbox_stbox(const STBox *box1, const STBox *box2, bool strict);
extern STBox *intersection_stbox_stbox(const STBox *box1, const STBox *box2);

extern bool adjacent_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool adjacent_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool contained_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool contained_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool contains_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool contains_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool overlaps_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool overlaps_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool same_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool same_stbox_stbox(const STBox *box1, const STBox *box2);

extern bool left_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool overleft_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool right_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool overright_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool before_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool overbefore_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool after_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool overafter_tbox_tbox(const TBox *box1, const TBox *box2);
extern bool left_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overleft_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool right_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overright_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool below_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overbelow_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool above_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overabove_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool front_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overfront_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool back_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overback_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool before_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overbefore_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool after_stbox_stbox(const STBox *box1, const STBox *box2);
extern bool overafter_stbox_stbox(const STBox *box1, const STBox *box2);

extern bool tbox_eq(const TBox *box1, const TBox *box2);
extern bool tbox_ne(const TBox *box1, const TBox *box2);
extern int tbox_cmp(const TBox *box1, const TBox *box2);
extern bool tbox_lt(const TBox *box1, const TBox *box2);
extern bool tbox_le(const TBox *box1, const TBox *box2);
extern bool tbox_ge(const TBox *box1, const TBox *box2);
extern bool tbox_gt(const TBox *box1, const TBox *box2);
extern bool stbox_eq(const STBox *box1, const STBox *box2);
extern bool stbox_ne(const STBox *box1, const STBox *box2);
extern int stbox_cmp(const STBox *box1, const STBox *box2);
extern bool stbox_lt(const STBox *box1, const STBox *box2);
extern bool stbox_le(const STBox *box1, const STBox *box2);
extern bool stbox_ge(const STBox *box1, const STBox *box2);
extern bool stbox_gt(const STBox *box1, const STBox *box2);

extern Temporal *tbool_in(const char *str);
extern Temporal *tint_in(const char *str);
extern Temporal *tfloat_in(const char *str);
extern Temporal *ttext_in(const char *str);
extern Temporal *tgeompoint_in(const char *str);
extern Temporal *tgeogpoint_in(const char *str);
extern Temporal *tbool_from_mfjson(const char *str);
extern Temporal *tint_from_mfjson(const char *str);
extern Temporal *tfloat_from_mfjson(const char *str);
extern Temporal *ttext_from_mfjson(const char *str);
extern Temporal *tgeompoint_from_mfjson(const char *str);
extern Temporal *tgeogpoint_from_mfjson(const char *str);
extern Temporal *temporal_from_wkb(const uint8_t *wkb, size_t size);
extern Temporal *temporal_from_hexwkb(const char *hexwkb);

extern char *tbool_out(const Temporal *temp);
extern char *tint_out(const Temporal *temp);
extern char *tfloat_out(const Temporal *temp, int maxdd);
extern char *ttext_out(const Temporal *temp);
extern char *tpoint_out(const Temporal *temp, int maxdd);
extern char *tpoint_as_text(const Temporal *temp, int maxdd);
extern char *tpoint_as_ewkt(const Temporal *temp, int maxdd);
extern char *temporal_as_mfjson(const Temporal *temp, bool with_bbox, int flags, int precision, char *srs);
extern uint8_t *temporal_as_wkb(const Temporal *temp, uint8_t variant, size_t *size_out);
extern char *temporal_as_hexwkb(const Temporal *temp, uint8_t variant, size_t *size_out);

extern Temporal *tbool_from_base_temp(bool b, const Temporal *temp);
extern TInstant *tboolinst_make(bool b, TimestampTz t);
extern TSequence *tboolseq_from_base_tstzset(bool b, const Set *s);
extern TSequence *tboolseq_from_base_tstzspan(bool b, const Span *s);
extern TSequenceSet *tboolseqset_from_base_tstzspanset(bool b, const SpanSet *ss);
extern Temporal *temporal_copy(const Temporal *temp);
extern Temporal *tfloat_from_base_temp(double d, const Temporal *temp);
extern TInstant *tfloatinst_make(double d, TimestampTz t);
extern TSequence *tfloatseq_from_base_tstzspan(double d, const Span *s, interpType interp);
extern TSequence *tfloatseq_from_base_tstzset(double d, const Set *s);
extern TSequenceSet *tfloatseqset_from_base_tstzspanset(double d, const SpanSet *ss, interpType interp);
extern Temporal *tint_from_base_temp(int i, const Temporal *temp);
extern TInstant *tintinst_make(int i, TimestampTz t);
extern TSequence *tintseq_from_base_tstzspan(int i, const Span *s);
extern TSequence *tintseq_from_base_tstzset(int i, const Set *s);
extern TSequenceSet *tintseqset_from_base_tstzspanset(int i, const SpanSet *ss);
extern Temporal *tpoint_from_base_temp(const GSERIALIZED *gs, const Temporal *temp);
extern TInstant *tpointinst_make(const GSERIALIZED *gs, TimestampTz t);
extern TSequence *tpointseq_from_base_tstzspan(const GSERIALIZED *gs, const Span *s, interpType interp);
extern TSequence *tpointseq_from_base_tstzset(const GSERIALIZED *gs, const Set *s);
extern TSequenceSet *tpointseqset_from_base_tstzspanset(const GSERIALIZED *gs, const SpanSet *ss, interpType interp);
extern TSequence *tsequence_make(const TInstant **instants, int count, bool lower_inc, bool upper_inc, interpType interp, bool normalize);
extern TSequenceSet *tsequenceset_make(const TSequence **sequences, int count, bool normalize);
extern TSequenceSet *tsequenceset_make_gaps(const TInstant **instants, int count, interpType interp, Interval *maxt, double maxdist);
extern Temporal *ttext_from_base_temp(const text *txt, const Temporal *temp);
extern TInstant *ttextinst_make(const text *txt, TimestampTz t);
extern TSequence *ttextseq_from_base_tstzspan(const text *txt, const Span *s);
extern TSequence *ttextseq_from_base_tstzset(const text *txt, const Set *s);
extern TSequenceSet *ttextseqset_from_base_tstzspanset(const text *txt, const SpanSet *ss);

extern Span *temporal_to_tstzspan(const Temporal *temp);
extern Temporal *tfloat_to_tint(const Temporal *temp);
extern Temporal *tint_to_tfloat(const Temporal *temp);
extern Span *tnumber_to_span(const Temporal *temp);

extern bool tbool_end_value(const Temporal *temp);
extern bool tbool_start_value(const Temporal *temp);
extern bool tbool_value_at_timestamptz(const Temporal *temp, TimestampTz t, bool strict, bool *value);
extern bool *tbool_values(const Temporal *temp, int *count);
extern Interval *temporal_duration(const Temporal *temp, bool boundspan);
extern TInstant *temporal_end_instant(const Temporal *temp);
extern TSequence *temporal_end_sequence(const Temporal *temp);
extern TimestampTz temporal_end_timestamptz(const Temporal *temp);
extern uint32 temporal_hash(const Temporal *temp);
extern TInstant *temporal_instant_n(const Temporal *temp, int n);
extern TInstant **temporal_instants(const Temporal *temp, int *count);
extern const char *temporal_interp(const Temporal *temp);
extern TInstant *temporal_max_instant(const Temporal *temp);
extern TInstant *temporal_min_instant(const Temporal *temp);
extern int temporal_num_instants(const Temporal *temp);
extern int temporal_num_sequences(const Temporal *temp);
extern int temporal_num_timestamps(const Temporal *temp);
extern TSequence **temporal_segments(const Temporal *temp, int *count);
extern TSequence *temporal_sequence_n(const Temporal *temp, int i);
extern TSequence **temporal_sequences(const Temporal *temp, int *count);
extern int temporal_lower_inc(const Temporal *temp);
extern int temporal_upper_inc(const Temporal *temp);
extern TInstant *temporal_start_instant(const Temporal *temp);
extern TSequence *temporal_start_sequence(const Temporal *temp);
extern TimestampTz temporal_start_timestamptz(const Temporal *temp);
extern TSequenceSet *temporal_stops(const Temporal *temp, double maxdist, const Interval *minduration);
extern const char *temporal_subtype(const Temporal *temp);
extern SpanSet *temporal_time(const Temporal *temp);
extern bool temporal_timestamptz_n(const Temporal *temp, int n, TimestampTz *result);
extern TimestampTz *temporal_timestamps(const Temporal *temp, int *count);
extern double tfloat_end_value(const Temporal *temp);
extern double tfloat_max_value(const Temporal *temp);
extern double tfloat_min_value(const Temporal *temp);
extern double tfloat_start_value(const Temporal *temp);
extern bool tfloat_value_at_timestamptz(const Temporal *temp, TimestampTz t, bool strict, double *value);
extern double *tfloat_values(const Temporal *temp, int *count);
extern int tint_end_value(const Temporal *temp);
extern int tint_max_value(const Temporal *temp);
extern int tint_min_value(const Temporal *temp);
extern int tint_start_value(const Temporal *temp);
extern bool tint_value_at_timestamptz(const Temporal *temp, TimestampTz t, bool strict, int *value);
extern int *tint_values(const Temporal *temp, int *count);
extern double tnumber_integral(const Temporal *temp);
extern double tnumber_twavg(const Temporal *temp);
extern SpanSet *tnumber_valuespans(const Temporal *temp);
extern GSERIALIZED *tpoint_end_value(const Temporal *temp);
extern GSERIALIZED *tpoint_start_value(const Temporal *temp);
extern bool tpoint_value_at_timestamptz(const Temporal *temp, TimestampTz t, bool strict, GSERIALIZED **value);
extern GSERIALIZED **tpoint_values(const Temporal *temp, int *count);
extern text *ttext_end_value(const Temporal *temp);
extern text *ttext_max_value(const Temporal *temp);
extern text *ttext_min_value(const Temporal *temp);
extern text *ttext_start_value(const Temporal *temp);
extern bool ttext_value_at_timestamptz(const Temporal *temp, TimestampTz t, bool strict, text **value);
extern text **ttext_values(const Temporal *temp, int *count);

extern double float_degrees(double value, bool normalize);
extern Temporal *temporal_scale_time(const Temporal *temp, const Interval *duration);
extern Temporal *temporal_set_interp(const Temporal *temp, interpType interp);
extern Temporal *temporal_shift_scale_time(const Temporal *temp, const Interval *shift, const Interval *duration);
extern Temporal *temporal_shift_time(const Temporal *temp, const Interval *shift);
extern TInstant *temporal_to_tinstant(const Temporal *temp);
extern TSequence *temporal_to_tsequence(const Temporal *temp, char *interp_str);
extern TSequenceSet *temporal_to_tsequenceset(const Temporal *temp, char *interp_str);
extern Temporal *tfloat_degrees(const Temporal *temp, bool normalize);
extern Temporal *tfloat_radians(const Temporal *temp);
extern Temporal *tfloat_round(const Temporal *temp, int maxdd);
extern Temporal *tfloat_scale_value(const Temporal *temp, double width);
extern Temporal *tfloat_shift_scale_value(const Temporal *temp, double shift, double width);
extern Temporal *tfloat_shift_value(const Temporal *temp, double shift);
extern Temporal **tfloatarr_round(const Temporal **temp, int count, int maxdd);
extern Temporal *tint_scale_value(const Temporal *temp, int width);
extern Temporal *tint_shift_scale_value(const Temporal *temp, int shift, int width);
extern Temporal *tint_shift_value(const Temporal *temp, int shift);
extern Temporal *tpoint_round(const Temporal *temp, int maxdd);
extern Temporal *tpoint_transform(const Temporal *temp, int32 srid);
extern Temporal *tpoint_transform_pipeline(const Temporal *temp, char *pipelinestr, int32 srid, bool is_forward);
extern Temporal **tpointarr_round(const Temporal **temp, int count, int maxdd);

extern Temporal *temporal_append_tinstant(Temporal *temp, const TInstant *inst, double maxdist, Interval *maxt, bool expand);
extern Temporal *temporal_append_tsequence(Temporal *temp, const TSequence *seq, bool expand);
extern Temporal *temporal_delete_tstzspan(const Temporal *temp, const Span *s, bool connect);
extern Temporal *temporal_delete_tstzspanset(const Temporal *temp, const SpanSet *ss, bool connect);
extern Temporal *temporal_delete_timestamptz(const Temporal *temp, TimestampTz t, bool connect);
extern Temporal *temporal_delete_tstzset(const Temporal *temp, const Set *s, bool connect);
extern Temporal *temporal_insert(const Temporal *temp1, const Temporal *temp2, bool connect);
extern Temporal *temporal_merge(const Temporal *temp1, const Temporal *temp2);
extern Temporal *temporal_merge_array(Temporal **temparr, int count);
extern Temporal *temporal_update(const Temporal *temp1, const Temporal *temp2, bool connect);

extern Temporal *tbool_at_value(const Temporal *temp, bool b);
extern Temporal *tbool_minus_value(const Temporal *temp, bool b);
extern Temporal *temporal_at_max(const Temporal *temp);
extern Temporal *temporal_at_min(const Temporal *temp);
extern Temporal *temporal_at_tstzspan(const Temporal *temp, const Span *s);
extern Temporal *temporal_at_tstzspanset(const Temporal *temp, const SpanSet *ss);
extern Temporal *temporal_at_timestamptz(const Temporal *temp, TimestampTz t);
extern Temporal *temporal_at_tstzset(const Temporal *temp, const Set *s);
extern Temporal *temporal_at_values(const Temporal *temp, const Set *set);
extern Temporal *temporal_minus_max(const Temporal *temp);
extern Temporal *temporal_minus_min(const Temporal *temp);
extern Temporal *temporal_minus_tstzspan(const Temporal *temp, const Span *s);
extern Temporal *temporal_minus_tstzspanset(const Temporal *temp, const SpanSet *ss);
extern Temporal *temporal_minus_timestamptz(const Temporal *temp, TimestampTz t);
extern Temporal *temporal_minus_tstzset(const Temporal *temp, const Set *s);
extern Temporal *temporal_minus_values(const Temporal *temp, const Set *set);
extern Temporal *tfloat_at_value(const Temporal *temp, double d);
extern Temporal *tfloat_minus_value(const Temporal *temp, double d);
extern Temporal *tint_at_value(const Temporal *temp, int i);
extern Temporal *tint_minus_value(const Temporal *temp, int i);
extern Temporal *tnumber_at_span(const Temporal *temp, const Span *span);
extern Temporal *tnumber_at_spanset(const Temporal *temp, const SpanSet *ss);
extern Temporal *tnumber_at_tbox(const Temporal *temp, const TBox *box);
extern Temporal *tnumber_minus_span(const Temporal *temp, const Span *span);
extern Temporal *tnumber_minus_spanset(const Temporal *temp, const SpanSet *ss);
extern Temporal *tnumber_minus_tbox(const Temporal *temp, const TBox *box);
extern Temporal *tpoint_at_geom_time(const Temporal *temp, const GSERIALIZED *gs, const Span *zspan, const Span *period);
extern Temporal *tpoint_at_stbox(const Temporal *temp, const STBox *box, bool border_inc);
extern Temporal *tpoint_at_value(const Temporal *temp, GSERIALIZED *gs);
extern Temporal *tpoint_minus_geom_time(const Temporal *temp, const GSERIALIZED *gs, const Span *zspan, const Span *period);
extern Temporal *tpoint_minus_stbox(const Temporal *temp, const STBox *box, bool border_inc);
extern Temporal *tpoint_minus_value(const Temporal *temp, GSERIALIZED *gs);
extern Temporal *ttext_at_value(const Temporal *temp, text *txt);
extern Temporal *ttext_minus_value(const Temporal *temp, text *txt);

extern int temporal_cmp(const Temporal *temp1, const Temporal *temp2);
extern bool temporal_eq(const Temporal *temp1, const Temporal *temp2);
extern bool temporal_ge(const Temporal *temp1, const Temporal *temp2);
extern bool temporal_gt(const Temporal *temp1, const Temporal *temp2);
extern bool temporal_le(const Temporal *temp1, const Temporal *temp2);
extern bool temporal_lt(const Temporal *temp1, const Temporal *temp2);
extern bool temporal_ne(const Temporal *temp1, const Temporal *temp2);

extern int always_eq_bool_tbool(bool b, const Temporal *temp);
extern int always_eq_float_tfloat(double d, const Temporal *temp);
extern int always_eq_int_tint(int i, const Temporal *temp);
extern int always_eq_point_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern int always_eq_tbool_bool(const Temporal *temp, bool b);
extern int always_eq_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int always_eq_text_ttext(const text *txt, const Temporal *temp);
extern int always_eq_tfloat_float(const Temporal *temp, double d);
extern int always_eq_tint_int(const Temporal *temp, int i);
extern int always_eq_tpoint_point(const Temporal *temp, const GSERIALIZED *gs);
extern int always_eq_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int always_eq_ttext_text(const Temporal *temp, const text *txt);
extern int always_ne_bool_tbool(bool b, const Temporal *temp);
extern int always_ne_float_tfloat(double d, const Temporal *temp);
extern int always_ne_int_tint(int i, const Temporal *temp);
extern int always_ne_point_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern int always_ne_tbool_bool(const Temporal *temp, bool b);
extern int always_ne_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int always_ne_text_ttext(const text *txt, const Temporal *temp);
extern int always_ne_tfloat_float(const Temporal *temp, double d);
extern int always_ne_tint_int(const Temporal *temp, int i);
extern int always_ne_tpoint_point(const Temporal *temp, const GSERIALIZED *gs);
extern int always_ne_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int always_ne_ttext_text(const Temporal *temp, const text *txt);
extern int always_ge_float_tfloat(double d, const Temporal *temp);
extern int always_ge_int_tint(int i, const Temporal *temp);
extern int always_ge_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int always_ge_text_ttext(const text *txt, const Temporal *temp);
extern int always_ge_tfloat_float(const Temporal *temp, double d);
extern int always_ge_tint_int(const Temporal *temp, int i);
extern int always_ge_ttext_text(const Temporal *temp, const text *txt);
extern int always_gt_float_tfloat(double d, const Temporal *temp);
extern int always_gt_int_tint(int i, const Temporal *temp);
extern int always_gt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int always_gt_text_ttext(const text *txt, const Temporal *temp);
extern int always_gt_tfloat_float(const Temporal *temp, double d);
extern int always_gt_tint_int(const Temporal *temp, int i);
extern int always_gt_ttext_text(const Temporal *temp, const text *txt);
extern int always_le_float_tfloat(double d, const Temporal *temp);
extern int always_le_int_tint(int i, const Temporal *temp);
extern int always_le_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int always_le_text_ttext(const text *txt, const Temporal *temp);
extern int always_le_tfloat_float(const Temporal *temp, double d);
extern int always_le_tint_int(const Temporal *temp, int i);
extern int always_le_ttext_text(const Temporal *temp, const text *txt);
extern int always_lt_float_tfloat(double d, const Temporal *temp);
extern int always_lt_int_tint(int i, const Temporal *temp);
extern int always_lt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int always_lt_text_ttext(const text *txt, const Temporal *temp);
extern int always_lt_tfloat_float(const Temporal *temp, double d);
extern int always_lt_tint_int(const Temporal *temp, int i);
extern int always_lt_ttext_text(const Temporal *temp, const text *txt);
extern int ever_eq_bool_tbool(bool b, const Temporal *temp);
extern int ever_eq_float_tfloat(double d, const Temporal *temp);
extern int ever_eq_int_tint(int i, const Temporal *temp);
extern int ever_eq_point_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern int ever_eq_tbool_bool(const Temporal *temp, bool b);
extern int ever_eq_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int ever_eq_text_ttext(const text *txt, const Temporal *temp);
extern int ever_eq_tfloat_float(const Temporal *temp, double d);
extern int ever_eq_tint_int(const Temporal *temp, int i);
extern int ever_eq_tpoint_point(const Temporal *temp, const GSERIALIZED *gs);
extern int ever_eq_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int ever_eq_ttext_text(const Temporal *temp, const text *txt);
extern int ever_ge_float_tfloat(double d, const Temporal *temp);
extern int ever_ge_int_tint(int i, const Temporal *temp);
extern int ever_ge_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int ever_ge_text_ttext(const text *txt, const Temporal *temp);
extern int ever_ge_tfloat_float(const Temporal *temp, double d);
extern int ever_ge_tint_int(const Temporal *temp, int i);
extern int ever_ge_ttext_text(const Temporal *temp, const text *txt);
extern int ever_gt_float_tfloat(double d, const Temporal *temp);
extern int ever_gt_int_tint(int i, const Temporal *temp);
extern int ever_gt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int ever_gt_text_ttext(const text *txt, const Temporal *temp);
extern int ever_gt_tfloat_float(const Temporal *temp, double d);
extern int ever_gt_tint_int(const Temporal *temp, int i);
extern int ever_gt_ttext_text(const Temporal *temp, const text *txt);
extern int ever_le_float_tfloat(double d, const Temporal *temp);
extern int ever_le_int_tint(int i, const Temporal *temp);
extern int ever_le_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int ever_le_text_ttext(const text *txt, const Temporal *temp);
extern int ever_le_tfloat_float(const Temporal *temp, double d);
extern int ever_le_tint_int(const Temporal *temp, int i);
extern int ever_le_ttext_text(const Temporal *temp, const text *txt);
extern int ever_lt_float_tfloat(double d, const Temporal *temp);
extern int ever_lt_int_tint(int i, const Temporal *temp);
extern int ever_lt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int ever_lt_text_ttext(const text *txt, const Temporal *temp);
extern int ever_lt_tfloat_float(const Temporal *temp, double d);
extern int ever_lt_tint_int(const Temporal *temp, int i);
extern int ever_lt_ttext_text(const Temporal *temp, const text *txt);
extern int ever_ne_bool_tbool(bool b, const Temporal *temp);
extern int ever_ne_float_tfloat(double d, const Temporal *temp);
extern int ever_ne_int_tint(int i, const Temporal *temp);
extern int ever_ne_point_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern int ever_ne_tbool_bool(const Temporal *temp, bool b);
extern int ever_ne_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern int ever_ne_text_ttext(const text *txt, const Temporal *temp);
extern int ever_ne_tfloat_float(const Temporal *temp, double d);
extern int ever_ne_tint_int(const Temporal *temp, int i);
extern int ever_ne_tpoint_point(const Temporal *temp, const GSERIALIZED *gs);
extern int ever_ne_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int ever_ne_ttext_text(const Temporal *temp, const text *txt);

extern Temporal *teq_bool_tbool(bool b, const Temporal *temp);
extern Temporal *teq_float_tfloat(double d, const Temporal *temp);
extern Temporal *teq_int_tint(int i, const Temporal *temp);
extern Temporal *teq_point_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern Temporal *teq_tbool_bool(const Temporal *temp, bool b);
extern Temporal *teq_tbool_tbool(const Temporal *temp1, const Temporal *temp2);
/* extern Temporal *teq_temporal_temporal(const Temporal *temp1, const Temporal *temp2);  (undefined) */
extern Temporal *teq_text_ttext(const text *txt, const Temporal *temp);
extern Temporal *teq_tfloat_float(const Temporal *temp, double d);
extern Temporal *teq_tfloat_tfloat(const Temporal *temp1, const Temporal *temp2);
extern Temporal *teq_tpoint_point(const Temporal *temp, const GSERIALIZED *gs);
extern Temporal *teq_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern Temporal *teq_tint_int(const Temporal *temp, int i);
extern Temporal *teq_tint_tint(const Temporal *temp1, const Temporal *temp2);
extern Temporal *teq_ttext_text(const Temporal *temp, const text *txt);
extern Temporal *teq_ttext_ttext(const Temporal *temp1, const Temporal *temp2);
extern Temporal *tge_float_tfloat(double d, const Temporal *temp);
extern Temporal *tge_int_tint(int i, const Temporal *temp);
/* extern Temporal *tge_temporal_temporal(const Temporal *temp1, const Temporal *temp2);  (undefined) */
extern Temporal *tge_text_ttext(const text *txt, const Temporal *temp);
extern Temporal *tge_tfloat_float(const Temporal *temp, double d);
extern Temporal *tge_tint_int(const Temporal *temp, int i);
extern Temporal *tge_ttext_text(const Temporal *temp, const text *txt);
extern Temporal *tgt_float_tfloat(double d, const Temporal *temp);
extern Temporal *tgt_int_tint(int i, const Temporal *temp);
/* extern Temporal *tgt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);  (undefined) */
extern Temporal *tgt_text_ttext(const text *txt, const Temporal *temp);
extern Temporal *tgt_tfloat_float(const Temporal *temp, double d);
extern Temporal *tgt_tint_int(const Temporal *temp, int i);
extern Temporal *tgt_ttext_text(const Temporal *temp, const text *txt);
extern Temporal *tle_float_tfloat(double d, const Temporal *temp);
extern Temporal *tle_int_tint(int i, const Temporal *temp);
/* extern Temporal *tle_temporal_temporal(const Temporal *temp1, const Temporal *temp2);  (undefined) */
extern Temporal *tle_text_ttext(const text *txt, const Temporal *temp);
extern Temporal *tle_tfloat_float(const Temporal *temp, double d);
extern Temporal *tle_tint_int(const Temporal *temp, int i);
extern Temporal *tle_ttext_text(const Temporal *temp, const text *txt);
extern Temporal *tlt_float_tfloat(double d, const Temporal *temp);
extern Temporal *tlt_int_tint(int i, const Temporal *temp);
/* extern Temporal *tlt_temporal_temporal(const Temporal *temp1, const Temporal *temp2);  (undefined) */
extern Temporal *tlt_text_ttext(const text *txt, const Temporal *temp);
extern Temporal *tlt_tfloat_float(const Temporal *temp, double d);
extern Temporal *tlt_tint_int(const Temporal *temp, int i);
extern Temporal *tlt_ttext_text(const Temporal *temp, const text *txt);
extern Temporal *tne_bool_tbool(bool b, const Temporal *temp);
extern Temporal *tne_float_tfloat(double d, const Temporal *temp);
extern Temporal *tne_int_tint(int i, const Temporal *temp);
extern Temporal *tne_point_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern Temporal *tne_tbool_bool(const Temporal *temp, bool b);
extern Temporal *tne_tbool_tbool(const Temporal *temp1, const Temporal *temp2);
/* extern Temporal *tne_temporal_temporal(const Temporal *temp1, const Temporal *temp2);  (undefined) */
extern Temporal *tne_text_ttext(const text *txt, const Temporal *temp);
extern Temporal *tne_tfloat_float(const Temporal *temp, double d);
extern Temporal *tne_tfloat_tfloat(const Temporal *temp1, const Temporal *temp2);
extern Temporal *tne_tpoint_point(const Temporal *temp, const GSERIALIZED *gs);
extern Temporal *tne_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern Temporal *tne_tint_int(const Temporal *temp, int i);
extern Temporal *tne_tint_tint(const Temporal *temp1, const Temporal *temp2);
extern Temporal *tne_ttext_text(const Temporal *temp, const text *txt);
extern Temporal *tne_ttext_ttext(const Temporal *temp1, const Temporal *temp2);

extern bool adjacent_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool adjacent_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool adjacent_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool adjacent_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool adjacent_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool adjacent_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool adjacent_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool adjacent_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool adjacent_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool adjacent_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool adjacent_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool contained_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool contained_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool contained_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool contained_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool contained_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool contained_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool contained_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool contained_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool contained_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool contained_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool contained_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool contains_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool contains_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool contains_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool contains_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool contains_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool contains_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool contains_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool contains_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool contains_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool contains_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool contains_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool overlaps_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool overlaps_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overlaps_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool overlaps_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool overlaps_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool overlaps_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool overlaps_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool overlaps_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool overlaps_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overlaps_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overlaps_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool same_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool same_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool same_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool same_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool same_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool same_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool same_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool same_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool same_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool same_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool same_tstzspan_temporal(const Span *s, const Temporal *temp);

extern bool above_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool above_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool above_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool after_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool after_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool after_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool after_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool after_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool after_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool after_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool after_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool after_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool back_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool back_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool back_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool before_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool before_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool before_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool before_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool before_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool before_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool before_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool before_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool before_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool below_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool below_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool below_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool front_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool front_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool front_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool left_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool left_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool left_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool left_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool left_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool left_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool left_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool left_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overabove_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overabove_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overabove_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overafter_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overafter_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool overafter_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool overafter_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool overafter_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool overafter_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool overafter_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overafter_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overafter_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool overback_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overback_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overback_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overbefore_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overbefore_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool overbefore_temporal_tstzspan(const Temporal *temp, const Span *s);
extern bool overbefore_temporal_temporal(const Temporal *temp1, const Temporal *temp2);
extern bool overbefore_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool overbefore_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool overbefore_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overbefore_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overbefore_tstzspan_temporal(const Span *s, const Temporal *temp);
extern bool overbelow_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overbelow_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overbelow_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overfront_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overfront_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overfront_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overleft_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool overleft_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overleft_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool overleft_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool overleft_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool overleft_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool overleft_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overleft_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool overright_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool overright_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool overright_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool overright_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool overright_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool overright_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool overright_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool overright_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern bool right_numspan_tnumber(const Span *s, const Temporal *temp);
extern bool right_stbox_tpoint(const STBox *box, const Temporal *temp);
extern bool right_tbox_tnumber(const TBox *box, const Temporal *temp);
extern bool right_tnumber_numspan(const Temporal *temp, const Span *s);
extern bool right_tnumber_tbox(const Temporal *temp, const TBox *box);
extern bool right_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern bool right_tpoint_stbox(const Temporal *temp, const STBox *box);
extern bool right_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);

extern Temporal *tand_bool_tbool(bool b, const Temporal *temp);
extern Temporal *tand_tbool_bool(const Temporal *temp, bool b);
extern Temporal *tand_tbool_tbool(const Temporal *temp1, const Temporal *temp2);
extern SpanSet *tbool_when_true(const Temporal *temp);
extern Temporal *tnot_tbool(const Temporal *temp);
extern Temporal *tor_bool_tbool(bool b, const Temporal *temp);
extern Temporal *tor_tbool_bool(const Temporal *temp, bool b);
extern Temporal *tor_tbool_tbool(const Temporal *temp1, const Temporal *temp2);

extern Temporal *add_float_tfloat(double d, const Temporal *tnumber);
extern Temporal *add_int_tint(int i, const Temporal *tnumber);
extern Temporal *add_tfloat_float(const Temporal *tnumber, double d);
extern Temporal *add_tint_int(const Temporal *tnumber, int i);
extern Temporal *add_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);
extern Temporal *div_float_tfloat(double d, const Temporal *tnumber);
extern Temporal *div_int_tint(int i, const Temporal *tnumber);
extern Temporal *div_tfloat_float(const Temporal *tnumber, double d);
extern Temporal *div_tint_int(const Temporal *tnumber, int i);
extern Temporal *div_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);
extern Temporal *mult_float_tfloat(double d, const Temporal *tnumber);
extern Temporal *mult_int_tint(int i, const Temporal *tnumber);
extern Temporal *mult_tfloat_float(const Temporal *tnumber, double d);
extern Temporal *mult_tint_int(const Temporal *tnumber, int i);
extern Temporal *mult_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);
extern Temporal *sub_float_tfloat(double d, const Temporal *tnumber);
extern Temporal *sub_int_tint(int i, const Temporal *tnumber);
extern Temporal *sub_tfloat_float(const Temporal *tnumber, double d);
extern Temporal *sub_tint_int(const Temporal *tnumber, int i);
extern Temporal *sub_tnumber_tnumber(const Temporal *tnumber1, const Temporal *tnumber2);
extern Temporal *tfloat_derivative(const Temporal *temp);
extern Temporal *tnumber_abs(const Temporal *temp);
extern Temporal *tnumber_angular_difference(const Temporal *temp);
extern Temporal *tnumber_delta_value(const Temporal *temp);

extern Temporal *textcat_text_ttext(const text *txt, const Temporal *temp);
extern Temporal *textcat_ttext_text(const Temporal *temp, const text *txt);
extern Temporal *textcat_ttext_ttext(const Temporal *temp1, const Temporal *temp2);
extern Temporal *ttext_upper(const Temporal *temp);
extern Temporal *ttext_lower(const Temporal *temp);
extern Temporal *ttext_initcap(const Temporal *temp);

extern Temporal *distance_tfloat_float(const Temporal *temp, double d);
extern Temporal *distance_tint_int(const Temporal *temp, int i);
extern Temporal *distance_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);
extern Temporal *distance_tpoint_point(const Temporal *temp, const GSERIALIZED *gs);
extern Temporal *distance_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern double nad_stbox_geo(const STBox *box, const GSERIALIZED *gs);
extern double nad_stbox_stbox(const STBox *box1, const STBox *box2);
extern int nad_tint_int(const Temporal *temp, int i);
extern int nad_tint_tbox(const Temporal *temp, const TBox *box);
extern int nad_tint_tint(const Temporal *temp1, const Temporal *temp2);
extern int nad_tboxint_tboxint(const TBox *box1, const TBox *box2);
extern double nad_tfloat_float(const Temporal *temp, double d);
extern double nad_tfloat_tfloat(const Temporal *temp1, const Temporal *temp2);
extern double nad_tfloat_tbox(const Temporal *temp, const TBox *box);
extern double nad_tboxfloat_tboxfloat(const TBox *box1, const TBox *box2);
extern double nad_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern double nad_tpoint_stbox(const Temporal *temp, const STBox *box);
extern double nad_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern TInstant *nai_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern TInstant *nai_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern GSERIALIZED *shortestline_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern GSERIALIZED *shortestline_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);

extern bool bearing_point_point(const GSERIALIZED *gs1, const GSERIALIZED *gs2, double *result);
extern Temporal *bearing_tpoint_point(const Temporal *temp, const GSERIALIZED *gs, bool invert);
extern Temporal *bearing_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern Temporal *tpoint_angular_difference(const Temporal *temp);
extern Temporal *tpoint_azimuth(const Temporal *temp);
extern GSERIALIZED *tpoint_convex_hull(const Temporal *temp);
extern Temporal *tpoint_cumulative_length(const Temporal *temp);
extern bool tpoint_direction(const Temporal *temp, double *result);
extern Temporal *tpoint_get_x(const Temporal *temp);
extern Temporal *tpoint_get_y(const Temporal *temp);
extern Temporal *tpoint_get_z(const Temporal *temp);
extern bool tpoint_is_simple(const Temporal *temp);
extern double tpoint_length(const Temporal *temp);
extern Temporal *tpoint_speed(const Temporal *temp);
extern int tpoint_srid(const Temporal *temp);
extern STBox *tpoint_stboxes(const Temporal *temp, int *count);
extern GSERIALIZED *tpoint_trajectory(const Temporal *temp);
extern GSERIALIZED *tpoint_twcentroid(const Temporal *temp);

extern STBox *geo_expand_space(const GSERIALIZED *gs, double d);
extern Temporal *geomeas_to_tpoint(const GSERIALIZED *gs);
extern Temporal *tgeogpoint_to_tgeompoint(const Temporal *temp);
extern Temporal *tgeompoint_to_tgeogpoint(const Temporal *temp);
bool tpoint_AsMVTGeom(const Temporal *temp, const STBox *bounds, int32_t extent, int32_t buffer, bool clip_geom, GSERIALIZED **gsarr, int64 **timesarr, int *count);
extern STBox *tpoint_expand_space(const Temporal *temp, double d);
extern Temporal **tpoint_make_simple(const Temporal *temp, int *count);
extern Temporal *tpoint_set_srid(const Temporal *temp, int32 srid);
bool tpoint_tfloat_to_geomeas(const Temporal *tpoint, const Temporal *measure, bool segmentize, GSERIALIZED **result);

extern int acontains_geo_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern int adisjoint_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern int adisjoint_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int adwithin_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, double dist);
extern int adwithin_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2, double dist);
extern int aintersects_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern int aintersects_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int atouches_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern int econtains_geo_tpoint(const GSERIALIZED *gs, const Temporal *temp);
extern int edisjoint_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern int edisjoint_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int edwithin_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, double dist);
extern int edwithin_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2, double dist);
extern int eintersects_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);
extern int eintersects_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2);
extern int etouches_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs);

extern Temporal *tcontains_geo_tpoint(const GSERIALIZED *gs, const Temporal *temp, bool restr, bool atvalue);
extern Temporal *tdisjoint_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, bool restr, bool atvalue);
extern Temporal *tdisjoint_tpoint_tpoint (const Temporal *temp1, const Temporal *temp2, bool restr, bool atvalue);
extern Temporal *tdwithin_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, double dist, bool restr, bool atvalue);
extern Temporal *tdwithin_tpoint_tpoint(const Temporal *temp1, const Temporal *temp2, double dist, bool restr, bool atvalue);
extern Temporal *tintersects_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, bool restr, bool atvalue);
extern Temporal *tintersects_tpoint_tpoint (const Temporal *temp1, const Temporal *temp2, bool restr, bool atvalue);
extern Temporal *ttouches_tpoint_geo(const Temporal *temp, const GSERIALIZED *gs, bool restr, bool atvalue);

extern SkipList *tbool_tand_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tbool_tor_transfn(SkipList *state, const Temporal *temp);
extern Span *temporal_extent_transfn(Span *s, const Temporal *temp);
extern Temporal *temporal_tagg_finalfn(SkipList *state);
extern SkipList *temporal_tcount_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tfloat_tmax_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tfloat_tmin_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tfloat_tsum_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tfloat_wmax_transfn(SkipList *state, const Temporal *temp, const Interval *interv);
extern SkipList *tfloat_wmin_transfn(SkipList *state, const Temporal *temp, const Interval *interv);
extern SkipList *tfloat_wsum_transfn(SkipList *state, const Temporal *temp, const Interval *interv);
extern SkipList *timestamptz_tcount_transfn(SkipList *state, TimestampTz t);
extern SkipList *tint_tmax_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tint_tmin_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tint_tsum_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tint_wmax_transfn(SkipList *state, const Temporal *temp, const Interval *interv);
extern SkipList *tint_wmin_transfn(SkipList *state, const Temporal *temp, const Interval *interv);
extern SkipList *tint_wsum_transfn(SkipList *state, const Temporal *temp, const Interval *interv);
extern TBox *tnumber_extent_transfn(TBox *box, const Temporal *temp);
extern Temporal *tnumber_tavg_finalfn(SkipList *state);
extern SkipList *tnumber_tavg_transfn(SkipList *state, const Temporal *temp);
extern SkipList *tnumber_wavg_transfn(SkipList *state, const Temporal *temp, const Interval *interv);
extern STBox *tpoint_extent_transfn(STBox *box, const Temporal *temp);
extern Temporal *tpoint_tcentroid_finalfn(SkipList *state);
extern SkipList *tpoint_tcentroid_transfn(SkipList *state, Temporal *temp);
extern SkipList *tstzset_tcount_transfn(SkipList *state, const Set *s);
extern SkipList *tstzspan_tcount_transfn(SkipList *state, const Span *s);
extern SkipList *tstzspanset_tcount_transfn(SkipList *state, const SpanSet *ss);
extern SkipList *ttext_tmax_transfn(SkipList *state, const Temporal *temp);
extern SkipList *ttext_tmin_transfn(SkipList *state, const Temporal *temp);

Temporal *temporal_simplify_dp(const Temporal *temp, double eps_dist, bool synchronized);
Temporal *temporal_simplify_max_dist(const Temporal *temp, double eps_dist, bool synchronized);
Temporal *temporal_simplify_min_dist(const Temporal *temp, double dist);
Temporal *temporal_simplify_min_tdelta(const Temporal *temp, const Interval *mint);

extern Temporal *temporal_tprecision(const Temporal *temp, const Interval *duration, TimestampTz origin);
extern Temporal *temporal_tsample(const Temporal *temp, const Interval *duration, TimestampTz origin);

extern double temporal_dyntimewarp_distance(const Temporal *temp1, const Temporal *temp2);
extern Match *temporal_dyntimewarp_path(const Temporal *temp1, const Temporal *temp2, int *count);
extern double temporal_frechet_distance(const Temporal *temp1, const Temporal *temp2);
extern Match *temporal_frechet_path(const Temporal *temp1, const Temporal *temp2, int *count);
extern double temporal_hausdorff_distance(const Temporal *temp1, const Temporal *temp2);

extern double float_bucket(double value, double size, double origin);
extern Span *floatspan_bucket_list(const Span *bounds, double size, double origin, int *count);
extern int int_bucket(int value, int size, int origin);
extern Span *intspan_bucket_list(const Span *bounds, int size, int origin, int *count);
extern STBox *stbox_tile(GSERIALIZED *point, TimestampTz t, double xsize, double ysize, double zsize, Interval *duration, GSERIALIZED *sorigin, TimestampTz torigin, bool hast);
extern STBox *stbox_tile_list(const STBox *bounds, double xsize, double ysize, double zsize, const Interval *duration, GSERIALIZED *sorigin, TimestampTz torigin, int *count);
extern Temporal **temporal_time_split(Temporal *temp, Interval *duration, TimestampTz torigin, TimestampTz **time_buckets, int *count);
extern Temporal **tfloat_value_split(Temporal *temp, double size, double origin, double **value_buckets, int *count);
extern Temporal **tfloat_value_time_split(Temporal *temp, double size, Interval *duration, double vorigin, TimestampTz torigin, double **value_buckets, TimestampTz **time_buckets, int *count);
extern Temporal **tpoint_space_split(Temporal *temp, float xsize, float ysize, float zsize, GSERIALIZED *sorigin, bool bitmatrix, GSERIALIZED ***space_buckets, int *count);
extern TBox *tfloatbox_tile(double value, TimestampTz t, double vsize, Interval *duration, double vorigin, TimestampTz torigin);
extern TBox *tfloatbox_tile_list(const TBox *box, double xsize, const Interval *duration, double xorigin, TimestampTz torigin, int *count);
extern TimestampTz timestamptz_bucket(TimestampTz timestamp, const Interval *duration, TimestampTz origin);
extern Temporal **tint_value_split(Temporal *temp, int size, int origin, int **value_buckets, int *count);
extern Temporal **tint_value_time_split(Temporal *temp, int size, Interval *duration, int vorigin, TimestampTz torigin, int **value_buckets, TimestampTz **time_buckets, int *count);
extern TBox *tintbox_tile(int value, TimestampTz t, int vsize, Interval *duration, int vorigin, TimestampTz torigin);
extern TBox *tintbox_tile_list(const TBox *box, int xsize, const Interval *duration, int xorigin, TimestampTz torigin, int *count);
extern Temporal **tpoint_space_time_split(Temporal *temp, float xsize, float ysize, float zsize, Interval *duration, GSERIALIZED *sorigin, TimestampTz torigin, bool bitmatrix, GSERIALIZED ***space_buckets, TimestampTz **time_buckets, int *count);
extern Span *tstzspan_bucket_list(const Span *bounds, const Interval *duration, TimestampTz origin, int *count);

//-------------------- meos_catalog.h --------------------


//#include <stdbool.h>

typedef signed short int16;

//#include <meos.h>

typedef enum
{
  T_UNKNOWN        = 0,   
  T_BOOL           = 1,   
  T_DATE           = 2,   
  T_DATEMULTIRANGE = 3,   
  T_DATERANGE      = 4,   
  T_DATESET        = 5,   
  T_DATESPAN       = 6,   
  T_DATESPANSET    = 7,   
  T_DOUBLE2        = 8,   
  T_DOUBLE3        = 9,   
  T_DOUBLE4        = 10,   
  T_FLOAT8         = 11,  
  T_FLOATSET       = 12,  
  T_FLOATSPAN      = 13,  
  T_FLOATSPANSET   = 14,  
  T_INT4           = 15,  
  T_INT4MULTIRANGE = 16,  
  T_INT4RANGE      = 17,  
  T_INTSET         = 18,  
  T_INTSPAN        = 19,  
  T_INTSPANSET     = 20,  
  T_INT8           = 21,  
  T_BIGINTSET      = 22,  
  T_BIGINTSPAN     = 23,  
  T_BIGINTSPANSET  = 24,  
  T_STBOX          = 25,  
  T_TBOOL          = 26,  
  T_TBOX           = 27,  
  T_TDOUBLE2       = 28,  
  T_TDOUBLE3       = 29,  
  T_TDOUBLE4       = 30,  
  T_TEXT           = 31,  
  T_TEXTSET        = 32,  
  T_TFLOAT         = 33,  
  T_TIMESTAMPTZ    = 34,  
  T_TINT           = 35,  
  T_TSTZMULTIRANGE = 36,  
  T_TSTZRANGE      = 37,  
  T_TSTZSET        = 38,  
  T_TSTZSPAN       = 39,  
  T_TSTZSPANSET    = 40,  
  T_TTEXT          = 41,  
  T_GEOMETRY       = 42,  
  T_GEOMSET        = 43,  
  T_GEOGRAPHY      = 44,  
  T_GEOGSET        = 45,  
  T_TGEOMPOINT     = 46,  
  T_TGEOGPOINT     = 47,  
  T_NPOINT         = 48,  
  T_NPOINTSET      = 49,  
  T_NSEGMENT       = 50,  
  T_TNPOINT        = 51,  
} meosType;

#define NO_MEOS_TYPES 52
typedef enum
{
  UNKNOWN_OP      = 0,
  EQ_OP           = 1,  
  NE_OP           = 2,  
  LT_OP           = 3,  
  LE_OP           = 4,  
  GT_OP           = 5,  
  GE_OP           = 6,  
  ADJACENT_OP     = 7,  
  UNION_OP        = 8,  
  MINUS_OP        = 9,  
  INTERSECT_OP    = 10, 
  OVERLAPS_OP     = 11, 
  CONTAINS_OP     = 12, 
  CONTAINED_OP    = 13, 
  SAME_OP         = 14, 
  LEFT_OP         = 15, 
  OVERLEFT_OP     = 16, 
  RIGHT_OP        = 17, 
  OVERRIGHT_OP    = 18, 
  BELOW_OP        = 19, 
  OVERBELOW_OP    = 20, 
  ABOVE_OP        = 21, 
  OVERABOVE_OP    = 22, 
  FRONT_OP        = 23, 
  OVERFRONT_OP    = 24, 
  BACK_OP         = 25, 
  OVERBACK_OP     = 26, 
  BEFORE_OP       = 27, 
  OVERBEFORE_OP   = 28, 
  AFTER_OP        = 29, 
  OVERAFTER_OP    = 30, 
  EVEREQ_OP       = 31, 
  EVERNE_OP       = 32, 
  EVERLT_OP       = 33, 
  EVERLE_OP       = 34, 
  EVERGT_OP       = 35, 
  EVERGE_OP       = 36, 
  ALWAYSEQ_OP     = 37, 
  ALWAYSNE_OP     = 38, 
  ALWAYSLT_OP     = 39, 
  ALWAYSLE_OP     = 40, 
  ALWAYSGT_OP     = 41, 
  ALWAYSGE_OP     = 42, 
} meosOper;

typedef struct
{
  meosType temptype;    
  meosType basetype;    
} temptype_catalog_struct;

typedef struct
{
  meosType settype;     
  meosType basetype;    
} settype_catalog_struct;

typedef struct
{
  meosType spantype;    
  meosType basetype;    
} spantype_catalog_struct;

typedef struct
{
  meosType spansettype;    
  meosType spantype;       
} spansettype_catalog_struct;

/* extern bool temptype_subtype(tempSubtype subtype);  (undefined) */
/* extern bool temptype_subtype_all(tempSubtype subtype);  (undefined) */
extern const char *tempsubtype_name(tempSubtype subtype);
extern bool tempsubtype_from_string(const char *str, int16 *subtype);
extern const char *meosoper_name(meosOper oper);
extern meosOper meosoper_from_string(const char *name);
extern const char *interptype_name(interpType interp);
extern interpType interptype_from_string(const char *interp_str);

extern const char *meostype_name(meosType type);
extern meosType temptype_basetype(meosType type);
extern meosType settype_basetype(meosType type);
extern meosType spantype_basetype(meosType type);
extern meosType spantype_spansettype(meosType type);
extern meosType spansettype_spantype(meosType type);
extern meosType basetype_spantype(meosType type);
extern meosType basetype_settype(meosType type);

/* extern bool meos_basetype(meosType type);  (undefined) */
/* extern bool alpha_basetype(meosType type);  (undefined) */
extern bool tnumber_basetype(meosType type);
/* extern bool alphanum_basetype(meosType type);  (undefined) */
extern bool geo_basetype(meosType type);
extern bool spatial_basetype(meosType type);

extern bool time_type(meosType type);
/* extern bool set_basetype(meosType type);  (undefined) */

extern bool set_type(meosType type);
extern bool numset_type(meosType type);
extern bool ensure_numset_type(meosType type);
extern bool timeset_type(meosType type);
/* extern bool ensure_timeset_type(meosType type);  (undefined) */
extern bool set_spantype(meosType type);
extern bool ensure_set_spantype(meosType type);
extern bool alphanumset_type(meosType settype);
extern bool geoset_type(meosType type);
extern bool ensure_geoset_type(meosType type);
extern bool spatialset_type(meosType type);
extern bool ensure_spatialset_type(meosType type);

extern bool span_basetype(meosType type);
extern bool span_canon_basetype(meosType type);
extern bool span_type(meosType type);
/* extern bool span_bbox_type(meosType type);  (undefined) */
extern bool numspan_basetype(meosType type);
extern bool numspan_type(meosType type);
extern bool ensure_numspan_type(meosType type);
extern bool timespan_basetype(meosType type);
extern bool timespan_type(meosType type);
/* extern bool ensure_timespan_type(meosType type);  (undefined) */

extern bool spanset_type(meosType type);
/* extern bool numspanset_type(meosType type);  (undefined) */
extern bool timespanset_type(meosType type);
extern bool ensure_timespanset_type(meosType type);

extern bool temporal_type(meosType type);
/* extern bool temporal_basetype(meosType type);  (undefined) */
extern bool temptype_continuous(meosType type);
extern bool basetype_byvalue(meosType type);
extern bool basetype_varlength(meosType type);
extern int16 basetype_length(meosType type);
/* extern bool talphanum_type(meosType type);  (undefined) */
extern bool talpha_type(meosType type);
extern bool tnumber_type(meosType type);
extern bool ensure_tnumber_type(meosType type);
/* extern bool tnumber_basetype(meosType type);  (repeated) */
extern bool ensure_tnumber_basetype(meosType type);
/* extern bool tnumber_settype(meosType type);  (undefined) */
extern bool tnumber_spantype(meosType type);
extern bool tnumber_spansettype(meosType type);
extern bool tspatial_type(meosType type);
extern bool ensure_tspatial_type(meosType type);
extern bool tspatial_basetype(meosType type);
extern bool tgeo_type(meosType type);
extern bool ensure_tgeo_type(meosType type);
extern bool ensure_tnumber_tgeo_type(meosType type);

 

//-------------------- meos_internal.h --------------------


//#include <stddef.h>

//#include <json-c/json.h>

//#include <meos.h>
//#include "meos_catalog.h" 

 

extern Datum datum_degrees(Datum d, Datum normalize);
extern Datum datum_radians(Datum d);
extern uint32 datum_hash(Datum d, meosType basetype);
extern uint64 datum_hash_extended(Datum d, meosType basetype, uint64 seed);

 

extern Set *set_in(const char *str, meosType basetype);
extern char *set_out(const Set *s, int maxdd);
extern Span *span_in(const char *str, meosType spantype);
extern char *span_out(const Span *s, int maxdd);
extern SpanSet *spanset_in(const char *str, meosType spantype);
extern char *spanset_out(const SpanSet *ss, int maxdd);

extern Set *set_cp(const Set *s);
extern Set *set_make(const Datum *values, int count, meosType basetype, bool ordered);
extern Set *set_make_exp(const Datum *values, int count, int maxcount, meosType basetype, bool ordered);
extern Set *set_make_free(Datum *values, int count, meosType basetype, bool ordered);
extern Span *span_cp(const Span *s);
extern Span *span_make(Datum lower, Datum upper, bool lower_inc, bool upper_inc, meosType basetype);
extern void span_set(Datum lower, Datum upper, bool lower_inc, bool upper_inc, meosType basetype, meosType spantype, Span *s);
extern SpanSet *spanset_cp(const SpanSet *ss);
extern SpanSet *spanset_make_exp(Span *spans, int count, int maxcount, bool normalize, bool ordered);
extern SpanSet *spanset_make_free(Span *spans, int count, bool normalize, bool ordered);

extern Set *dateset_tstzset(const Set *s);
extern Span *datespan_tstzspan(const Span *s);
extern SpanSet *datespanset_tstzspanset(const SpanSet *ss);
extern Set *floatset_intset(const Set *s);
extern Span *floatspan_intspan(const Span *s);
extern SpanSet *floatspanset_intspanset(const SpanSet *ss);
extern Set *intset_floatset(const Set *s);
extern Span *intspan_floatspan(const Span *s);
extern SpanSet *intspanset_floatspanset(const SpanSet *ss);
extern Span *set_span(const Set *s);
extern SpanSet *set_spanset(const Set *s);
extern SpanSet *span_spanset(const Span *s);
extern Set *tstzset_dateset(const Set *s);
extern Span *tstzspan_datespan(const Span *s);
extern SpanSet *tstzspanset_datespanset(const SpanSet *ss);
extern void value_set_span(Datum value, meosType basetype, Span *s);
extern Set *value_to_set(Datum d, meosType basetype);
extern Span *value_to_span(Datum d, meosType basetype);
extern SpanSet *value_to_spanset(Datum d, meosType basetype);

extern Datum numspan_width(const Span *s);
extern Datum numspanset_width(const SpanSet *ss, bool boundspan);
extern Datum set_end_value(const Set *s);
extern int set_mem_size(const Set *s);
extern void set_set_span(const Set *s, Span *sp);
/* extern Span *set_span(const Set *s);  (repeated) */
extern Datum set_start_value(const Set *s);
extern bool set_value_n(const Set *s, int n, Datum *result);
extern Datum *set_vals(const Set *s);
extern Datum *set_values(const Set *s);
extern Datum spanset_lower(const SpanSet *ss);
extern int spanset_mem_size(const SpanSet *ss);
extern const Span **spanset_sps(const SpanSet *ss);
extern Datum spanset_upper(const SpanSet *ss);

extern void datespan_set_tstzspan(const Span *s1, Span *s2);
extern Set * floatset_deg(const Set *s, bool normalize);
extern Set * floatset_rad(const Set *s);
extern Set * floatset_rnd(const Set *s, int size);
extern Span *floatspan_rnd(const Span *s, int size);
extern SpanSet *floatspanset_rnd(const SpanSet *ss, int size);
extern void floatspan_set_intspan(const Span *s1, Span *s2);
extern void intspan_set_floatspan(const Span *s1, Span *s2);
extern Set *numset_shift_scale(const Set *s, Datum shift, Datum width, bool hasshift, bool haswidth);
extern Span *numspan_shift_scale(const Span *s, Datum shift, Datum width, bool hasshift, bool haswidth);
extern SpanSet *numspanset_shift_scale(const SpanSet *ss, Datum shift, Datum width, bool hasshift, bool haswidth);
extern Set *set_compact(const Set *s);
extern void span_expand(const Span *s1, Span *s2);
extern SpanSet *spanset_compact(const SpanSet *ss);
extern Set *textcat_textset_text_int(const Set *s, const text *txt, bool invert);
extern void tstzspan_set_datespan(const Span *s1, Span *s2);

extern int set_cmp_int(const Set *s1, const Set *s2);
/* extern bool set_eq_int(const Set *s1, const Set *s2);  (undefined) */
extern int span_cmp_int(const Span *s1, const Span *s2);
extern bool span_eq_int(const Span *s1, const Span *s2);
extern int spanset_cmp_int(const SpanSet *ss1, const SpanSet *ss2);
extern bool spanset_eq_int(const SpanSet *ss1, const SpanSet *ss2);

extern bool adj_span_span(const Span *s1, const Span *s2);
extern bool adjacent_span_value(const Span *s, Datum value);
extern bool adjacent_spanset_value(const SpanSet *ss, Datum value);
extern bool adjacent_value_spanset(Datum value, const SpanSet *ss);
extern bool cont_span_span(const Span *s1, const Span *s2);
extern bool contained_value_set(Datum value, const Set *s);
extern bool contained_value_span(Datum value, const Span *s);
extern bool contained_value_spanset(Datum value, const SpanSet *ss);
extern bool contains_set_value(const Set *s, Datum value);
extern bool contains_span_value(const Span *s, Datum value);
extern bool contains_spanset_value(const SpanSet *ss, Datum value);
extern bool ovadj_span_span(const Span *s1, const Span *s2);
extern bool over_span_span(const Span *s1, const Span *s2);

extern bool left_set_value(const Set *s, Datum value);
extern bool left_span_value(const Span *s, Datum value);
extern bool left_spanset_value(const SpanSet *ss, Datum value);
extern bool left_value_set(Datum value, const Set *s);
extern bool left_value_span(Datum value, const Span *s);
extern bool left_value_spanset(Datum value, const SpanSet *ss);
extern bool lf_span_span(const Span *s1, const Span *s2);
extern bool lfnadj_span_span(const Span *s1, const Span *s2);
extern bool overleft_set_value(const Set *s, Datum value);
extern bool overleft_span_value(const Span *s, Datum value);
extern bool overleft_spanset_value(const SpanSet *ss, Datum value);
extern bool overleft_value_set(Datum value, const Set *s);
extern bool overleft_value_span(Datum value, const Span *s);
extern bool overleft_value_spanset(Datum value, const SpanSet *ss);
extern bool overright_set_value(const Set *s, Datum value);
extern bool overright_span_value(const Span *s, Datum value);
extern bool overright_spanset_value(const SpanSet *ss, Datum value);
extern bool overright_value_set(Datum value, const Set *s);
extern bool overright_value_span(Datum value, const Span *s);
extern bool overright_value_spanset(Datum value, const SpanSet *ss);
extern bool ovlf_span_span(const Span *s1, const Span *s2);
extern bool ovri_span_span(const Span *s1, const Span *s2);
extern bool ri_span_span(const Span *s1, const Span *s2);
extern bool right_value_set(Datum value, const Set *s);
extern bool right_set_value(const Set *s, Datum value);
extern bool right_value_span(Datum value, const Span *s);
extern bool right_value_spanset(Datum value, const SpanSet *ss);
extern bool right_span_value(const Span *s, Datum value);
extern bool right_spanset_value(const SpanSet *ss, Datum value);

extern void bbox_union_span_span(const Span *s1, const Span *s2, Span *result);
extern bool inter_span_span(const Span *s1, const Span *s2, Span *result);
extern Set *intersection_set_value(const Set *s, Datum value);
extern Span *intersection_span_value(const Span *s, Datum value);
extern SpanSet *intersection_spanset_value(const SpanSet *ss, Datum value);
extern Set *intersection_value_set(Datum value, const Set *s);
extern Span *intersection_value_span(Datum value, const Span *s);
extern SpanSet *intersection_value_spanset(Datum value, const SpanSet *ss);
extern int mi_span_span(const Span *s1, const Span *s2, Span *result);
extern Set *minus_set_value(const Set *s, Datum value);
extern SpanSet *minus_span_value(const Span *s, Datum value);
extern SpanSet *minus_spanset_value(const SpanSet *ss, Datum value);
extern Set *minus_value_set(Datum value, const Set *s);
extern SpanSet *minus_value_span(Datum value, const Span *s);
extern SpanSet *minus_value_spanset(Datum value, const SpanSet *ss);
extern Span *super_union_span_span(const Span *s1, const Span *s2);
extern Set *union_set_value(const Set *s, const Datum value);
extern SpanSet *union_span_value(const Span *s, Datum value);
extern SpanSet *union_spanset_value(const SpanSet *ss, Datum value);
extern Set *union_value_set(const Datum value, const Set *s);
extern SpanSet *union_value_span(Datum value, const Span *s);
extern SpanSet *union_value_spanset(Datum value, const SpanSet *ss);

extern Datum dist_set_set(const Set *s1, const Set *s2);
extern Datum dist_span_span(const Span *s1, const Span *s2);
extern Datum distance_set_set(const Set *s1, const Set *s2);
extern Datum distance_set_value(const Set *s, Datum value);
extern Datum distance_span_span(const Span *s1, const Span *s2);
extern Datum distance_span_value(const Span *s, Datum value);
extern Datum distance_spanset_span(const SpanSet *ss, const Span *s);
extern Datum distance_spanset_spanset(const SpanSet *ss1, const SpanSet *ss2);
extern Datum distance_spanset_value(const SpanSet *ss, Datum value);
extern Datum distance_value_value(Datum l, Datum r, meosType basetype);

extern Span *spanbase_extent_transfn(Span *state, Datum value, meosType basetype);
extern Set *value_union_transfn(Set *state, Datum value, meosType basetype);

extern TBox *number_tstzspan_to_tbox(Datum d, meosType basetype, const Span *s);
extern TBox *number_timestamptz_to_tbox(Datum d, meosType basetype, TimestampTz t);
extern STBox *stbox_cp(const STBox *box);
extern void stbox_set(bool hasx, bool hasz, bool geodetic, int32 srid, double xmin, double xmax, double ymin, double ymax, double zmin, double zmax, const Span *s, STBox *box);
extern TBox *tbox_cp(const TBox *box);
extern void tbox_set(const Span *s, const Span *p, TBox *box);

extern STBox *box3d_to_stbox(const BOX3D *box);
extern STBox *gbox_to_stbox(const GBOX *box);
extern void float_set_tbox(double d, TBox *box);
/* extern STBox *gbox_to_stbox(const GBOX *box);  (repeated) */
extern bool geo_set_stbox(const GSERIALIZED *gs, STBox *box);
extern void geoarr_set_stbox(const Datum *values, int count, STBox *box);
extern void int_set_tbox(int i, TBox *box);
extern void number_set_tbox(Datum d, meosType basetype, TBox *box);
extern TBox *number_to_tbox(Datum value, meosType basetype);
extern void numset_set_tbox(const Set *s, TBox *box);
extern void numspan_set_tbox(const Span *span, TBox *box);
extern void numspanset_set_tbox(const SpanSet *ss, TBox *box);
extern void spatialset_set_stbox(const Set *set, STBox *box);
extern void stbox_set_box3d(const STBox *box, BOX3D *box3d);
extern void stbox_set_gbox(const STBox *box, GBOX *gbox);
extern void timestamptz_set_stbox(TimestampTz t, STBox *box);
extern void timestamptz_set_tbox(TimestampTz t, TBox *box);
extern void tstzset_set_stbox(const Set *s, STBox *box);
extern void tstzset_set_tbox(const Set *s, TBox *box);
extern void tstzspan_set_stbox(const Span *s, STBox *box);
extern void tstzspan_set_tbox(const Span *s, TBox *box);
extern void tstzspanset_set_stbox(const SpanSet *ss, STBox *box);
extern void tstzspanset_set_tbox(const SpanSet *ss, TBox *box);

extern TBox *tbox_shift_scale_value(const TBox *box, Datum shift, Datum width, meosType basetype, bool hasshift, bool haswidth);
extern void stbox_expand(const STBox *box1, STBox *box2);
extern void tbox_expand(const TBox *box1, TBox *box2);

extern bool inter_stbox_stbox(const STBox *box1, const STBox *box2, STBox *result);
extern bool inter_tbox_tbox(const TBox *box1, const TBox *box2, TBox *result);

extern char **geoarr_as_text(const Datum *geoarr, int count, int maxdd, bool extended);
extern char *tboolinst_as_mfjson(const TInstant *inst, bool with_bbox);
/* extern TInstant *tboolinst_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TInstant *tboolinst_in(const char *str);
extern char *tboolseq_as_mfjson(const TSequence *seq, bool with_bbox);
/* extern TSequence *tboolseq_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TSequence *tboolseq_in(const char *str, interpType interp);
extern char *tboolseqset_as_mfjson(const TSequenceSet *ss, bool with_bbox);
/* extern TSequenceSet *tboolseqset_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TSequenceSet *tboolseqset_in(const char *str);
extern Temporal *temporal_in(const char *str, meosType temptype);
extern char *temporal_out(const Temporal *temp, int maxdd);
extern char **temparr_out(const Temporal **temparr, int count, int maxdd);
extern char *tfloatinst_as_mfjson(const TInstant *inst, bool with_bbox, int precision);
/* extern TInstant *tfloatinst_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TInstant *tfloatinst_in(const char *str);
extern char *tfloatseq_as_mfjson(const TSequence *seq, bool with_bbox, int precision);
/* extern TSequence *tfloatseq_from_mfjson(json_object *mfjson, interpType interp);  (undefined type json_object) */
extern TSequence *tfloatseq_in(const char *str, interpType interp);
extern char *tfloatseqset_as_mfjson(const TSequenceSet *ss, bool with_bbox, int precision);
/* extern TSequenceSet *tfloatseqset_from_mfjson(json_object *mfjson, interpType interp);  (undefined type json_object) */
extern TSequenceSet *tfloatseqset_in(const char *str);
/* extern TInstant *tgeogpointinst_from_mfjson(json_object *mfjson, int srid);  (undefined type json_object) */
extern TInstant *tgeogpointinst_in(const char *str);
/* extern TSequence *tgeogpointseq_from_mfjson(json_object *mfjson, int srid, interpType interp);  (undefined type json_object) */
extern TSequence *tgeogpointseq_in(const char *str, interpType interp);
/* extern TSequenceSet *tgeogpointseqset_from_mfjson(json_object *mfjson, int srid, interpType interp);  (undefined type json_object) */
extern TSequenceSet *tgeogpointseqset_in(const char *str);
/* extern TInstant *tgeompointinst_from_mfjson(json_object *mfjson, int srid);  (undefined type json_object) */
extern TInstant *tgeompointinst_in(const char *str);
/* extern TSequence *tgeompointseq_from_mfjson(json_object *mfjson, int srid, interpType interp);  (undefined type json_object) */
extern TSequence *tgeompointseq_in(const char *str, interpType interp);
/* extern TSequenceSet *tgeompointseqset_from_mfjson(json_object *mfjson, int srid, interpType interp);  (undefined type json_object) */
extern TSequenceSet *tgeompointseqset_in(const char *str);
extern char *tinstant_as_mfjson(const TInstant *inst, bool with_bbox, int precision, char *srs);
/* extern TInstant *tinstant_from_mfjson(json_object *mfjson, bool isgeo, int srid, meosType temptype);  (undefined type json_object) */
extern TInstant *tinstant_in(const char *str, meosType temptype);
extern char *tinstant_out(const TInstant *inst, int maxdd);
extern char *tintinst_as_mfjson(const TInstant *inst, bool with_bbox);
/* extern TInstant *tintinst_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TInstant *tintinst_in(const char *str);
extern char *tintseq_as_mfjson(const TSequence *seq, bool with_bbox);
/* extern TSequence *tintseq_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TSequence *tintseq_in(const char *str, interpType interp);
extern char *tintseqset_as_mfjson(const TSequenceSet *ss, bool with_bbox);
/* extern TSequenceSet *tintseqset_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TSequenceSet *tintseqset_in(const char *str);
extern char **tpointarr_as_text(const Temporal **temparr, int count, int maxdd, bool extended);
extern char *tpointinst_as_mfjson(const TInstant *inst, bool with_bbox, int precision, char *srs);
extern char *tpointseq_as_mfjson(const TSequence *seq, bool with_bbox, int precision, char *srs);
extern char *tpointseqset_as_mfjson(const TSequenceSet *ss, bool with_bbox, int precision, char *srs);
extern char *tsequence_as_mfjson(const TSequence *seq, bool with_bbox, int precision, char *srs);
/* extern TSequence *tsequence_from_mfjson(json_object *mfjson, bool isgeo, int srid, meosType temptype, interpType interp);  (undefined type json_object) */
extern TSequence *tsequence_in(const char *str, meosType temptype, interpType interp);
extern char *tsequence_out(const TSequence *seq, int maxdd);
extern char *tsequenceset_as_mfjson(const TSequenceSet *ss, bool with_bbox, int precision, char *srs);
/* extern TSequenceSet *tsequenceset_from_mfjson(json_object *mfjson, bool isgeo, int srid, meosType temptype, interpType interp);  (undefined type json_object) */
extern TSequenceSet *tsequenceset_in(const char *str, meosType temptype, interpType interp);
extern char *tsequenceset_out(const TSequenceSet *ss, int maxdd);
extern char *ttextinst_as_mfjson(const TInstant *inst, bool with_bbox);
/* extern TInstant *ttextinst_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TInstant *ttextinst_in(const char *str);
extern char *ttextseq_as_mfjson(const TSequence *seq, bool with_bbox);
/* extern TSequence *ttextseq_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TSequence *ttextseq_in(const char *str, interpType interp);
extern char *ttextseqset_as_mfjson(const TSequenceSet *ss, bool with_bbox);
/* extern TSequenceSet *ttextseqset_from_mfjson(json_object *mfjson);  (undefined type json_object) */
extern TSequenceSet *ttextseqset_in(const char *str);
extern Temporal *temporal_from_mfjson(const char *mfjson, meosType temptype);

extern Temporal *temporal_cp(const Temporal *temp);
extern Temporal *temporal_from_base_temp(Datum value, meosType temptype, const Temporal *temp);
extern TInstant *tinstant_copy(const TInstant *inst);
extern TInstant *tinstant_make(Datum value, meosType temptype, TimestampTz t);
extern TInstant *tinstant_make_free(Datum value, meosType temptype, TimestampTz t);
extern TSequence *tpointseq_make_coords(const double *xcoords, const double *ycoords, const double *zcoords, const TimestampTz *times, int count, int32 srid, bool geodetic, bool lower_inc, bool upper_inc, interpType interp, bool normalize);
extern TSequence *tsequence_copy(const TSequence *seq);
extern TSequence *tsequence_from_base_tstzset(Datum value, meosType temptype, const Set *ss);
extern TSequence *tsequence_from_base_tstzspan(Datum value, meosType temptype, const Span *s, interpType interp);
extern TSequence *tsequence_make_exp(const TInstant **instants, int count, int maxcount, bool lower_inc, bool upper_inc, interpType interp, bool normalize);
extern TSequence *tsequence_make_free(TInstant **instants, int count, bool lower_inc, bool upper_inc, interpType interp, bool normalize);
extern TSequenceSet *tsequenceset_copy(const TSequenceSet *ss);
extern TSequenceSet *tseqsetarr_to_tseqset(TSequenceSet **seqsets, int count, int totalseqs);
extern TSequenceSet *tsequenceset_from_base_tstzspanset(Datum value, meosType temptype, const SpanSet *ss, interpType interp);
extern TSequenceSet *tsequenceset_make_exp(const TSequence **sequences, int count, int maxcount, bool normalize);
extern TSequenceSet *tsequenceset_make_free(TSequence **sequences, int count, bool normalize);

extern void temporal_set_tstzspan(const Temporal *temp, Span *s);
extern void tinstant_set_tstzspan(const TInstant *inst, Span *s);
extern Span *tnumber_span(const Temporal *temp);
extern void tsequence_set_tstzspan(const TSequence *seq, Span *s);
extern void tsequenceset_set_tstzspan(const TSequenceSet *ss, Span *s);

extern Datum temporal_end_value(const Temporal *temp);
extern const TInstant **temporal_insts(const Temporal *temp, int *count);
extern Datum temporal_max_value(const Temporal *temp);
extern size_t temporal_mem_size(const Temporal *temp);
extern Datum temporal_min_value(const Temporal *temp);
extern const TSequence **temporal_seqs(const Temporal *temp, int *count);
extern void temporal_set_bbox(const Temporal *temp, void *box);
/* extern void temporal_set_tstzspan(const Temporal *temp, Span *s);  (repeated) */
/* extern const TSequence **temporal_seqs(const Temporal *temp, int *count);  (repeated) */
extern Datum temporal_start_value (const Temporal *temp);
extern Datum *temporal_vals(const Temporal *temp, int *count);
extern Datum *temporal_values(const Temporal *temp, int *count);
extern uint32 tinstant_hash(const TInstant *inst);
extern const TInstant **tinstant_insts(const TInstant *inst, int *count);
extern void tinstant_set_bbox(const TInstant *inst, void *box);
extern SpanSet *tinstant_time(const TInstant *inst);
extern TimestampTz *tinstant_timestamps(const TInstant *inst, int *count);
extern Datum tinstant_val(const TInstant *inst);
extern Datum tinstant_value(const TInstant *inst);
extern bool tinstant_value_at_timestamptz(const TInstant *inst, TimestampTz t, Datum *result);
extern Datum *tinstant_vals(const TInstant *inst, int *count);
extern void tnumber_set_span(const Temporal *temp, Span *span);
extern SpanSet *tnumberinst_valuespans(const TInstant *inst);
extern SpanSet *tnumberseq_valuespans(const TSequence *seq);
extern SpanSet *tnumberseqset_valuespans(const TSequenceSet *ss);
extern Interval *tsequence_duration(const TSequence *seq);
extern TimestampTz tsequence_end_timestamptz(const TSequence *seq);
extern uint32 tsequence_hash(const TSequence *seq);
extern const TInstant **tsequence_insts(const TSequence *seq);
extern const TInstant *tsequence_max_inst(const TSequence *seq);
extern Datum tsequence_max_val(const TSequence *seq);
extern const TInstant *tsequence_min_inst(const TSequence *seq);
extern Datum tsequence_min_val(const TSequence *seq);
extern TSequence **tsequence_segments(const TSequence *seq, int *count);
extern const TSequence **tsequence_seqs(const TSequence *seq, int *count);
extern void tsequence_set_bbox(const TSequence *seq, void *box);
extern void tsequence_expand_bbox(TSequence *seq, const TInstant *inst);
extern TimestampTz tsequence_start_timestamptz(const TSequence *seq);
extern SpanSet *tsequence_time(const TSequence *seq);
extern TimestampTz *tsequence_timestamps(const TSequence *seq, int *count);
extern bool tsequence_value_at_timestamptz(const TSequence *seq, TimestampTz t, bool strict, Datum *result);
extern Datum *tsequence_vals(const TSequence *seq, int *count);
extern Interval *tsequenceset_duration(const TSequenceSet *ss, bool boundspan);
extern TimestampTz tsequenceset_end_timestamptz(const TSequenceSet *ss);
extern uint32 tsequenceset_hash(const TSequenceSet *ss);
extern const TInstant *tsequenceset_inst_n(const TSequenceSet *ss, int n);
extern const TInstant **tsequenceset_insts(const TSequenceSet *ss);
extern const TInstant *tsequenceset_max_inst(const TSequenceSet *ss);
extern Datum tsequenceset_max_val(const TSequenceSet *ss);
extern const TInstant *tsequenceset_min_inst(const TSequenceSet *ss);
extern Datum tsequenceset_min_val(const TSequenceSet *ss);
extern int tsequenceset_num_instants(const TSequenceSet *ss);
extern int tsequenceset_num_timestamps(const TSequenceSet *ss);
extern TSequence **tsequenceset_segments(const TSequenceSet *ss, int *count);
extern const TSequence **tsequenceset_seqs(const TSequenceSet *ss);
extern void tsequenceset_set_bbox(const TSequenceSet *ss, void *box);
extern TimestampTz tsequenceset_start_timestamptz(const TSequenceSet *ss);
extern SpanSet *tsequenceset_time(const TSequenceSet *ss);
/* extern Interval *tsequenceset_timespan(const TSequenceSet *ss);  (undefined) */
extern bool tsequenceset_timestamptz_n(const TSequenceSet *ss, int n, TimestampTz *result);
extern TimestampTz *tsequenceset_timestamps(const TSequenceSet *ss, int *count);
extern bool tsequenceset_value_at_timestamptz(const TSequenceSet *ss, TimestampTz t, bool strict, Datum *result);
extern Datum *tsequenceset_vals(const TSequenceSet *ss, int *count);

extern Temporal *temporal_compact(const Temporal *temp);
extern void temporal_restart(Temporal *temp, int count);
extern TSequence *temporal_tsequence(const Temporal *temp, interpType interp);
extern TSequenceSet *temporal_tsequenceset(const Temporal *temp, interpType interp);
extern TInstant *tinstant_shift_time(const TInstant *inst, const Interval *interv);
extern TSequence *tinstant_to_tsequence(const TInstant *inst, interpType interp);
extern TSequence *tinstant_to_tsequence_free(TInstant *inst, interpType interp);
extern TSequenceSet *tinstant_to_tsequenceset(const TInstant *inst, interpType interp);
extern Temporal *tnumber_shift_scale_value(const Temporal *temp, Datum shift, Datum width, bool hasshift, bool haswidth);
extern TInstant *tnumberinst_shift_value(const TInstant *inst, Datum shift);
extern TSequence *tnumberseq_shift_scale_value(const TSequence *seq, Datum shift, Datum width, bool hasshift, bool haswidth);
extern TSequenceSet *tnumberseqset_shift_scale_value(const TSequenceSet *ss, Datum start, Datum width, bool hasshift, bool haswidth);
extern TSequence *tsequence_compact(const TSequence *seq);
extern void tsequence_restart(TSequence *seq, int count);
extern Temporal *tsequence_set_interp(const TSequence *seq, interpType interp);
extern TSequence *tsequence_shift_scale_time(const TSequence *seq, const Interval *shift, const Interval *duration);
extern TSequence *tsequence_subseq(const TSequence *seq, int from, int to, bool lower_inc, bool upper_inc);
extern TInstant *tsequence_to_tinstant(const TSequence *seq);
extern TSequenceSet *tsequence_to_tsequenceset(const TSequence *seq);
extern TSequenceSet *tsequence_to_tsequenceset_free(TSequence *seq);
extern TSequenceSet *tsequence_to_tsequenceset_interp(const TSequence *seq, interpType interp);
extern TSequenceSet *tsequenceset_compact(const TSequenceSet *ss);
extern void tsequenceset_restart(TSequenceSet *ss, int count);
extern Temporal *tsequenceset_set_interp(const TSequenceSet *ss, interpType interp);
extern TSequenceSet *tsequenceset_shift_scale_time(const TSequenceSet *ss, const Interval *start, const Interval *duration);
extern TSequence *tsequenceset_to_discrete(const TSequenceSet *ss);
extern TSequenceSet *tsequenceset_to_linear(const TSequenceSet *ss);
extern TSequenceSet *tsequenceset_to_step(const TSequenceSet *ss);
extern TInstant *tsequenceset_to_tinstant(const TSequenceSet *ss);
extern TSequence *tsequenceset_to_tsequence(const TSequenceSet *ss);

extern Temporal *tinstant_merge(const TInstant *inst1, const TInstant *inst2);
extern Temporal *tinstant_merge_array(const TInstant **instants, int count);
extern Temporal *tsequence_append_tinstant(TSequence *seq, const TInstant *inst, double maxdist, const Interval *maxt, bool expand);
extern Temporal *tsequence_append_tsequence(TSequence *seq1, const TSequence *seq2, bool expand);
extern Temporal *tsequence_delete_timestamptz(const TSequence *seq, TimestampTz t, bool connect);
extern Temporal *tsequence_delete_tstzset(const TSequence *seq, const Set *s, bool connect);
extern Temporal *tsequence_delete_tstzspan(const TSequence *seq, const Span *s, bool connect);
extern Temporal *tsequence_delete_tstzspanset(const TSequence *seq, const SpanSet *ss, bool connect);
extern Temporal *tsequence_insert(const TSequence *seq1, const TSequence *seq2, bool connect);
extern Temporal *tsequence_merge(const TSequence *seq1, const TSequence *seq2);
extern Temporal *tsequence_merge_array(const TSequence **sequences, int count);
extern TSequenceSet *tsequenceset_append_tinstant(TSequenceSet *ss, const TInstant *inst, double maxdist, const Interval *maxt, bool expand);
extern TSequenceSet *tsequenceset_append_tsequence(TSequenceSet *ss, const TSequence *seq, bool expand);
extern TSequenceSet *tsequenceset_delete_timestamptz(const TSequenceSet *ss, TimestampTz t);
extern TSequenceSet *tsequenceset_delete_tstzset(const TSequenceSet *ss, const Set *s);
extern TSequenceSet *tsequenceset_delete_tstzspan(const TSequenceSet *ss, const Span *s);
extern TSequenceSet *tsequenceset_delete_tstzspanset(const TSequenceSet *ss, const SpanSet *ps);
extern TSequenceSet *tsequenceset_insert(const TSequenceSet *ss1, const TSequenceSet *ss2);
extern TSequenceSet *tsequenceset_merge(const TSequenceSet *ss1, const TSequenceSet *ss2);
extern TSequenceSet *tsequenceset_merge_array(const TSequenceSet **seqsets, int count);

/* extern void tsequence_expand_bbox(TSequence *seq, const TInstant *inst);  (repeated) */
/* extern void tsequence_set_bbox(const TSequence *seq, void *box);  (repeated) */
extern void tsequenceset_expand_bbox(TSequenceSet *ss, const TSequence *seq);
/* extern void tsequenceset_set_bbox(const TSequenceSet *ss, void *box);  (repeated) */

extern TSequence *tdiscseq_restrict_minmax(const TSequence *seq, bool min, bool atfunc);
extern TSequenceSet *tcontseq_restrict_minmax(const TSequence *seq, bool min, bool atfunc);
extern bool temporal_bbox_restrict_set(const Temporal *temp, const Set *set);
extern Temporal *temporal_restrict_minmax(const Temporal *temp, bool min, bool atfunc);
extern Temporal *temporal_restrict_timestamptz(const Temporal *temp, TimestampTz t, bool atfunc);
extern Temporal *temporal_restrict_tstzset(const Temporal *temp, const Set *s, bool atfunc);
extern Temporal *temporal_restrict_tstzspan(const Temporal *temp, const Span *s, bool atfunc);
extern Temporal *temporal_restrict_tstzspanset(const Temporal *temp, const SpanSet *ss, bool atfunc);
extern Temporal *temporal_restrict_value(const Temporal *temp, Datum value, bool atfunc);
extern Temporal *temporal_restrict_values(const Temporal *temp, const Set *set, bool atfunc);
extern bool temporal_value_at_timestamptz(const Temporal *temp, TimestampTz t, bool strict, Datum *result);
extern TInstant *tinstant_restrict_tstzspan(const TInstant *inst, const Span *period, bool atfunc);
extern TInstant *tinstant_restrict_tstzspanset(const TInstant *inst, const SpanSet *ss, bool atfunc);
extern TInstant *tinstant_restrict_timestamptz(const TInstant *inst, TimestampTz t, bool atfunc);
extern TInstant *tinstant_restrict_tstzset(const TInstant *inst, const Set *s, bool atfunc);
extern TInstant *tinstant_restrict_value(const TInstant *inst, Datum value, bool atfunc);
extern TInstant *tinstant_restrict_values(const TInstant *inst, const Set *set, bool atfunc);
extern Temporal *tnumber_restrict_span(const Temporal *temp, const Span *span, bool atfunc);
extern Temporal *tnumber_restrict_spanset(const Temporal *temp, const SpanSet *ss, bool atfunc);
extern TInstant *tnumberinst_restrict_span(const TInstant *inst, const Span *span, bool atfunc);
extern TInstant *tnumberinst_restrict_spanset(const TInstant *inst, const SpanSet *ss, bool atfunc);
extern TSequenceSet *tnumberseqset_restrict_span(const TSequenceSet *ss, const Span *span, bool atfunc);
extern TSequenceSet *tnumberseqset_restrict_spanset(const TSequenceSet *ss, const SpanSet *spanset, bool atfunc);
extern Temporal *tpoint_restrict_geom_time(const Temporal *temp, const GSERIALIZED *gs, const Span *zspan, const Span *period, bool atfunc);
extern Temporal *tpoint_restrict_stbox(const Temporal *temp, const STBox *box, bool border_inc, bool atfunc);
extern TInstant *tpointinst_restrict_geom_time(const TInstant *inst, const GSERIALIZED *gs, const Span *zspan, const Span *period, bool atfunc);
extern TInstant *tpointinst_restrict_stbox(const TInstant *inst, const STBox *box, bool border_inc, bool atfunc);
extern Temporal *tpointseq_restrict_geom_time(const TSequence *seq, const GSERIALIZED *gs, const Span *zspan, const Span *period, bool atfunc);
extern Temporal *tpointseq_restrict_stbox(const TSequence *seq, const STBox *box, bool border_inc, bool atfunc);
extern TSequenceSet *tpointseqset_restrict_geom_time(const TSequenceSet *ss, const GSERIALIZED *gs, const Span *zspan, const Span *period, bool atfunc);
extern TSequenceSet *tpointseqset_restrict_stbox(const TSequenceSet *ss, const STBox *box, bool border_inc, bool atfunc);
extern TInstant *tsequence_at_timestamptz(const TSequence *seq, TimestampTz t);
extern Temporal *tsequence_restrict_tstzspan(const TSequence *seq, const Span *s, bool atfunc);
extern Temporal *tsequence_restrict_tstzspanset(const TSequence *seq, const SpanSet *ss, bool atfunc);
extern TSequenceSet *tsequenceset_restrict_minmax(const TSequenceSet *ss, bool min, bool atfunc);
extern TSequenceSet *tsequenceset_restrict_tstzspan(const TSequenceSet *ss, const Span *s, bool atfunc);
extern TSequenceSet *tsequenceset_restrict_tstzspanset(const TSequenceSet *ss, const SpanSet *ps, bool atfunc);
extern Temporal *tsequenceset_restrict_timestamptz(const TSequenceSet *ss, TimestampTz t, bool atfunc);
extern Temporal *tsequenceset_restrict_tstzset(const TSequenceSet *ss, const Set *s, bool atfunc);
extern TSequenceSet *tsequenceset_restrict_value(const TSequenceSet *ss, Datum value, bool atfunc);
extern TSequenceSet *tsequenceset_restrict_values(const TSequenceSet *ss, const Set *s, bool atfunc);

extern int tinstant_cmp(const TInstant *inst1, const TInstant *inst2);
extern bool tinstant_eq(const TInstant *inst1, const TInstant *inst2);
extern int tsequence_cmp(const TSequence *seq1, const TSequence *seq2);
extern bool tsequence_eq(const TSequence *seq1, const TSequence *seq2);
extern int tsequenceset_cmp(const TSequenceSet *ss1, const TSequenceSet *ss2);
extern bool tsequenceset_eq(const TSequenceSet *ss1, const TSequenceSet *ss2);

extern int always_eq_base_temporal(Datum value, const Temporal *temp);
extern int always_eq_temporal_base(const Temporal *temp, Datum value);
/* extern int always_eq_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_eq_tpointinst_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_eq_tpointseq_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_eq_tpointseqset_base(const TSequenceSet *ss, Datum value);  (undefined) */
/* extern int always_eq_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_eq_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int always_ne_base_temporal(Datum value, const Temporal *temp);
extern int always_ne_temporal_base(const Temporal *temp, Datum value);
/* extern int always_ne_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_ne_tpointinst_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_ne_tpointseq_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_ne_tpointseqset_base(const TSequenceSet *ss, Datum value);  (undefined) */
/* extern int always_ne_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_ne_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int always_ge_base_temporal(Datum value, const Temporal *temp);
extern int always_ge_temporal_base(const Temporal *temp, Datum value);
/* extern int always_ge_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_ge_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_ge_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int always_gt_base_temporal(Datum value, const Temporal *temp);
extern int always_gt_temporal_base(const Temporal *temp, Datum value);
/* extern int always_gt_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_gt_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_gt_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int always_le_base_temporal(Datum value, const Temporal *temp);
extern int always_le_temporal_base(const Temporal *temp, Datum value);
/* extern int always_le_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_le_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_le_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int always_lt_base_temporal(Datum value, const Temporal *temp);
extern int always_lt_temporal_base(const Temporal *temp, Datum value);
/* extern int always_lt_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int always_lt_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int always_lt_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int ever_eq_base_temporal(Datum value, const Temporal *temp);
extern int ever_eq_temporal_base(const Temporal *temp, Datum value);
/* extern int ever_eq_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int ever_eq_tpointinst_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int ever_eq_tpointseq_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int ever_eq_tpointseqset_base(const TSequenceSet *ss, Datum value);  (undefined) */
/* extern int ever_eq_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int ever_eq_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int ever_ne_base_temporal(Datum value, const Temporal *temp);
extern int ever_ne_temporal_base(const Temporal *temp, Datum value);
/* extern int ever_ne_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int ever_ne_tpointinst_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int ever_ne_tpointseq_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int ever_ne_tpointseqset_base(const TSequenceSet *ss, Datum value);  (undefined) */
/* extern int ever_ne_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int ever_ne_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int ever_ge_base_temporal(Datum value, const Temporal *temp);
extern int ever_ge_temporal_base(const Temporal *temp, Datum value);
/* extern int ever_ge_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int ever_ge_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int ever_ge_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int ever_gt_base_temporal(Datum value, const Temporal *temp);
extern int ever_gt_temporal_base(const Temporal *temp, Datum value);
/* extern int ever_gt_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int ever_gt_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int ever_gt_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int ever_le_base_temporal(Datum value, const Temporal *temp);
extern int ever_le_temporal_base(const Temporal *temp, Datum value);
/* extern int ever_le_tinstant_base(const TInstant *inst, Datum value);  (undefined) */
/* extern int ever_le_tsequence_base(const TSequence *seq, Datum value);  (undefined) */
/* extern int ever_le_tsequenceset_base(const TSequenceSet *ss, Datum value);  (undefined) */
extern int ever_lt_base_temporal(Datum value, const Temporal *temp);
extern int ever_lt_temporal_base(const Temporal *temp, Datum value);

extern TSequence *tfloatseq_derivative(const TSequence *seq);
extern TSequenceSet *tfloatseqset_derivative(const TSequenceSet *ss);
extern TInstant *tnumberinst_abs(const TInstant *inst);
extern TSequence *tnumberseq_abs(const TSequence *seq);
extern TSequence *tnumberseq_angular_difference(const TSequence *seq);
extern TSequence *tnumberseq_delta_value(const TSequence *seq);
extern TSequenceSet *tnumberseqset_abs(const TSequenceSet *ss);
extern TSequence *tnumberseqset_angular_difference(const TSequenceSet *ss);
extern TSequenceSet *tnumberseqset_delta_value(const TSequenceSet *ss);

extern Temporal *distance_tnumber_number(const Temporal *temp, Datum value);
extern Datum nad_tbox_tbox(const TBox *box1, const TBox *box2);
extern Datum nad_tnumber_number(const Temporal *temp, Datum value);
extern Datum nad_tnumber_tbox(const Temporal *temp, const TBox *box);
extern Datum nad_tnumber_tnumber(const Temporal *temp1, const Temporal *temp2);

extern int tpointinst_srid(const TInstant *inst);
extern GSERIALIZED *tpointseq_trajectory(const TSequence *seq);
extern TSequenceSet *tpointseq_azimuth(const TSequence *seq);
extern TSequence *tpointseq_cumulative_length(const TSequence *seq, double prevlength);
extern bool tpointseq_is_simple(const TSequence *seq);
extern double tpointseq_length(const TSequence *seq);
extern TSequence *tpointseq_speed(const TSequence *seq);
extern int tpointseq_srid(const TSequence *seq);
extern STBox *tpointseq_stboxes(const TSequence *seq, int *count);
extern TSequenceSet *tpointseqset_azimuth(const TSequenceSet *ss);
extern TSequenceSet *tpointseqset_cumulative_length(const TSequenceSet *ss);
extern bool tpointseqset_is_simple(const TSequenceSet *ss);
extern double tpointseqset_length(const TSequenceSet *ss);
extern TSequenceSet *tpointseqset_speed(const TSequenceSet *ss);
extern int tpointseqset_srid(const TSequenceSet *ss);
extern STBox *tpointseqset_stboxes(const TSequenceSet *ss, int *count);
extern GSERIALIZED *tpointseqset_trajectory(const TSequenceSet *ss);
extern Temporal *tpoint_get_coord(const Temporal *temp, int coord);

extern TInstant *tgeompointinst_tgeogpointinst(const TInstant *inst, bool oper);
extern TSequence *tgeompointseq_tgeogpointseq(const TSequence *seq, bool oper);
extern TSequenceSet *tgeompointseqset_tgeogpointseqset(const TSequenceSet *ss, bool oper);
extern Temporal *tgeompoint_tgeogpoint(const Temporal *temp, bool oper);
extern TInstant *tpointinst_set_srid(const TInstant *inst, int32 srid);
extern TSequence **tpointseq_make_simple(const TSequence *seq, int *count);
extern TSequence *tpointseq_set_srid(const TSequence *seq, int32 srid);
extern TSequence **tpointseqset_make_simple(const TSequenceSet *ss, int *count);
extern TSequenceSet *tpointseqset_set_srid(const TSequenceSet *ss, int32 srid);

extern double tnumberseq_integral(const TSequence *seq);
extern double tnumberseq_twavg(const TSequence *seq);
extern double tnumberseqset_integral(const TSequenceSet *ss);
extern double tnumberseqset_twavg(const TSequenceSet *ss);
extern GSERIALIZED *tpointseq_twcentroid(const TSequence *seq);
extern GSERIALIZED *tpointseqset_twcentroid(const TSequenceSet *ss);

/* extern Temporal *temporal_compact(const Temporal *temp);  (repeated) */
/* extern TSequence *tsequence_compact(const TSequence *seq);  (repeated) */
/* extern TSequenceSet *tsequenceset_compact(const TSequenceSet *ss);  (repeated) */

extern void skiplist_free(SkipList *list);
extern Temporal *temporal_app_tinst_transfn(Temporal *state, const TInstant *inst, double maxdist, Interval *maxt);
extern Temporal *temporal_app_tseq_transfn(Temporal *state, const TSequence *seq);
/* extern double tnumberseq_integral(const TSequence *seq);  (repeated) */
/* extern double tnumberseq_twavg(const TSequence *seq);  (repeated) */
/* extern double tnumberseqset_integral(const TSequenceSet *ss);  (repeated) */
/* extern double tnumberseqset_twavg(const TSequenceSet *ss);  (repeated) */
/* extern GSERIALIZED *tpointseq_twcentroid(const TSequence *seq);  (repeated) */
/* extern GSERIALIZED *tpointseqset_twcentroid(const TSequenceSet *ss);  (repeated) */

extern Temporal **tnumber_value_split(const Temporal *temp, Datum size, Datum origin, Datum **buckets, int *count);
extern TBox *tbox_tile(Datum value, TimestampTz t, Datum vsize, Interval *duration, Datum vorigin, TimestampTz torigin, meosType basetype);

 


extern "Python" void py_error_handler(int, int, char*);