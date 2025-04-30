# file: misc_sql_work.py
# Author: Alison Silldorff
# Date: 1/9/25
# Purpose: Space to do anywork that you need to do in SQL from Python! Write a method.


# 1. Connect to the database
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import csv
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime

password = open("C:\\Users\\12676\\mysqlinfo", 'r').read()

file1 = open("urls_and_ids.json")
file2 = open("musicals_info.json")

ids = json.load(file1)
musicals = json.load(file2)
musicals2 = json.loads
musicals_values = musicals.values()


def populate_property_ids(cursor):
    property_ids = set()
    for row in musicals_values:
        full_url = row["url"]
        #short_url = full_url.split("ibdb.com")[1]
        if full_url in ids:
            work_id = ids[full_url]
            property_id = work_id[:4]
            if property_id not in property_ids:
                print(full_url)
                title = row["title"]
                property_ids.add(property_id)
                # Values: property_id, property
                query = "INSERT INTO property_id_info VALUES (%s, %s)"
                cursor.execute(query, (property_id, title))
                connection.commit()


def populate_musical_actors(cursor):
    # for each musical, 
    i = 0
    actor_dict = {}
    for row in musicals_values:
        full_url = row["url"]
        if full_url in ids:
            work_person_ids = {}
            work_id = ids[full_url]
            property_id = work_id[:4]
            type_id = work_id[-2:]
            title = row["title"]
            short_url = full_url.split("ibdb.com")[1]
            opening_cast = row["opening_cast"]
            for actor in opening_cast.values():
                actor_url = actor["url"].split("ibdb.com")[1]
                name = actor["actor"]
                if actor["debut"]:
                    debut = 1
                else:
                    debut = 0

                for role in actor["roles"]:
                    if actor_url in actor_dict:
                        person_id = actor_dict[actor_url]
                    else:
                        person_id = str(i).zfill(10)
                        i += 1
                        actor_dict.update({actor_url:person_id})
                    temp_wpid = work_id + person_id
                    if temp_wpid in work_person_ids:
                        work_person_id = temp_wpid + str(work_person_ids[temp_wpid]+ 1).zfill(2)
                        work_person_ids[temp_wpid]+=1
                    else:
                        work_person_id = temp_wpid + '00'
                        work_person_ids.update({temp_wpid:0})
                    # Values: work_person_id, person_id, name, work_id, title, property_id, type_id, role, url, debut (int)
                    print(work_person_id)
                    query = "INSERT INTO actor VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, (work_person_id, person_id, name, work_id, title, property_id, type_id, role, actor_url, debut))
                    connection.commit()


def remove_accents_and_return_unaccented(input_str):
    new_str = ''
    for c in input_str:
        if unicodedata.is_normalized('NFKD', c) ==0:
            continue
        else:
            new_str += c
    
    return new_str


def get_person_url(name, urls):
    # replace all spaces with -
    # remove . and '
    name = name.replace('.', '')
    name = name.replace('\'', '')
    name = remove_accents_and_return_unaccented(name)
    emdash = name.replace(' ', '-').lower()
    for url in urls:
        if emdash in url:
            return url
    print(name)


