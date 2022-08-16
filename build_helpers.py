ADDITIONAL_DEFINITIONS = (
    """/*****************************************************************************
 * Type definitions
 *****************************************************************************/"""
    ,
    """
/*****************************************************************************
 * Additional definitions
 *****************************************************************************/

typedef struct varlena
{
    char		vl_len_[4];		/* Do not touch this field directly! */
    char		vl_dat[];	/* Data content is here */
} varlena;

typedef varlena text;
typedef struct varlena bytea;

typedef struct
{
    uint32_t size; /* For PgSQL use only, use VAR* macros to manipulate. */
    uint8_t srid[3]; /* 24 bits of SRID */
    uint8_t gflags; /* HasZ, HasM, HasBBox, IsGeodetic */
    uint8_t data[]; /* See gserialized.txt */
    ...;
} GSERIALIZED;

typedef uint16_t lwflags_t;

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
        GBOX *bbox;
        void *data;
        int32_t srid;
        lwflags_t flags;
        uint8_t type;
        char pad[1]; /* Padding to 24 bytes (unused) */
} LWGEOM;

typedef signed char int8;
typedef signed short int16;
typedef signed int int32;
typedef long int int64;

typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned long int uint64;

typedef int32 DateADT;
typedef int64 Timestamp;
typedef int64 TimestampTz;
typedef int64 TimeOffset;
typedef struct
{
    TimeOffset	time;			/* all time units other than days, months and
								 * years */
    int32		day;			/* days, after time for alignment */
    int32		month;			/* months and years, after time for alignment */
} Interval;

typedef uintptr_t Datum;

extern char *text2cstring(const text *textptr);
extern text *cstring2text(const char *cstring);

extern LWGEOM *lwgeom_from_gserialized(const GSERIALIZED *g);

/*****************************************************************************
 * Type definitions
 *****************************************************************************/"""
)
