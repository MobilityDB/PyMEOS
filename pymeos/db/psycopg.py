from typing import Any

import psycopg
from psycopg import connect
from psycopg.adapt import Loader, Buffer, Dumper

from .db_objects import db_objects


def _pymeos_loader_factory(cl):
    class _PymeosLoader(Loader):
        def load(self, data: Buffer) -> Any:
            return cl.read_from_cursor(data.decode())

    return _PymeosLoader


class _PymeosDumper(Dumper):
    def dump(self, obj: Any) -> Buffer:
        return str(obj).encode()


class MobilityDB:
    """
    Helper class to register MobilityDB classes to a psycopg (3) connection and their automatic conversion to
    PyMEOS classes.
    """

    @classmethod
    def connect(cls, *args, **kwargs):
        """
        Establishes a connection to a MobilityDB server.

        Refer to :func:`psycopg.connect` for the list of valid arguments.

        If the connection already exists, see the :func:`~pymeos.db.psycopg.MobilityDB.register` in this class.

        Args:
            *args: positional arguments that will be passed to :func:`psycopg.connect`
            **kwargs: keyword arguments that will be passed to :func:`psycopg.connect`

        Returns:
            A new :class:`psycopg.Connection` object with the MobilityDB classes registered.

        """
        connection = connect(*args, **kwargs)
        cls.register(connection)
        return connection

    @classmethod
    def register(cls, connection: psycopg.Connection):
        """
        Registers MobilityDB classes to the passed connection.

        Args:
            connection: An :class:`psycopg.Connection` to register the classes to.
        """
        cursor = connection.cursor()
        for cl in db_objects:
            cursor.execute(f"SELECT NULL::{cl._mobilitydb_name}")
            oid = cursor.description[0][1]
            connection.adapters.register_loader(oid, _pymeos_loader_factory(cl))
            connection.adapters.register_dumper(cl, _PymeosDumper)
