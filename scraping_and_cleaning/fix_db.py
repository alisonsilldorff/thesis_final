# file: populate_db.py
# Author: Alison Silldorff
# Date: 1/8/25
# Purpose: Fix the closing dates of a bunch of rows.


# 1. Connect to the database
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import csv

password = open("C:\\Users\\12676\\mysqlinfo", 'r').read()

file1 = open("urls_and_ids.json")
file2 = open("musicals_info.json")
file3 = "rows that need to be fixed 2.json"

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

        with open(file3) as file_obj:
            reader = csv.reader(file_obj)
            for row in reader:
                work_id = row[0]
                url = row[4]
                closing = musicals[url]["closing"]
                print(url)
                print(closing)
                if closing=='Closing date unknown':
                    closing_date = ''
                else:
                    closing_date = datetime.strptime(closing, "%b %Y").date()

                query2 = "UPDATE stage_work SET closing_date=%s WHERE work_id=%s"
                cursor.execute(query2, (closing_date, work_id))
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
