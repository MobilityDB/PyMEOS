LIBLWGEOM_DEFINITIONS = """
typedef uint16_t lwflags_t;

/******************************************************************/

typedef struct {
    double afac, bfac, cfac, dfac, efac, ffac, gfac, hfac, ifac, xoff, yoff, zoff;
} AFFINE;

/******************************************************************/

typedef struct
{
    double xmin, ymin, zmin;
    double xmax, ymax, zmax;
    int32_t srid;
}
BOX3D;

/******************************************************************
* GBOX structure.
* We include the flags (information about dimensionality),
* so we don't have to constantly pass them
* into functions that use the GBOX.
*/
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


/******************************************************************
* SPHEROID
*
*  Standard definition of an ellipsoid (what wkt calls a spheroid)
*    f = (a-b)/a
*    e_sq = (a*a - b*b)/(a*a)
*    b = a - fa
*/
typedef struct
{
    double  a;  /* semimajor axis */
    double  b;  /* semiminor axis b = (a - fa) */
    double  f;  /* flattening f = (a-b)/a */
    double  e;  /* eccentricity (first) */
    double  e_sq;   /* eccentricity squared (first) e_sq = (a*a-b*b)/(a*a) */
    double  radius;  /* spherical average radius = (2*a+b)/3 */
    char    name[20];  /* name of ellipse */
}
SPHEROID;

/******************************************************************
* POINT2D, POINT3D, POINT3DM, POINT4D
*/
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

/******************************************************************
*  POINTARRAY
*  Point array abstracts a lot of the complexity of points and point lists.
*  It handles 2d/3d translation
*    (2d points converted to 3d will have z=0 or NaN)
*  DO NOT MIX 2D and 3D POINTS! EVERYTHING* is either one or the other
*/
typedef struct
{
    uint32_t npoints;   /* how many points we are currently storing */
    uint32_t maxpoints; /* how many points we have space for in serialized_pointlist */

    /* Use FLAGS_* macros to handle */
    lwflags_t flags;

    /* Array of POINT 2D, 3D or 4D, possibly misaligned. */
    uint8_t *serialized_pointlist;
}
POINTARRAY;

/******************************************************************
* GSERIALIZED
*/

typedef struct
{
    uint32_t size; /* For PgSQL use only, use VAR* macros to manipulate. */
    uint8_t srid[3]; /* 24 bits of SRID */
    uint8_t gflags; /* HasZ, HasM, HasBBox, IsGeodetic */
    uint8_t data[1]; /* See gserialized.txt */
} GSERIALIZED;

/******************************************************************
* LWGEOM (any geometry type)
*
* Abstract type, note that 'type', 'bbox' and 'srid' are available in
* all geometry variants.
*/
typedef struct
{
    GBOX *bbox;
    void *data;
    int32_t srid;
    lwflags_t flags;
    uint8_t type;
    char pad[1]; /* Padding to 24 bytes (unused) */
}
LWGEOM;

/* POINTYPE */
typedef struct
{
    GBOX *bbox;
    POINTARRAY *point;  /* hide 2d/3d (this will be an array of 1 point) */
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* POINTTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
}
LWPOINT; /* "light-weight point" */

/* LINETYPE */
typedef struct
{
    GBOX *bbox;
    POINTARRAY *points; /* array of POINT3D */
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* LINETYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
}
LWLINE; /* "light-weight line" */

/* TRIANGLE */
typedef struct
{
    GBOX *bbox;
    POINTARRAY *points;
    int32_t srid;
    lwflags_t flags;
    uint8_t type;
    char pad[1]; /* Padding to 24 bytes (unused) */
}
LWTRIANGLE;

/* CIRCSTRINGTYPE */
typedef struct
{
    GBOX *bbox;
    POINTARRAY *points; /* array of POINT(3D/3DM) */
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* CIRCSTRINGTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
}
LWCIRCSTRING; /* "light-weight circularstring" */

/* POLYGONTYPE */
typedef struct
{
    GBOX *bbox;
    POINTARRAY **rings; /* list of rings (list of points) */
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* POLYGONTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t nrings;   /* how many rings we are currently storing */
    uint32_t maxrings; /* how many rings we have space for in **rings */
}
LWPOLY; /* "light-weight polygon" */

/* MULTIPOINTTYPE */
typedef struct
{
    GBOX *bbox;
    LWPOINT **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* MULTYPOINTTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWMPOINT;

/* MULTILINETYPE */
typedef struct
{
    GBOX *bbox;
    LWLINE **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* MULTILINETYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWMLINE;

/* MULTIPOLYGONTYPE */
typedef struct
{
    GBOX *bbox;
    LWPOLY **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* MULTIPOLYGONTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWMPOLY;

/* COLLECTIONTYPE */
typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* COLLECTIONTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWCOLLECTION;

/* COMPOUNDTYPE */
typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* COLLECTIONTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWCOMPOUND; /* "light-weight compound line" */

/* CURVEPOLYTYPE */
typedef struct
{
    GBOX *bbox;
    LWGEOM **rings;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* CURVEPOLYTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t nrings;    /* how many rings we are currently storing */
    uint32_t maxrings;  /* how many rings we have space for in **rings */
}
LWCURVEPOLY; /* "light-weight polygon" */

/* MULTICURVE */
typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* MULTICURVE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWMCURVE;

/* MULTISURFACETYPE */
typedef struct
{
    GBOX *bbox;
    LWGEOM **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* MULTISURFACETYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWMSURFACE;

/* POLYHEDRALSURFACETYPE */
typedef struct
{
    GBOX *bbox;
    LWPOLY **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* POLYHEDRALSURFACETYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWPSURFACE;

/* TINTYPE */
typedef struct
{
    GBOX *bbox;
    LWTRIANGLE **geoms;
    int32_t srid;
    lwflags_t flags;
    uint8_t type; /* TINTYPE */
    char pad[1]; /* Padding to 24 bytes (unused) */
    uint32_t ngeoms;   /* how many geometries we are currently storing */
    uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
}
LWTIN;

extern LWPOINT *lwpoint_make(int32_t srid, int hasz, int hasm, const POINT4D *p);

extern LWGEOM *lwgeom_from_gserialized(const GSERIALIZED *g);
extern GSERIALIZED *gserialized_from_lwgeom(LWGEOM *geom, size_t *size);

extern static inline LWPOINT *lwgeom_as_lwpoint(const LWGEOM *lwgeom);

extern int32_t lwgeom_get_srid(const LWGEOM *geom);

extern double lwpoint_get_x(const LWPOINT *point);
extern double lwpoint_get_y(const LWPOINT *point);
extern double lwpoint_get_z(const LWPOINT *point);
extern double lwpoint_get_m(const LWPOINT *point);

extern int lwgeom_has_z(const LWGEOM *geom);
extern int lwgeom_has_m(const LWGEOM *geom);
"""

