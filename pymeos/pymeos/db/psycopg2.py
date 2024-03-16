import psycopg2
from psycopg2 import extensions, connect

from .db_objects import db_objects


class MobilityDB:
    """
    Helper class to register MobilityDB classes to a psycopg2 connection and their automatic conversion to
    PyMEOS classes.
    """

    @classmethod
    def connect(cls, *args, **kwargs) -> psycopg2.extensions.connection:
        """
        Establishes a connection to a MobilityDB server.

        Refer to :func:`psycopg2.connect` for the list of valid arguments.

        If the connection already exists, see the :func:`~pymeos.db.psycopg2.MobilityDB.register` in this class.

        Args:
            *args: positional arguments that will be passed to :func:`psycopg.connect`
            **kwargs: keyword arguments that will be passed to :func:`psycopg.connect`

        Returns:
            A new :class:`psycopg2.extensions.connection` object with the MobilityDB classes registered.

        """
        conn = connect(*args, **kwargs)
        cls.register(conn)
        return conn

    @classmethod
    def register(cls, connection: psycopg2.extensions.connection) -> None:
        """
        Registers MobilityDB classes to the passed connection.

        Args:
            connection: An :class:`psycopg2.extensions.connection` to register the classes to.
        """
        if isinstance(connection, extensions.cursor):
            # Retro compatibility
            cursor = connection
        else:
            cursor = connection.cursor()

        # Add MobilityDB types to PostgreSQL adapter and specify the reader function for each type.
        for cl in db_objects:
            cursor.execute(f"SELECT NULL::{cl._mobilitydb_name}")
            oid = cursor.description[0][1]
            extensions.register_type(
                extensions.new_type((oid,), cl._mobilitydb_name, cl.read_from_cursor)
            )
