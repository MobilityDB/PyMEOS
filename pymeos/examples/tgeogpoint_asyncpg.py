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

import asyncio
import asyncpg
from mobilitydb.asyncpg import register
from mobilitydb.examples.db_connect import asyncpg_connect


async def run():

    # Set the connection parameters to PostgreSQL
    connection = await asyncpg_connect()

    try:
        # Register MobilityDB data types
        await register(connection)

        ######################
        # TGeogPointInst
        ######################

        select_query = "select * from tbl_tgeogpointinst order by k limit 10"

        print("\n****************************************************************")
        print("Selecting rows from tbl_tgeogpointinst table\n")
        rows = await connection.fetch(select_query)

        for row in rows:
            print("key =", row[0])
            print("tgeogpointinst =", row[1])
            if not row[1]:
                print("")
            else:
                print("startTimestamp =", row[1].start_timestamp, "\n")

        drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointinst_temp;'''
        await connection.execute(drop_table_query)
        print("Table deleted successfully in PostgreSQL ")
    
        create_table_query = '''CREATE TABLE tbl_tgeogpointinst_temp
            (
              k integer PRIMARY KEY,
              temp tgeogpoint
            ); '''
    
        await connection.execute(create_table_query)
        print("Table created successfully in PostgreSQL ")
    
        postgres_insert_query = ''' INSERT INTO tbl_tgeogpointinst_temp (k, temp) VALUES ($1, $2) '''
        await connection.executemany(postgres_insert_query, rows)
        # count = cursor.rowcount
        print(len(rows), "record(s) inserted successfully into tbl_tgeogpointinst table")

        ######################
        # TGeogPointI
        ######################

        select_query = "select * from tbl_tgeogpointi order by k limit 10"

        print("\n****************************************************************")
        print("Selecting rows from tbl_tgeogpointi table\n")
        rows = await connection.fetch(select_query)

        for row in rows:
            print("key =", row[0])
            print("tgeogpointi =", row[1])
            if not row[1]:
                print("")
            else:
                print("startTimestamp =", row[1].start_timestamp, "\n")

        drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointinstset_temp;'''
        await connection.execute(drop_table_query)
        print("Table deleted successfully in PostgreSQL ")
    
        create_table_query = '''CREATE TABLE tbl_tgeogpointinstset_temp
            (
              k integer PRIMARY KEY,
              temp tgeogpoint
            ); '''
    
        await connection.execute(create_table_query)
        print("Table created successfully in PostgreSQL ")
    
        postgres_insert_query = ''' INSERT INTO tbl_tgeogpointinstset_temp (k, temp) VALUES ($1, $2) '''
        await connection.executemany(postgres_insert_query, rows)
        #count = cursor.rowcount
        print(len(rows), "record(s) inserted successfully into tbl_tgeogpointinstset_temp table")

        ######################
        # TGeogPointSeq
        ######################
    
        select_query = "select * from tbl_tgeogpointseq order by k limit 10"
    
        print("\n****************************************************************")
        print("Selecting rows from tbl_tgeogpointseq table\n")
        rows = await connection.fetch(select_query)
    
        for row in rows:
            print("key =", row[0])
            print("tgeogpointseq =", row[1])
            if not row[1]:
                print("")
            else:
                print("startTimestamp =", row[1].start_timestamp, "\n")
    
        drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointseq_temp;'''
        await connection.execute(drop_table_query)
        print("Table deleted successfully in PostgreSQL ")
    
        create_table_query = '''CREATE TABLE tbl_tgeogpointseq_temp
            (
              k integer PRIMARY KEY,
              temp tgeogpoint
            ); '''
    
        await connection.execute(create_table_query)
        print("Table created successfully in PostgreSQL ")
    
        postgres_insert_query = ''' INSERT INTO tbl_tgeogpointseq_temp (k, temp) VALUES ($1, $2) '''
        await connection.executemany(postgres_insert_query, rows)
        #count = cursor.rowcount
        print(len(rows), "record(s) inserted successfully into tbl_tgeogpointseq_temp table")

        ######################
        # TGeogPointS
        ######################
    
        select_query = "select * from tbl_tgeogpoints order by k limit 10"
    
        print("\n****************************************************************")
        print("Selecting rows from tbl_tgeogpoints table\n")
        rows = await connection.fetch(select_query)
    
        for row in rows:
            print("key =", row[0])
            print("tgeogpoints =", row[1])
            if not row[1]:
                print("")
            else:
                print("startTimestamp =", row[1].start_timestamp, "\n")
    
        drop_table_query = '''DROP TABLE IF EXISTS tbl_tgeogpointseqset_temp;'''
        await connection.execute(drop_table_query)
        print("Table deleted successfully in PostgreSQL ")
    
        create_table_query = '''CREATE TABLE tbl_tgeogpointseqset_temp
            (
              k integer PRIMARY KEY,
              temp tgeogpoint
            ); '''
    
        await connection.execute(create_table_query)
        print("Table created successfully in PostgreSQL ")
    
        postgres_insert_query = ''' INSERT INTO tbl_tgeogpointseqset_temp (k, temp) VALUES ($1, $2) '''
        await connection.executemany(postgres_insert_query, rows)
        # count = cursor.rowcount
        print(len(rows), "record(s) inserted successfully into tbl_tgeogpointseqset_temp table")
    
        print("\n****************************************************************")

    finally:
        await connection.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())


