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
    # TGeogPointInst
    ######################

    select_query = "select * from tbl_tgeogpointinst order by k limit 10"

    cursor.execute(select_query)
    print("\n****************************************************************")
    print("Selecting rows from tbl_tgeogpointinst table\n")
    rows = cursor.fetchall()

    for row in rows:
        print("key =", row[0])
        print("tgeogpointinst =", row[1])
        if not row[1]:
            print("")
        else:
            print("startTimestamp =", row[1].startTimestamp, "\n")

    drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointinst_temp;'''
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully in PostgreSQL ")

    create_table_query = '''CREATE TABLE tbl_tgeogpointinst_temp
        (
          k integer PRIMARY KEY,
          temp tgeogpoint
        ); '''

    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    postgres_insert_query = ''' INSERT INTO tbl_tgeogpointinst_temp (k, temp) VALUES (%s, %s) '''
    result = cursor.executemany(postgres_insert_query, rows)
    connection.commit()
    count = cursor.rowcount
    print(count, "record(s) inserted successfully into tbl_tgeogpointinst_temp table")

    ######################
    # TGeogPointI
    ######################

    select_query = "select * from tbl_tgeogpointi order by k limit 10"

    cursor.execute(select_query)
    print("\n****************************************************************")
    print("Selecting rows from tbl_tgeogpointi table\n")
    rows = cursor.fetchall()

    for row in rows:
        print("key =", row[0])
        print("tgeogpointi =", row[1])
        if not row[1]:
            print("")
        else:
            print("startTimestamp =", row[1].startTimestamp, "\n")

    drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointinstset_temp;'''
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully in PostgreSQL ")

    create_table_query = '''CREATE TABLE tbl_tgeogpointinstset_temp
        (
          k integer PRIMARY KEY,
          temp tgeogpoint
        ); '''

    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    postgres_insert_query = ''' INSERT INTO tbl_tgeogpointinstset_temp (k, temp) VALUES (%s, %s) '''
    result = cursor.executemany(postgres_insert_query, rows)
    connection.commit()
    count = cursor.rowcount
    print(count, "record(s) inserted successfully into tbl_tgeogpointinstset_temp table")

    ######################
    # TGeogPointSeq
    ######################

    select_query = "select * from tbl_tgeogpointseq order by k limit 10"

    cursor.execute(select_query)
    print("\n****************************************************************")
    print("Selecting rows from tbl_tgeogpointseq table\n")
    rows = cursor.fetchall()

    for row in rows:
        print("key =", row[0])
        print("tgeogpointseq =", row[1])
        if not row[1]:
            print("")
        else:
            print("startTimestamp =", row[1].startTimestamp, "\n")

    drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointseq_temp;'''
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully in PostgreSQL ")

    create_table_query = '''CREATE TABLE tbl_tgeogpointseq_temp
        (
          k integer PRIMARY KEY,
          temp tgeogpoint
        ); '''

    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    postgres_insert_query = ''' INSERT INTO tbl_tgeogpointseq_temp (k, temp) VALUES (%s, %s) '''
    result = cursor.executemany(postgres_insert_query, rows)
    connection.commit()
    count = cursor.rowcount
    print(count, "record(s) inserted successfully into tbl_tgeogpointseq_temp table")

    ######################
    # TGeogPointS
    ######################

    select_query = "select * from tbl_tgeogpoints order by k limit 10"

    cursor.execute(select_query)
    print("\n****************************************************************")
    print("Selecting rows from tbl_tgeogpoints table\n")
    rows = cursor.fetchall()

    for row in rows:
        print("key =", row[0])
        print("tgeogpoints =", row[1])
        if not row[1]:
            print("")
        else:
            print("startTimestamp =", row[1].startTimestamp, "\n")

    drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointseqset_temp;'''
    cursor.execute(drop_table_query)
    connection.commit()
    print("Table deleted successfully in PostgreSQL ")

    create_table_query = '''CREATE TABLE tbl_tgeogpointseqset_temp
        (
          k integer PRIMARY KEY,
          temp tgeogpoint
        ); '''

    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    postgres_insert_query = ''' INSERT INTO tbl_tgeogpointseqset_temp (k, temp) VALUES (%s, %s) '''
    result = cursor.executemany(postgres_insert_query, rows)
    connection.commit()
    count = cursor.rowcount
    print(count, "record(s) inserted successfully into tbl_tgeogpointseqset_temp table")

    print("\n****************************************************************")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:

    if connection:
        connection.close()