LIBLWGEOM_DEFINITIONS_2 = """

typedef struct {
	double afac, bfac, cfac, dfac, efac, ffac, gfac, hfac, ifac, xoff, yoff, zoff;
} AFFINE;

/******************************************************************/

typedef struct
{
	double xmin, ymin, zmin;
	double xmax, ymax, zmax;
	int32_t srid;
}
BOX3D;

/******************************************************************
* GBOX structure.
* We include the flags (information about dimensionality),
* so we don't have to constantly pass them
* into functions that use the GBOX.
*/
typedef struct
{
	uint8_t flags;
	double xmin;
	double xmax;
	double ymin;
	double ymax;
	double zmin;
	double zmax;
	double mmin;
	double mmax;
} GBOX;


/******************************************************************
* SPHEROID
*
*  Standard definition of an ellipsoid (what wkt calls a spheroid)
*    f = (a-b)/a
*    e_sq = (a*a - b*b)/(a*a)
*    b = a - fa
*/
typedef struct
{
	double	a;	/* semimajor axis */
	double	b; 	/* semiminor axis b = (a - fa) */
	double	f;	/* flattening f = (a-b)/a */
	double	e;	/* eccentricity (first) */
	double	e_sq;	/* eccentricity squared (first) e_sq = (a*a-b*b)/(a*a) */
	double  radius;  /* spherical average radius = (2*a+b)/3 */
	char	name[20];  /* name of ellipse */
}
SPHEROID;

/******************************************************************
* POINT2D, POINT3D, POINT3DM, POINT4D
*/
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

/******************************************************************
*  POINTARRAY
*  Point array abstracts a lot of the complexity of points and point lists.
*  It handles 2d/3d translation
*    (2d points converted to 3d will have z=0 or NaN)
*  DO NOT MIX 2D and 3D POINTS! EVERYTHING* is either one or the other
*/
typedef struct
{
	/* Array of POINT 2D, 3D or 4D, possibly misaligned. */
	uint8_t *serialized_pointlist;

	/* Use FLAGS_* macros to handle */
	uint8_t  flags;

	uint32_t npoints;   /* how many points we are currently storing */
	uint32_t maxpoints; /* how many points we have space for in serialized_pointlist */
}
POINTARRAY;

/******************************************************************
* GSERIALIZED
*/
typedef struct
{
	uint32_t size; /* For PgSQL use only, use VAR* macros to manipulate. */
	uint8_t srid[3]; /* 24 bits of SRID */
	uint8_t flags; /* HasZ, HasM, HasBBox, IsGeodetic, IsReadOnly */
	uint8_t data[1]; /* See gserialized.txt */
} GSERIALIZED;


/******************************************************************
* LWGEOM (any geometry type)
*
* Abstract type, note that 'type', 'bbox' and 'srid' are available in
* all geometry variants.
*/
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	void *data;
}
LWGEOM;

/* POINTYPE */
typedef struct
{
	uint8_t type; /* POINTTYPE */
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	POINTARRAY *point;  /* hide 2d/3d (this will be an array of 1 point) */
}
LWPOINT; /* "light-weight point" */

/* LINETYPE */
typedef struct
{
	uint8_t type; /* LINETYPE */
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	POINTARRAY *points; /* array of POINT3D */
}
LWLINE; /* "light-weight line" */

/* TRIANGLE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	POINTARRAY *points;
}
LWTRIANGLE;

/* CIRCSTRINGTYPE */
typedef struct
{
	uint8_t type; /* CIRCSTRINGTYPE */
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	POINTARRAY *points; /* array of POINT(3D/3DM) */
}
LWCIRCSTRING; /* "light-weight circularstring" */

/* POLYGONTYPE */
typedef struct
{
	uint8_t type; /* POLYGONTYPE */
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t nrings;   /* how many rings we are currently storing */
	uint32_t maxrings; /* how many rings we have space for in **rings */
	POINTARRAY **rings; /* list of rings (list of points) */
}
LWPOLY; /* "light-weight polygon" */

/* MULTIPOINTTYPE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWPOINT **geoms;
}
LWMPOINT;

/* MULTILINETYPE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWLINE **geoms;
}
LWMLINE;

/* MULTIPOLYGONTYPE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWPOLY **geoms;
}
LWMPOLY;

/* COLLECTIONTYPE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWGEOM **geoms;
}
LWCOLLECTION;

/* COMPOUNDTYPE */
typedef struct
{
	uint8_t type; /* COMPOUNDTYPE */
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWGEOM **geoms;
}
LWCOMPOUND; /* "light-weight compound line" */

/* CURVEPOLYTYPE */
typedef struct
{
	uint8_t type; /* CURVEPOLYTYPE */
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t nrings;    /* how many rings we are currently storing */
	uint32_t maxrings;  /* how many rings we have space for in **rings */
	LWGEOM **rings; /* list of rings (list of points) */
}
LWCURVEPOLY; /* "light-weight polygon" */

/* MULTICURVE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWGEOM **geoms;
}
LWMCURVE;

/* MULTISURFACETYPE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWGEOM **geoms;
}
LWMSURFACE;

/* POLYHEDRALSURFACETYPE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWPOLY **geoms;
}
LWPSURFACE;

/* TINTYPE */
typedef struct
{
	uint8_t type;
	uint8_t flags;
	GBOX *bbox;
	int32_t srid;
	uint32_t ngeoms;   /* how many geometries we are currently storing */
	uint32_t maxgeoms; /* how many geometries we have space for in **geoms */
	LWTRIANGLE **geoms;
}
LWTIN;


extern LWPOINT *lwpoint_make(int32_t srid, int hasz, int hasm, const POINT4D *p);

extern LWGEOM *lwgeom_from_gserialized(const GSERIALIZED *g);
extern GSERIALIZED *gserialized_from_lwgeom(LWGEOM *geom, size_t *size);

extern static inline LWPOINT *lwgeom_as_lwpoint(const LWGEOM *lwgeom);

extern int32_t lwgeom_get_srid(const LWGEOM *geom);

extern double lwpoint_get_x(const LWPOINT *point);
extern double lwpoint_get_y(const LWPOINT *point);
extern double lwpoint_get_z(const LWPOINT *point);
extern double lwpoint_get_m(const LWPOINT *point);

extern int lwgeom_has_z(const LWGEOM *geom);
extern int lwgeom_has_m(const LWGEOM *geom);
"""

ADDITIONAL_DEFINITIONS = (
    """/*****************************************************************************
 * Type definitions
 *****************************************************************************/"""
    ,
    """
""" + LIBLWGEOM_DEFINITIONS + """
/*****************************************************************************
 * Type definitions
 *****************************************************************************/"""
)
