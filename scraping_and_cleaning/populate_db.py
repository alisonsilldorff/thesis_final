# file: populate_db.py
# Author: Alison Silldorff
# Date: 1/8/25
# Purpose: Populate the shows portion of the db!


# 1. Connect to the database
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

password = open("C:\\Users\\12676\\mysqlinfo", 'r').read()

file1 = open("urls_and_ids.json")
file2 = open("musicals_info.json")

ids = json.load(file1)
musicals = json.load(file2)


try:
    connection = mysql.connector.connect(host='localhost', 
                                         database='shows_db',
                                         user='root',
                                         password=password, use_pure=True)
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

        # add info to work and stage_work
        for full_url in ids:
            url = full_url.split("ibdb.com")[1]
            work_id = ids[full_url]
            property_id = work_id[:4]
            type_id = work_id[-2:]
            title = musicals[url]["title"]
            # ibdb_url = url
            opening_date = musicals[url]["opening"]
            year = 0
            try:
                if opening_date != "":
                    opening_date = datetime.strptime(opening_date, "%b %d, %Y").date()
                    year = opening_date.year
            except:
                opening_date = 'RETRY'
                year = -1

            preview_date = musicals[url]["preview"]
            try:
                if preview_date != '':
                    preview_date = datetime.strptime(preview_date, "%b %d, %Y").date()
            except:
                preview_date = 'RETRY'

            closing_date = musicals[url]["closing"]
            try:
                if closing_date != '':
                    closing_date = datetime.strptime(closing_date, "%b %d, %Y").date()
            except:
                closing_date = 'RETRY'

            num_previews = musicals[url]["num_previews"]
            num_performances = musicals[url]["num_perfs"]
            print(url)
            query1 = "INSERT INTO work (work_id, property_id, type_id, title, year) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query1, (work_id, property_id, type_id, title, year))
            query2 = "INSERT INTO stage_work (work_id, property_id, type_id, title, ibdb_url, opening_date, preview_start_date, closing_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query2, (work_id, property_id, type_id, title, url, opening_date, preview_date, closing_date))
            connection.commit()
        print(cursor.rowcount)
        cursor.close()   
except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