def parse_prod_people(cursor):
    # max person_id currently: 00046314
    all_people = []
    people_to_revisit = []
    for musical in musicals_values:
        if musical["url"] in ids:
            prod_people = musical["people"]
            people_urls = musical["people_links"]
            for row in prod_people:
                names = set()
                if 'Based on' in row or 'Based upon' in row or 'Adapted from' in row or 'adapted from' in row:
                    continue
                elif ' by:' in row:
                    split = row.split(' by:')
                    new_row=split[1]
                    role=split[0]
                elif ' by ' in row:
                    split = row.split(' by ')
                    new_row = split[1]
                    role = split[0].strip()
                elif ':' in row:
                    split = row.split(':')
                    new_row = split[1]
                    role = split[0].strip()
                else:
                    people_to_revisit.append([musical["url"], row, "nothing to split"])
                    #print(musical["url"] + ": " + row)
                    continue
                new_row_split = new_row.split(',')
                for name in new_row_split:
                    if 'and ' in name:
                        names_split = name.split(' and ')
                        for a_name in names_split:
                            names.add(a_name.strip())
                    else:
                        names.add(name.strip())
                #print(names)
                for name in names:
                    #print(name)
                    person_url = get_person_url(name, people_urls)
                    if person_url is None:
                        people_to_revisit.append([musical["url"], row, "can't find URL"])
                    else:
                        all_people.append([musical["url"], name, role, person_url])
                    #print(get_person_url(name, people_urls))
                    
                # let's export everything into a CSV with the name, role, show url, and person url.
    with open("current_people.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["show_url", "name", "role", "person_url"])
        for row in all_people:
            writer.writerow(row)

    with open("people_to_revisit.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["show_url", "credit", "error message"])
        for row in people_to_revisit:
            writer.writerow(row)

                # if the new row contains commas, split by those, then split by "and"

# get the person_id for every actor. Also get the work_person_id for every acting credit.
def get_all_actor_ids(cursor):
    query = "SELECT url, person_id FROM actor"
    cursor.execute(query)
    connection.commit()
    res = cursor.fetchall()
    people_dict = {}
    for row in res:
        if row[0] not in people_dict:
            people_dict.update({row[0]:row[1]})
    query2 = "SELECT work_person_id FROM actor"
    cursor.execute(query2)
    connection.commit()
    res2 = cursor.fetchall()
    wpids = set()
    for row in res2:
        wpids.add(row[0])
    return people_dict, wpids

def get_all_work_ids(cursor):
    query = "SELECT ibdb_url, work_id FROM stage_work"
    cursor.execute(query)
    connection.commit()
    res = cursor.fetchall()
    work_dict = {}
    for row in res:
        work_dict.update({row[0]:row[1]})
    return work_dict


# put all the prod people into SQL
def populate_prod_people(cursor):
    # go through every row of the prod_people csv 
    people_dict, actor_wpids = get_all_actor_ids(cursor)
    work_dict = get_all_work_ids(cursor)
    i = 46314
    j = 0
    file = "all-people-csv 5.csv"
    wpids = {}
    with open(file, encoding="utf-8") as file_obj:
        reader = csv.reader(file_obj)
        for row in reader:
            print(j)
            if row[0]=='show_url':
                continue
            show_url = row[0].split("ibdb.com")[1]
            person_url = row[3].split("ibdb.com")[1]
            # generate a person_id if they don't have one!
            if person_url not in people_dict:
                person_id = str(i).zfill(10)
                i += 1
                people_dict.update({person_url:person_id})
            else:
                person_id = people_dict[person_url]
            
            work_id = work_dict[show_url]
            property_id = work_id[:4]
            type_id = work_id[-2:]

            temp_wpid = work_id + person_id
            if temp_wpid not in wpids:
                work_person_id = temp_wpid + '00'
                wpids.update({temp_wpid:0})
            else:
                work_person_id = temp_wpid + str(wpids[temp_wpid]+ 1).zfill(2)
                wpids[temp_wpid]+=1
            
            while work_person_id in actor_wpids:
                new_seq = int(work_person_id[-2:]) + 1
                work_person_id = work_person_id[:-2]+str(new_seq).zfill(2)
                wpids[temp_wpid] = new_seq

            query = "INSERT INTO work_person VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (work_person_id, person_id, work_id, row[1], property_id, type_id, row[2], row[4], person_url))
            connection.commit()
            j += 1
            
            # work_person_id, person_id, work_id, name, property_id, type_id, role, song, url

def revisit_people_info(cursor):
    people_dict = json.load(open("revisited_people_info.json"))
    i = 0
    browser = webdriver.Firefox()
    res_dict = {}
    revisit_dict = {}
    for person in people_dict:
        if i%100==0:
            print(i)
        url = people_dict[person]
        #url = "/broadway-cast-staff/stephen-sondheim-12430"
        try:
            browser.get("https://ibdb.com/"+url)
            BIRTH_CLASS = ".col.s6.txt-paddings"
            try:
                birth_date = browser.find_element(By.CSS_SELECTOR, BIRTH_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
            except:
                birth_date = ''
            try:
                birth_place = browser.find_element(By.CSS_SELECTOR, BIRTH_CLASS).find_element(By.CLASS_NAME, "xt-main-moreinfo").text
            except:
                birth_place = ''
            DEATH_CLASS = ".col.s6.txt-paddings.vertical-divider"
            try:
                death_date = browser.find_element(By.CSS_SELECTOR, DEATH_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
            except:
                death_date = ''
            try:
                death_place = browser.find_element(By.CSS_SELECTOR, DEATH_CLASS).find_element(By.CLASS_NAME, "xt-main-moreinfo").text
            except:
                death_place = ''
            GENDER_CLASS=".col.s12.txt-paddings"
            try:
                gender=browser.find_element(By.CSS_SELECTOR, GENDER_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
            except:
                gender = ''
            i+=1

            res_dict.update({person:[url, birth_date, birth_place, death_date, death_place, gender]})
        except:
            revisit_dict.update({person:url})
    
    json_object = json.dumps(res_dict, indent=4)
    with open("people_info_1.json", "w") as outfile:
        outfile.write(json_object)

    json_object = json.dumps(revisit_dict, indent=4)
    with open("revisited_people_info_1.json", "w") as outfile:
        outfile.write(json_object)

# get information on all people from IBDB
def get_people_info_ibdb(cursor):
    # This block can be used to get the full list from SQL and then scrape.
    query = "SELECT person_id, url FROM work_person"
    cursor.execute(query)
    connection.commit()
    res = cursor.fetchall()
    people_dict = {}
    for row in res:
        if row[0] not in people_dict:
            people_dict.update({row[0]:row[1]})
    
    #people_dict = {'0000046396':"/broadway-cast-staff/stephen-sondheim-12430"}
    # for every person, visit the url in Selenium and scrape things.
    browser = webdriver.Firefox()
    res_dict = {}
    revisit_dict = {}
    i = 0
    for elem in people_dict:
        if i%100==0:
            print(i)
        url = people_dict[elem]
        #url = "/broadway-cast-staff/stephen-sondheim-12430"
        try:
            browser.get("https://ibdb.com/"+url)
            BIRTH_CLASS = ".col.s6.txt-paddings"
            try:
                birth_date = browser.find_element(By.CSS_SELECTOR, BIRTH_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
            except:
                birth_date = ''
            try:
                birth_place = browser.find_element(By.CSS_SELECTOR, BIRTH_CLASS).find_element(By.CLASS_NAME, "xt-main-moreinfo").text
            except:
                birth_place = ''
            DEATH_CLASS = ".col.s6.txt-paddings.vertical-divider"
            try:
                death_date = browser.find_element(By.CSS_SELECTOR, DEATH_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
            except:
                death_date = ''
            try:
                death_place = browser.find_element(By.CSS_SELECTOR, DEATH_CLASS).find_element(By.CLASS_NAME, "xt-main-moreinfo").text
            except:
                death_place = ''
            GENDER_CLASS=".col.s12.txt-paddings"
            try:
                gender=browser.find_element(By.CSS_SELECTOR, GENDER_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
            except:
                gender = ''
            i+=1

            res_dict.update({elem:[url, birth_date, birth_place, death_date, death_place, gender]})
        except:
            print("revisit: ")
            revisit_dict.update({elem:url})
    
    json_object = json.dumps(res_dict, indent=4)
    with open("people_info.json", "w") as outfile:
        outfile.write(json_object)

    json_object = json.dumps(revisit_dict, indent=4)
    with open("revisited_people_info.json", "w") as outfile:
        outfile.write(json_object)
    

# populate the person table
def populate_person_table(cursor):
    # data I have: gender, birth date, death date, birth place, death place, id
    with open("people_info_1.json") as infile:
        people_dict = json.load(infile)
    # elem will be a person_id
    for elem in people_dict:
        curr = people_dict[elem]
        # (person_id, name, birth_date, death_date, birth_place, death_place, gender, url)
        query = "INSERT INTO person VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        # for now, put a placeholder name. Fix it in SQL
        cursor.execute(query, (elem, '', curr[1], curr[3], curr[2], curr[4], curr[5], curr[0]))
        connection.commit()



def assign_more_urls():
    res = []
    people_file = "Shows data  - fixed_ people_to_revisit.csv"
    with open(people_file) as file:
        reader = csv.reader(file)
        # for each row in the thing, see if it has a person_url. if it doesn't, call that other function and see. 
        for row in reader:
            if row[0] == 'show_url':
                continue
            if row[3] == '':
                print("here")
                short_url = row[0].split('ibdb.com')[1]
                people_links = musicals[short_url]["people_links"]
                url = get_person_url(row[1], people_links)
                res.append([row[0], row[1], row[2], url, row[4]])
            else:
                print(row)
                res.append(row)
    
    with open("revisited_people.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["show_url","name","role","person_url",'song'])
        for row in res:
            writer.writerow(row)
            # go to the musical that is listed by the URL


def get_adaptation_creds():
    # max person_id currently: 00046314
    all_people = []
    people_to_revisit = []
    for musical in musicals_values:
        if musical["url"] in ids:
            prod_people = musical["people"]
            people_urls = musical["people_links"]
            for row in prod_people:
                names = set()
                if 'Adapted from' in row or 'adapted from' in row:
                    if ' by:' in row:
                        split = row.split(' by:')
                        new_row=split[1]
                        role=split[0]
                    elif ' by ' in row:
                        split = row.split(' by ')
                        new_row = split[1]
                        role = split[0].strip()
                    elif ':' in row:
                        split = row.split(':')
                        new_row = split[1]
                        role = split[0].strip()
                    else:
                        people_to_revisit.append([musical["url"], row, "nothing to split"])
                else:
                    continue   

                new_row_split = new_row.split(',')
                for name in new_row_split:
                    if 'and ' in name:
                        names_split = name.split(' and ')
                        for a_name in names_split:
                            names.add(a_name.strip())
                    else:
                        names.add(name.strip())
                for name in names:
                    person_url = get_person_url(name, people_urls)
                    if person_url is None:
                        people_to_revisit.append([musical["url"], row, "can't find URL"])
                    else:
                        all_people.append([musical["url"], name, role, person_url])
                    
    with open("adapted_from_people.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["show_url", "name", "role", "person_url"])
        for row in all_people:
            writer.writerow(row)

    with open("adapted_from_people_to_revisit.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["show_url", "credit", "error message"])
        for row in people_to_revisit:
            writer.writerow(row)
                    
def duplicate_originals_helper(cursor):
    res = []
    file = "Shows data  - Sheet16.csv"
    with open(file, encoding="utf-8") as file_obj:
        reader = csv.reader(file_obj)
        for row in reader:
            if row[0] == "Title":
                continue
            property_id = row[1].zfill(4)
            title = row[0]
            query = "SELECT work_id, title, ibdb_url FROM stage_work WHERE title=%s AND property_id=%s AND type_id='11'"
            cursor.execute(query, (title, property_id))
            connection.commit()
            result = cursor.fetchall()
            for elem in result:
                res.append(elem)
    
    with open("possible_show_duplicates.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        for row in res:
            writer.writerow(row)
    print(res)

# update "limited engagement" type_ids in my db.
def fix_type_ids(cursor):
    with open("Shows data  - Sheet17.csv") as file:
        reader = csv.reader(file)
        for row in reader:
            print(row[0])
            query = "UPDATE stage_work SET work_id=%s, type_id=%s WHERE work_id=%s"
            old_work_id = str(row[0]).zfill(8)
            new_type_id = str(row[1])
            new_work_id = old_work_id[:-2] + new_type_id
            cursor.execute(query, (new_work_id, new_type_id, old_work_id))
            connection.commit()

            query2 = "UPDATE work"

# I used fix_type_ids to fix type IDs but I didn't fix them in every table. So I need to fix that.
def fix_type_ids_2(cursor):
    df = pd.read_csv("Shows data  - Sheet17.csv", header=None)
    work_ids = df.iloc[:,0].tolist()
    i=0
    while i < len(work_ids):
        work_ids[i]=str(work_ids[i]).zfill(8)
        i+=1
    work_person_ids = get_work_person_ids(cursor, work_ids)
    work_tag_ids = get_work_tag_ids(cursor, work_ids)
    work_actor_ids = get_work_actor_ids(cursor, work_ids)
    work_ids_dict = {}
    with open("Shows data  - Sheet17.csv") as file:
        reader = csv.reader(file)
        for row in reader:
            print(row[0])
            old_work_id = str(row[0]).zfill(8)
            new_type_id = str(row[1])
            new_work_id = old_work_id[:-2] + new_type_id
            work_ids_dict.update({old_work_id:new_work_id})

            # we have already updated the IDs in stage_work. We need to update them in:
            # work, work_person, ibdb_tag, and actor

            # work:
            query1 = "UPDATE work SET work_id=%s, type_id=%s WHERE work_id=%s"
            cursor.execute(query1, (new_work_id, new_type_id, old_work_id))
            connection.commit()
    
    # next: iterate through work_person_ids and the other ones. find the new work_id using the dictionary, generate the new work_person_id, update the table.
    print("here1")
    for wpid in work_person_ids:
        old_work_id = wpid[:8]
        person_id = wpid[8:]
        new_work_id = work_ids_dict[old_work_id]
        new_type_id = new_work_id[-2:]
        new_wpid = new_work_id + person_id
        query2 = "UPDATE work_person SET work_id=%s, type_id=%s, work_person_id=%s WHERE work_person_id=%s"
        cursor.execute(query2, (new_work_id, new_type_id, new_wpid, wpid))
        connection.commit()
    
    print("here2")
    for wtid in work_tag_ids:
        old_work_id = wtid[:8]
        tag_id = wtid[8:]
        new_work_id = work_ids_dict[old_work_id]
        new_type_id = new_work_id[-2:]
        new_wtid = new_work_id + tag_id
        query3 = "UPDATE ibdb_tag SET work_id=%s, type_id=%s, work_tag_id=%s WHERE work_tag_id=%s"
        cursor.execute(query3, (new_work_id, new_type_id, new_wtid, wtid))
        connection.commit()

    print("here3")
    for wpid in work_actor_ids:
        old_work_id = wpid[:8]
        person_id = wpid[8:]
        new_work_id = work_ids_dict[old_work_id]
        new_type_id = new_work_id[-2:]
        new_wpid = new_work_id + person_id
        query4 = "UPDATE actor SET work_id=%s, type_id=%s, work_person_id=%s WHERE work_person_id=%s"
        cursor.execute(query4, (new_work_id, new_type_id, new_wpid, wpid))
        connection.commit()
    
        


# given a set of work_ids, return all the work_person_ids corresponding to those works
def get_work_person_ids(cursor, work_ids):
    all_res = []
    for row in work_ids:
        query = "SELECT work_person_id FROM work_person WHERE work_id=%s"
        cursor.execute(query, (str(row),))
        connection.commit()
        res = cursor.fetchall()
        for item in res:
            all_res.append(item[0])
    return all_res

# get work_tag_ids from ibdb_tag
def get_work_tag_ids(cursor, work_ids):
    all_res = []
    for row in work_ids:
        query = "SELECT work_tag_id FROM ibdb_tag WHERE work_id=%s"
        cursor.execute(query, (str(row),))
        connection.commit()
        res = cursor.fetchall()
        for item in res:
            all_res.append(item[0])
    return all_res

# get work_tperson_ids from actor table
def get_work_actor_ids(cursor, work_ids):
    all_res = []
    for row in work_ids:
        query = "SELECT work_person_id FROM actor WHERE work_id=%s"
        cursor.execute(query, (str(row),))
        connection.commit()
        res = cursor.fetchall()
        for item in res:
            all_res.append(item[0])
    return all_res
        
# I need to fix the property IDs for Threepenny opera and South Pacific.
def fix_property_ids(cursor):
    #work_ids = ['02830012', '00130012', '23030012', '16700012']
    work_ids = ['11440223','11440323','11440423','11440523','11440623','11440723','11440823']
    works_ids = ['11440923','11441023']
    # old_work_id : new_work_id
    # work_ids_dict = {'02830012':['04570112', '0457'], 
    #                  '00130012':['23860312', '2386'], 
    #                  '23030012':['23860412','2386'], 
    #                  '16700012':['16690112', '1669']}
    # work_ids_dict = {'11440223':['11480323', '1148'], 
    #                  '11440323':['11480423', '1148'], 
    #                  '11440423':['11480523','1148'], 
    #                  '11440523':['11480623', '1148'],
    #                  '11440623':['11480723', '1148'],
    #                  '11440723':['11480823', '1148'],
    #                  '11440823':['11480923', '1148']}
    work_ids_dict = {'11440923':['11481023', '1148'], 
                     '11441023':['11481123', '1148']}
    
    work_person_ids = get_work_person_ids(cursor, work_ids)
    work_tag_ids = get_work_tag_ids(cursor, work_ids)
    work_actor_ids = get_work_actor_ids(cursor, work_ids)

    # work:
    query1 = "UPDATE work SET work_id=%s, property_id=%s WHERE work_id=%s"
    for key in work_ids_dict:
        cursor.execute(query1, (work_ids_dict[key][0], work_ids_dict[key][1], key))
        connection.commit()
    print("here1")

    # stage_work
    query0 = "UPDATE stage_work SET work_id=%s, property_id=%s WHERE work_id=%s"
    for key in work_ids_dict:
        cursor.execute(query0, (work_ids_dict[key][0], work_ids_dict[key][1], key))
        connection.commit()
    print("here1")

    for wpid in work_person_ids:
        old_work_id = wpid[:8]
        person_id = wpid[8:]
        new_work_id = work_ids_dict[old_work_id][0]
        new_property_id = work_ids_dict[old_work_id][1]
        new_wpid = new_work_id + person_id
        query2 = "UPDATE work_person SET work_id=%s, property_id=%s, work_person_id=%s WHERE work_person_id=%s"
        cursor.execute(query2, (new_work_id, new_property_id, new_wpid, wpid))
        connection.commit()
    
    # print("here2")
    # for wtid in work_tag_ids:
    #     old_work_id = wtid[:8]
    #     tag_id = wtid[8:]
    #     new_work_id = work_ids_dict[old_work_id][0]
    #     new_property_id = work_ids_dict[old_work_id][1]
    #     new_wtid = new_work_id + tag_id
    #     query3 = "UPDATE ibdb_tag SET work_id=%s, property_id=%s, work_tag_id=%s WHERE work_tag_id=%s"
    #     cursor.execute(query3, (new_work_id, new_property_id, new_wtid, wtid))
    #     connection.commit()

    print("here3")
    for wpid in work_actor_ids:
        old_work_id = wpid[:8]
        person_id = wpid[8:]
        new_work_id = work_ids_dict[old_work_id][0]
        new_property_id = work_ids_dict[old_work_id][1]
        new_wpid = new_work_id + person_id
        query4 = "UPDATE actor SET work_id=%s, property_id=%s, work_person_id=%s WHERE work_person_id=%s"
        cursor.execute(query4, (new_work_id, new_property_id, new_wpid, wpid))
        connection.commit()

# literally just Peter Pan
# i didn't update the variable names bc im LAZY!
def fix_type_ids_3(cursor):
    work_ids = ['14360012']
    # old_work_id : new_work_id
    work_ids_dict = {'14360012':['14360014', '14']}
    work_person_ids = get_work_person_ids(cursor, work_ids)
    work_tag_ids = get_work_tag_ids(cursor, work_ids)
    work_actor_ids = get_work_actor_ids(cursor, work_ids)

    # work:
    query1 = "UPDATE work SET work_id=%s, type_id=%s WHERE work_id=%s"
    for key in work_ids_dict:
        cursor.execute(query1, (work_ids_dict[key][0], work_ids_dict[key][1], key))
        connection.commit()
    print("here1")

    # stage_work
    query0 = "UPDATE stage_work SET work_id=%s, type_id=%s WHERE work_id=%s"
    for key in work_ids_dict:
        cursor.execute(query0, (work_ids_dict[key][0], work_ids_dict[key][1], key))
        connection.commit()
    print("here1")

    for wpid in work_person_ids:
        old_work_id = wpid[:8]
        person_id = wpid[8:]
        new_work_id = work_ids_dict[old_work_id][0]
        new_property_id = work_ids_dict[old_work_id][1]
        new_wpid = new_work_id + person_id
        query2 = "UPDATE work_person SET work_id=%s, type_id=%s, work_person_id=%s WHERE work_person_id=%s"
        cursor.execute(query2, (new_work_id, new_property_id, new_wpid, wpid))
        connection.commit()
    
    print("here2")
    for wtid in work_tag_ids:
        old_work_id = wtid[:8]
        tag_id = wtid[8:]
        new_work_id = work_ids_dict[old_work_id][0]
        new_property_id = work_ids_dict[old_work_id][1]
        new_wtid = new_work_id + tag_id
        query3 = "UPDATE ibdb_tag SET work_id=%s, type_id=%s, work_tag_id=%s WHERE work_tag_id=%s"
        cursor.execute(query3, (new_work_id, new_property_id, new_wtid, wtid))
        connection.commit()

    print("here3")
    for wpid in work_actor_ids:
        old_work_id = wpid[:8]
        person_id = wpid[8:]
        new_work_id = work_ids_dict[old_work_id][0]
        new_property_id = work_ids_dict[old_work_id][1]
        new_wpid = new_work_id + person_id
        query4 = "UPDATE actor SET work_id=%s, type_id=%s, work_person_id=%s WHERE work_person_id=%s"
        cursor.execute(query4, (new_work_id, new_property_id, new_wpid, wpid))
        connection.commit()

def get_all_person_ids(cursor):
    query = "SELECT person_id FROM person"
    cursor.execute(query)
    connection.commit()
    res = cursor.fetchall()
    work_set = set()
    for row in res:
        work_set.add(row[0])
    return work_set

# upload people collected from TMDB to the DB!
def upload_tmdb_people(cursor):
    work_person_df = pd.read_csv("tmdb_atl_work_person.csv")
    work_person_df = work_person_df.fillna('')

    person_df = pd.read_csv("tmdb_person.csv")
    person_df = person_df.fillna('')

    actor_df = pd.read_csv("tmdb_actor.csv")
    actor_df = actor_df.fillna('')

    curr_person_ids = get_all_person_ids(cursor)

    # query1 = "INSERT INTO work_person (work_person_id, work_id, person_id, name, property_id, type_id, role, tmdb_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    # alt_query1 = ""
    # for key, row in work_person_df.iterrows():
    #     # if it's this particular Gypsy movie, skip it.
    #     if str(row[2])=='6950221':
    #         continue
    #     tuple1 = (str(row[1]).zfill(20), str(row[2]).zfill(8), str(row[3]).zfill(10), row[4], str(row[5]).zfill(4), str(row[6]).zfill(2), row[7],row[8])
    #     cursor.execute(query1, tuple1)
    #     connection.commit()

    query2 = "INSERT INTO person (person_id, name, birth_date, death_date, birth_place, gender, tmdb_url, tmdb_popularity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    for key, row in person_df.iterrows():
        if str(row[1]).zfill(10) not in curr_person_ids:
            # if it's this particular Gypsy movie, skip it.
            if str(row[2])=='6950221':
                continue
            if row[8] == '':
                alt_query2 = "INSERT INTO person (person_id, name, birth_date, death_date, birth_place, gender, tmdb_url) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(alt_query2, (str(row[1]).zfill(10), row[2], row[3], row[4], row[5], row[6], row[7]))
                connection.commit()
            else:
                tmdb_popularity = round(float(row[8]), 4)
                tuple2 = (str(row[1]).zfill(10), row[2], row[3], row[4], row[5], row[6], row[7], tmdb_popularity)
                cursor.execute(query2, tuple2)
                connection.commit()

    query3 = "INSERT INTO actor (work_person_id, work_id, person_id, name, property_id, type_id, role, tmdb_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    for key, row in actor_df.iterrows():
        # if it's this particular Gypsy movie, skip it.
        if str(row[2])=='6950221':
            continue
        tuple3 = (str(row[1]).zfill(20), str(row[2]).zfill(8), str(row[3]).zfill(10), row[4], str(row[5]).zfill(4), str(row[6]).zfill(2), row[7],row[8])
        cursor.execute(query3, tuple3)
        connection.commit()

def check_wpids():
    work_person_df = pd.read_csv("tmdb_atl_work_person.csv")
    work_person_df = work_person_df.fillna('')
    for key, row in work_person_df.iterrows():
        if len(str(row[1])) > 20:
            print(row)


def upload_screen_works(cursor):
    screen_work_df = pd.read_csv('screen_works.csv')
    screen_work_df = screen_work_df.fillna('')
    query = "INSERT INTO screen_work (work_id, property_id, type_id, title, release_date, tmdb_url, us_origin, tmdb_popularity, budget, revenue, tmdb_rating, tmdb_vote_count, assoc_stage_work_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    query1 = "INSERT INTO work (work_id, property_id, type_id, title, year) VALUES (%s, %s, %s, %s, %s)"
    for key, row in screen_work_df.iterrows():
        if row[13] != '':
            assoc_stagework_id = str(int(row[13])).zfill(8)
        else:
            assoc_stagework_id = ''
        cursor.execute(query, (str(row[1]).zfill(8), str(row[2]).zfill(4), str(row[3]).zfill(2), row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], assoc_stagework_id))
        connection.commit()
        year = row[5]
        if year == '':
            alt_query="INSERT INTO work (work_id, property_id, type_id, title) VALUES (%s, %s, %s, %s)"
            cursor.execute(alt_query, (str(row[1]).zfill(8), str(row[2]).zfill(4), str(row[3]).zfill(2), row[4]))
            connection.commit()
        else:
            cursor.execute(query1, (str(row[1]).zfill(8), str(row[2]).zfill(4), str(row[3]).zfill(2), row[4],row[5][:4]))
            connection.commit()

    


# remove opera, operetta, pre-show boat, etc. 
def remove_non_musicals(cursor):
    print()    

def look_at_tags(cursor):
    query = "SELECT ibdb_tag.work_id, ibdb_tag.tag_name, ibdb_tag.tag_id, ibdb_tag.property_id, ibdb_tag.type_id, ibdb_tag.title, stage_work.opening_date, stage_work.ibdb_url FROM ibdb_tag INNER JOIN stage_work ON ibdb_tag.work_id=stage_work.work_id"
    cursor.execute(query)
    connection.commit()
    df = pd.DataFrame(cursor.fetchall())
    df.to_csv('all_tags.csv')

def export_all_people(cursor):
    query = "SELECT * FROM person"
    cursor.execute(query)
    connection.commit()
    df = pd.DataFrame(cursor.fetchall())
    df.to_csv('all_people.csv')


# put birth dates and death dates into a standardized format.
def fix_ibdb_dates(cursor):
    def output_correct_date(date):
        format1 = "%Y-%m-%d"
        format2 = "%b %d, %Y"
        format3 = "circa %Y"
        format4 = "%Y"
        format5 = "%b %Y"
        format6 = "circa %b %Y"
        format7 = "circa %b %d, %Y"
        try:
            return datetime.strptime(date, format1).date()
        except:
            try:
                return datetime.strptime(date, format2).date()
            except:
                try:
                    return datetime.strptime(date, format3).date()
                except:
                    try:
                       return datetime.strptime(date, format4).date() 
                    except:
                        try:
                            return datetime.strptime(date, format5).date()
                        except:
                            try:
                                return datetime.strptime(date, format6).date()
                            except:
                                try:
                                    return datetime.strptime(date, format7).date()
                                except:
                                    return ''

            

    query = "SELECT * FROM person"
    cursor.execute(query)
    connection.commit()
    people_df = pd.DataFrame(cursor.fetchall())
    # {person_id: [new_birth_date, new_death_date]} -- if one of these is empty, leave it as an empty string.
    dates_to_update = {}
    for key, row in people_df.iterrows():
        # row[2] is birth_date
        if row[2]=='' and row[3]=='':
            continue
        new_birth_date = str(output_correct_date(row[2]))
        new_death_date = str(output_correct_date(row[3]))
        dates_to_update.update({row[0]:[new_birth_date, new_death_date]})
    
    query1 = "UPDATE person SET birth_date = %s, death_date=%s WHERE person_id=%s"
    for row in dates_to_update:
        cursor.execute(query1, (dates_to_update[row][0], dates_to_update[row][1], row))
        connection.commit()

# helper function to merge the values of the two rows
def merge_people_rows(row1, row2):
    person_id = row1['person_id']
    old_person_id = row2['person_id']
    #name
    if row1['name']==row2['name']:
        name=row1['name']
    else:
        name = row1['name'] if len(row1['name'])>len(row2['name']) else row2['name']

    # birth_date. if different, take the one that is later (to avoid possible jan 1st defaults.)
    if row1['birth_date']==row2['birth_date']:
        birth_date=row1['birth_date']
    else:
        if row1['birth_date']=='' or row2['birth_date']=='':
            birth_date = row1['birth_date'] if len(row1['birth_date'])>len(row2['birth_date']) else row2['birth_date']
        else:
            birth_date = row1['birth_date'] if pd.to_datetime(row1['birth_date']) > pd.to_datetime(row2['birth_date']) else row2['birth_date']

    if row1['death_date']==row2['death_date']:
        death_date=row1['death_date']
    else:
        # print(name)
        # print(row1['death_date'])
        # print(row2['death_date'])
        if row1['death_date']=='' or row2['death_date']=='':
            death_date = row1['death_date'] if len(row1['death_date'])>len(row2['death_date']) else row2['death_date']
        else:
            death_date = row1['death_date'] if pd.to_datetime(row1['death_date']) > pd.to_datetime(row2['death_date']) else row2['death_date']

    if row1['birth_place']==row2['birth_place']:
        birth_place=row1['birth_place']
    else:
        birth_place = row1['birth_place'] if len(row1['birth_place'])>len(row2['birth_place']) else row2['birth_place']

    if row1['death_place']==row2['death_place']:
        death_place=row1['death_place']
    else:
        death_place = row1['death_place'] if len(row1['death_place'])>len(row2['death_place']) else row2['death_place']

    if row1['gender']==row2['gender']:
        gender=row1['gender']
    else:
        gender=''

    if row1['ibdb_url']==row2['ibdb_url']:
        ibdb_url=row1['ibdb_url']
    else:
        ibdb_url = row1['ibdb_url'] if len(row1['ibdb_url'])>len(row2['ibdb_url']) else row2['ibdb_url']

    if row1['tmdb_url']==row2['tmdb_url']:
        tmdb_url=row1['tmdb_url']
    else:
        tmdb_url = row1['tmdb_url'] if len(row1['tmdb_url'])>len(row2['tmdb_url']) else row2['tmdb_url']

    if row1['tmdb_popularity']==row2['tmdb_popularity']:
        tmdb_popularity=row1['tmdb_popularity']
    else:
        tmdb_popularity = row1['tmdb_popularity'] if len(str(row1['tmdb_popularity']))>len(str(row2['tmdb_popularity'])) else row2['tmdb_popularity']

    new_row = [person_id, name, birth_date, death_date, birth_place, death_place, gender, ibdb_url, tmdb_url, tmdb_popularity]
    return new_row, old_person_id
    
    



def merge_people_1(cursor):
    # {old person_id : new_person_id}
    merged_ids_dict = {}
    not_able_to_merge =pd.DataFrame(columns=['person_id', 'name', 'birth_date', 'death_date', 'birth_place', 
                             'death_place', 'gender', 'ibdb_url', 'tmdb_url', 'tmdb_popularity'])
    merged_people = pd.DataFrame(columns=['person_id', 'name', 'birth_date', 'death_date', 'birth_place', 
                             'death_place', 'gender', 'ibdb_url', 'tmdb_url', 'tmdb_popularity'])
    file = "duplicate_people_CLEAN.csv"
    dup_people_df = pd.read_csv(file)
    dup_people_df = dup_people_df.fillna('')
    dup_people_df = dup_people_df[['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']]
    dup_people_df.columns = ['person_id', 'name', 'birth_date', 'death_date', 'birth_place', 
                             'death_place', 'gender', 'ibdb_url', 'tmdb_url', 'tmdb_popularity']
    #print(dup_people_df)
    freq_dict = {}
    for key, row in dup_people_df.iterrows():
        if row['name'] not in freq_dict:
            freq_dict.update({row['name']:1})
        else:
            freq_dict[row['name']] +=1
    # address where there are only two people with that name
    i=0
    for name in freq_dict:
        # if i >50:
        #     break
        if freq_dict[name]==2:
            dupes = dup_people_df.loc[dup_people_df['name']==name]
            indices = dupes.index.tolist()
            i+=1
            if dupes.loc[indices[0]]['birth_date']==dupes.loc[indices[1]]['birth_date']:
                # if the birth date is an empty string, it's not helpful.
                if dupes.loc[indices[0]]['birth_date']=='':
                    not_able_to_merge.loc[len(not_able_to_merge)]=dupes.loc[indices[0]]
                    not_able_to_merge.loc[len(not_able_to_merge)]=dupes.loc[indices[1]]
                else:
                    new_row, old_person_id = merge_people_rows(dupes.loc[indices[0]], dupes.loc[indices[1]])
                    merged_ids_dict.update({old_person_id:new_row[0]})
                    merged_people.loc[len(merged_people)]=new_row
            else:
                not_able_to_merge.loc[len(not_able_to_merge)]=dupes.loc[indices[0]]
                not_able_to_merge.loc[len(not_able_to_merge)]=dupes.loc[indices[1]]
        else:
            dupes = dup_people_df.loc[dup_people_df['name']==name]
            indices = dupes.index.tolist()
            for index in indices:
                not_able_to_merge.loc[len(not_able_to_merge)]=dupes.loc[index]
    
    not_able_to_merge.to_csv('not_able_to_merge.csv')
    merged_people.to_csv('merged_people_1.csv')

    with open("merged_ids_dict.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["old_person_id", "new_person_id"])  # Writing header
        for key, value in merged_ids_dict.items():
            writer.writerow([key, value])

def get_all_work_person(cursor):
    query = "SELECT * FROM work_person"
    cursor.execute(query)
    connection.commit()
    df = pd.DataFrame(cursor.fetchall())
    return df

def get_all_actor(cursor):
    query = "SELECT * FROM actor"
    cursor.execute(query)
    connection.commit()
    df = pd.DataFrame(cursor.fetchall())
    return df

def get_all_person(cursor):
    query = "SELECT * FROM person"
    cursor.execute(query)
    connection.commit()
    df = pd.DataFrame(cursor.fetchall())
    return df


def execute_people_merge(cursor):
    work_person_df = get_all_work_person(cursor)
    actor_df = get_all_actor(cursor)

    file = "merged_people_1.csv"
    merged_people = pd.read_csv(file)
    merged_people = merged_people.fillna('')
    merged_ids_dict = {}
    with open("merged_ids_dict.csv", 'r') as file:
        reader = list(csv.reader(file))
        for row in reader:
            merged_ids_dict[str(row[0]).zfill(10)]=str(row[1]).zfill(10)
    print(merged_people)
    # remove old row from person
    query1 = "DELETE FROM person WHERE person_id=%s"
    # for key in merged_ids_dict:
    #     if key=='old_person_id':
    #         continue
    #     cursor.execute(query1, (key,))
    #     connection.commit()

    # UPDATE new person row
    query2 = "UPDATE person SET name=%s, birth_date=%s, death_date=%s, birth_place=%s, death_place=%s, gender=%s, ibdb_url=%s, tmdb_url=%s, tmdb_popularity=%s WHERE person_id=%s"
    # for key, row in merged_people.iterrows():
    #     if row['tmdb_popularity']!='':
    #         tmdb_popularity = round(float(row['tmdb_popularity']), 4)
    #         tuple2 = (row['name'], row['birth_date'], row['death_date'], row['birth_place'], row['death_place'],
    #               row['gender'], row['ibdb_url'], row['tmdb_url'], tmdb_popularity, str(row['person_id']).zfill(10))
    #         cursor.execute(query2, tuple2)
    #         connection.commit()
    #     else:
    #         alt_query2 = "UPDATE person SET name=%s, birth_date=%s, death_date=%s, birth_place=%s, death_place=%s, gender=%s, ibdb_url=%s, tmdb_url=%s WHERE person_id=%s"
    #         alt_tuple2 =(row['name'], row['birth_date'], row['death_date'], row['birth_place'], row['death_place'],
    #               row['gender'], row['ibdb_url'], row['tmdb_url'], str(row['person_id']).zfill(10))
    #         cursor.execute(alt_query2, alt_tuple2)
    #         connection.commit()

        
    # update IDs in work_person
    query3 = "UPDATE work_person SET work_person_id=%s, person_id=%s WHERE work_person_id=%s"
    for key, row in work_person_df.iterrows():
        curr_person_id = row[1]
        if curr_person_id in merged_ids_dict:
            work_id = row[2]
            curr_work_person = row[0]
            curr_sequence_bits = curr_work_person[-2:]
            new_wpid = work_id + merged_ids_dict[curr_person_id] + curr_sequence_bits
            cursor.execute(query3, (new_wpid,merged_ids_dict[curr_person_id],curr_work_person))
            connection.commit()
    
    # update IDs in actor
    query4 = "UPDATE actor SET work_person_id=%s, person_id=%s WHERE work_person_id=%s"
    # for key, row in actor_df.iterrows():
    #     curr_person_id = row[1]
    #     if curr_person_id in merged_ids_dict:
    #         work_id = row[3]
    #         curr_work_person = row[0]
    #         curr_sequence_bits = curr_work_person[-2:]
    #         new_wpid = work_id + merged_ids_dict[curr_person_id] + curr_sequence_bits
    #         cursor.execute(query4, (new_wpid,merged_ids_dict[curr_person_id], curr_work_person))
    #         connection.commit()

def fix_birth_dates(cursor):
    person_df = get_all_person(cursor)
    neg = 0
    empty = 0
    # row[2] is birth_date and row[3] is death_date
    query1 = "UPDATE person SET birth_date=%s WHERE person_id=%s"
    for key, row in person_df.iterrows():
        if row[2]==row[3]:
            if row[2]!='':
                neg+=1
                cursor.execute(query1, ('', row[0]))
                connection.commit()
    print(neg)


def fix_more_people_dates(cursor):
    remove_birth_dates = ['0000047096', '0000022270', '0000069439', '0000040720', '0000067392', '0000066553', '0000064720', '0000063542', '0000067990', '0000058589', '0000051879', '0000009355', '0000052152', '0000039407', '0000038308', '0000069332', '0000065651', '0000064412', '0000059337']
    remove_death_dates = ['0000069439', '0000047096']
    query1 = "UPDATE person SET birth_date=%s WHERE person_id=%s"
    for person_id in remove_birth_dates:
        cursor.execute(query1, ('', person_id))
        connection.commit()
    query2 = "UPDATE person SET death_date=%s WHERE person_id=%s"
    for person_id in remove_death_dates:
        cursor.execute(query2, ('', person_id))
        connection.commit()


        



try:
    connection = mysql.connector.connect(host='localhost', 
                                        database='shows_db',
                                        user='root',
                                        password=password, use_pure=True, buffered=True)
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        # ------------------------------ RUN METHODS HERE ------------------------------------------------------#
        #fix_type_ids_2(cursor)
        fix_property_ids(cursor)


        print(cursor.rowcount)
        cursor.close()   
except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
