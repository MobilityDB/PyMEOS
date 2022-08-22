###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################

import psycopg2
from mobilitydb.psycopg import register
from mobilitydb.examples.db_connect import psycopg_connect

connection = None

try:
    # Set the connection parameters to PostgreSQL
    connection = psycopg_connect()
    connection.autocommit = True

    # Register MobilityDB data types
    register(connection)

    cursor = connection.cursor()

    ######################
    # TimestampSet
    ######################

    select_query = "SELECT * FROM tbl_timestampset ORDER BY k LIMIT 10"

    cursor.execute(select_query)
    print("\n****************************************************************")
    print("Selecting rows from tbl_timestampset table\n")
    rows = cursor.fetchall()

    for row in rows:
        print("key =", row[0])
        print("timestampset =", row[1])
        if not row[1]:
            print("")
        else:
            print("duration =", row[1].duration, "\n")

    drop_table_query = "DROP TABLE IF EXISTS tbl_timestampset_temp;"
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully in PostgreSQL")

    create_table_query = '''CREATE TABLE tbl_timestampset_temp
    (
      k integer PRIMARY KEY,
      ts timestampset
    ); '''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL")

    insert_query = "INSERT INTO tbl_timestampset_temp (k, ts) VALUES (%s, %s)"
    result = cursor.executemany(insert_query, rows)
    connection.commit()
    count = cursor.rowcount
    print(count, "record(s) inserted successfully into tbl_timestampset_temp table")

    ######################
    # Period
    ######################

    select_query = "SELECT * FROM tbl_period ORDER BY k LIMIT 10"

    cursor.execute(select_query)
    print("\n****************************************************************")
    print("Selecting rows from tbl_period table\n")
    rows = cursor.fetchall()

    for row in rows:
        print("key =", row[0])
        print("period =", row[1])
        if not row[1]:
            print("")
        else:
            print("duration =", row[1].duration, "\n")

    drop_table_query = "DROP TABLE IF EXISTS tbl_period_temp;"
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully in PostgreSQL")

    create_table_query = '''CREATE TABLE tbl_period_temp
    (
      k integer PRIMARY KEY,
      p period
    ); '''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL")

    insert_query = "INSERT INTO tbl_period_temp (k, p) VALUES (%s, %s)"
    result = cursor.executemany(insert_query, rows)
    connection.commit()
    count = cursor.rowcount
    print(count, "record(s) inserted successfully into tbl_period_temp table")

    ######################
    # PeriodSet
    ######################

    select_query = "SELECT * FROM tbl_periodset ORDER BY k LIMIT 10"

    cursor.execute(select_query)
    print("\n****************************************************************")
    print("Selecting rows from tbl_periodset table\n")
    rows = cursor.fetchall()

    for row in rows:
        print("key =", row[0])
        print("periodset =", row[1])
        if not row[1]:
            print("")
        else:
            print("duration =", row[1].duration, "\n")

    drop_table_query = "DROP TABLE IF EXISTS tbl_periodset_temp;"
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully in PostgreSQL")

    create_table_query = '''CREATE TABLE tbl_periodset_temp
    (
      k integer PRIMARY KEY,
      ps periodset
    ); '''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL")

    insert_query = "INSERT INTO tbl_periodset_temp (k, ps) VALUES (%s, %s)"
    result = cursor.executemany(insert_query, rows)
    connection.commit()
    count = cursor.rowcount
    print(count, "record(s) inserted successfully into tbl_periodset_temp table")

    print("\n****************************************************************")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:

    if connection:
        connection.close()
