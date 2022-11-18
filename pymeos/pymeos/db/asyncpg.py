import asyncpg

from pymeos import TBool, TInt, TFloat, TText, TGeomPoint, TGeogPoint, TBox, STBox, TimestampSet, Period, PeriodSet


class MobilityDB:
    @classmethod
    async def connect(cls, *args, **kwargs):
        conn = await asyncpg.connect(*args, **kwargs)
        await cls.register(conn)
        return conn

    @classmethod
    async def register(cls, conn):
        # Add MobilityDB types to PostgreSQL adapter and specify the reader function for each type.
        classes = [TimestampSet, Period, PeriodSet, TBox, TBool, TInt, TFloat, TText, STBox, TGeomPoint, TGeogPoint]
        for cl in classes:
            await conn.set_type_codec(cl.__name__.lower(), encoder=str, decoder=cl.read_from_cursor)
