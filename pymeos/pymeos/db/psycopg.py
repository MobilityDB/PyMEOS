from typing import Any

from psycopg import connect
from psycopg.adapt import Loader, Buffer, Dumper

from pymeos import TBool, TInt, TFloat, TText, TGeomPoint, TGeogPoint, TBox, STBox, TimestampSet, Period, PeriodSet


def pymeos_loader_factory(cl):
    class _PymeosLoader(Loader):
        def load(self, data: Buffer) -> Any:
            return cl.read_from_cursor(data.decode())

    return _PymeosLoader


class _PymeosDumper(Dumper):
    def dump(self, obj: Any) -> Buffer:
        return str(obj).encode()


class MobilityDB:
    @classmethod
    def connect(cls, *args, **kwargs):
        connection = connect(*args, **kwargs)
        cls.register(connection)
        return connection

    @classmethod
    def register(cls, connection):
        # Add MobilityDB types to PostgreSQL adapter and specify the reader function for each type.
        cursor = connection.cursor()
        classes = [TimestampSet, Period, PeriodSet, TBox, TBool, TInt, TFloat, TText, STBox, TGeomPoint, TGeogPoint]
        for cl in classes:
            cursor.execute(f'SELECT NULL::{cl.__name__}')
            oid = cursor.description[0][1]
            connection.adapters.register_loader(oid, pymeos_loader_factory(cl))
            connection.adapters.register_dumper(cl, _PymeosDumper)
