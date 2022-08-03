/*****************************************************************************
 * Additional Type definitions
 *****************************************************************************/

typedef struct varlena
{
	char		vl_len_[4];		/* Do not touch this field directly! */
	char		vl_dat[];	/* Data content is here */
} varlena;

typedef varlena text;

typedef struct
{
        uint32_t size; /* For PgSQL use only, use VAR* macros to manipulate. */
        uint8_t srid[3]; /* 24 bits of SRID */
        uint8_t flags; /* HasZ, HasM, HasBBox, IsGeodetic, IsReadOnly */
        uint8_t data[1]; /* See gserialized.txt */
} GSERIALIZED;

typedef signed char int8;
typedef signed short int16;
typedef signed int int32;
typedef long int int64;

typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned long int uint64;

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

/*****************************************************************************
 * Type definitions
 *****************************************************************************/

/**
 * Structure to represent spans (a.k.a. ranges)
 */
typedef struct
{
  Datum lower;          /**< lower bound value */
  Datum upper;          /**< upper bound value */
  bool lower_inc;       /**< lower bound is inclusive (vs exclusive) */
  bool upper_inc;       /**< upper bound is inclusive (vs exclusive) */
  uint8 spantype;       /**< span type */
  uint8 basetype;       /**< span basetype */
} Span;

/**
 * Make the Period type as a Span type for facilitating the manipulation of
 * the time dimension
 */
typedef Span Period;

/**
 * Structure to represent timestamp sets
 */
typedef struct
{
  int32 vl_len_;        /**< Varlena header (do not touch directly!) */
  int32 count;          /**< Number of TimestampTz elements */
  Period period;        /**< Bounding period */
  TimestampTz elems[1]; /**< Beginning of variable-length data */
} TimestampSet;

/**
 * Structure to represent period sets
 */
typedef struct
{
  int32 vl_len_;        /**< Varlena header (do not touch directly!) */
  int32 count;          /**< Number of Period elements */
  Period period;        /**< Bounding period */
  Period elems[1];      /**< Beginning of variable-length data */
} PeriodSet;

/**
 * Structure to represent temporal boxes
 */
typedef struct
{
  double      xmin;   /**< minimum number value */
  double      xmax;   /**< maximum number value */
  TimestampTz tmin;   /**< minimum timestamp */
  TimestampTz tmax;   /**< maximum timestamp */
  int16       flags;  /**< flags */
} TBOX;

/**
 * Structure to represent spatiotemporal boxes
 */
typedef struct
{
  double      xmin;   /**< minimum x value */
  double      xmax;   /**< maximum x value */
  double      ymin;   /**< minimum y value */
  double      ymax;   /**< maximum y value */
  double      zmin;   /**< minimum z value */
  double      zmax;   /**< maximum z value */
  TimestampTz tmin;   /**< minimum timestamp */
  TimestampTz tmax;   /**< maximum timestamp */
  int32       srid;   /**< SRID */
  int16       flags;  /**< flags */
} STBOX;

/**
 * Structure to represent the common structure of temporal values of
 * any temporal subtype
 */
typedef struct
{
  int32         vl_len_;      /**< Varlena header (do not touch directly!) */
  uint8         temptype;     /**< Temporal type */
  uint8         subtype;      /**< Temporal subtype */
  int16         flags;        /**< Flags */
  /* variable-length data follows, if any */
} Temporal;

/**
 * Structure to represent temporal values of instant subtype
 */
typedef struct
{
  int32         vl_len_;      /**< Varlena header (do not touch directly!) */
  uint8         temptype;     /**< Temporal type */
  uint8         subtype;      /**< Temporal subtype */
  int16         flags;        /**< Flags */
  TimestampTz   t;            /**< Timestamp (8 bytes) */
  /* variable-length data follows */
} TInstant;

/**
 * Structure to represent temporal values of instant set subtype
 */
typedef struct
{
  int32         vl_len_;      /**< Varlena header (do not touch directly!) */
  uint8         temptype;     /**< Temporal type */
  uint8         subtype;      /**< Temporal subtype */
  int16         flags;        /**< Flags */
  int32         count;        /**< Number of TInstant elements */
  int16         bboxsize;     /**< Size of the bounding box */
  /**< beginning of variable-length data */
} TInstantSet;

/**
 * Structure to represent temporal values of sequence subtype
 */
typedef struct
{
  int32         vl_len_;      /**< Varlena header (do not touch directly!) */
  uint8         temptype;     /**< Temporal type */
  uint8         subtype;      /**< Temporal subtype */
  int16         flags;        /**< Flags */
  int32         count;        /**< Number of TInstant elements */
  int16         bboxsize;     /**< Size of the bounding box */
  Period        period;       /**< Time span (24 bytes) */
  /**< beginning of variable-length data */
} TSequence;

/**
 * Structure to represent temporal values of sequence set subtype
 */
typedef struct
{
  int32         vl_len_;      /**< Varlena header (do not touch directly!) */
  uint8         temptype;     /**< Temporal type */
  uint8         subtype;      /**< Temporal subtype */
  int16         flags;        /**< Flags */
  int32         count;        /**< Number of TSequence elements */
  int32         totalcount;   /**< Total number of TInstant elements in all TSequence elements */
  int16         bboxsize;     /**< Size of the bounding box */
  /**< beginning of variable-length data */
} TSequenceSet;

/**
 * Struct for storing a similarity match
 */
typedef struct
{
  int i;
  int j;
} Match;

