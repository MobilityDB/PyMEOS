from psycopg2 import extensions, connect

from pymeos import TBool, TInt, TFloat, TText, TGeomPoint, TGeogPoint, TBox, STBox, TimestampSet, Period, PeriodSet


class MobilityDB:
    @classmethod
    def connect(cls, *args, **kwargs):
        conn = connect(*args, **kwargs)
        cls.register(conn)
        return conn

    @classmethod
    def register(cls, connection):
        if isinstance(connection, extensions.cursor):
            # Retro compatibility
            cursor = connection
        else:
            cursor = connection.cursor()

        # Add MobilityDB types to PostgreSQL adapter and specify the reader function for each type.
        classes = [TimestampSet, Period, PeriodSet, TBox, TBool, TInt, TFloat, TText, STBox, TGeomPoint, TGeogPoint]
        for cl in classes:
            cursor.execute(f'SELECT NULL::{cl.__name__}')
            oid = cursor.description[0][1]
            extensions.register_type(extensions.new_type((oid,), cl.__name__, cl.read_from_cursor))
