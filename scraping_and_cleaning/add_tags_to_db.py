# file: add_tags_to_db.py
# Author: Alison Silldorff
# Date: 1/8/25
# Purpose: 


# 1. Connect to the database
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import csv

password = open("C:\\Users\\12676\\mysqlinfo", 'r').read()

file1 = open("urls_and_ids.json")
file2 = open("musicals_info.json")

ids = json.load(file1)
musicals = json.load(file2)
musicals_values = musicals.values()

tag_dict = {'Musical': '0', 'Original': '1', 'Broadway': '2', 'Comedy': '3', 
            'Revival': '4', 'Drama': '5', 'Fantasy': '6', 'Romance': '7', 
            'Ballet': '8', 'One Act': '9', 'Operetta': '10', 'Revue': '11', 
            'Romantic Comedy': '12', 'Dance': '13', 'Vaudeville': '14', 
            'Play with music': '15', 'Play': '16', 'Puppets': '17', 'Opera': '18', 
            'Satire': '19', 'History': '20', 'Sketches': '21', 'Minstrel': '22', 
            'Variety': '23', 'All Black Cast': '24', 'Spectacle': '25', 'Circus': '26', 
            'Foreign Lang.': '27', 'Tragedy': '28', 'Thriller': '29', 'Farce': '30', 
            'Extravaganza': '31', 'Pantomime': '32', 'All Female Cast': '33', 
            'Sign Language': '34', 'Concert': '35', 'Tribute': '36', 'Mystery': '37', 
            'Burlesque': '38', 'Melodrama': '39', 'Mime': '40', 'Solo': '41'}

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

        for row in musicals_values:
            full_url = row["url"]
            #short_url = full_url.split("ibdb.com")[1]
            if full_url in ids:
                work_id = ids[full_url]
                tags = row["tags"]
                title = row["title"]
                for tag in tags:
                    tag_id = tag_dict[tag].zfill(2)
                    work_tag_id = work_id + tag_id
                    property_id = work_id[:4]
                    type_id = work_id[-2:]
                    # Values: work_tag_id, tag_name, work_id, tag_id, property_id, type_id, title
                    query = "INSERT INTO ibdb_tag VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, (work_tag_id, tag, work_id, tag_id, property_id, type_id, title))
                    connection.commit()
            # work_id = row[0]
            # url = row[4]
            # closing = musicals[url]["closing"]
            # print(url)
            # print(closing)
            # if closing=='Closing date unknown':
            #     closing_date = ''
            # else:
            #     closing_date = datetime.strptime(closing, "%b %Y").date()

            # query2 = "UPDATE stage_work SET closing_date=%s WHERE work_id=%s"
            # cursor.execute(query2, (closing_date, work_id))
            # connection.commit()
        print(cursor.rowcount)
        cursor.close()   
except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
