# File: scrape_tmdb.py
# Author: Alison Silldorff
# Date: 11/20/24
# Purpose: scrape all movies in the "music" genre off of TMDB

import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import csv
import unicodedata
from selenium import webdriver
import statistics
from selenium.webdriver.common.by import By
import numpy as np


password = open("C:\\Users\\12676\\mysqlinfo", 'r').read()
key = open("C:\\Users\\12676\\tmdb_info", 'r').read()

# Simple python solution to do this (from the internet)
def scrape_all_music():
    df = pd.DataFrame()
    for i in range(1,2153):
        url = f'https://api.themoviedb.org/3/discover/movie?api_key={key}&language=en-US&sort_by=release_date.desc&with_genres=10402&page={i}'
        response = requests.get(url)
        temporary_df = pd.DataFrame(response.json()['results'])
        df = pd.concat([df,temporary_df],ignore_index=True)
    print(df)

def initial_scrape(cursor):
    sql_query = "SELECT DISTINCT title FROM stage_work"
    cursor.execute(sql_query)
    connection.commit()
    res = cursor.fetchall()
    titles = []
    for title in res:
        the_title = title[0].replace(" ", "-")
        titles.append(the_title)

    # something here to turn each title into the hyphenated version?
    # title = ["newsies", "a little night music", "cats"]
    res_dict = {}
    for title in titles:
        print(title)
        response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={key}&query={title}&with_genres=10402")
        res = response.json()
        res_dict.update({title:res.get("total_results")})

    json_object = json.dumps(res_dict, indent=4)
    with open("movie_counts.json", "w") as outfile:
        outfile.write(json_object)

    return res_dict

# from all distinct musical titles in my DB, get all movies that share that title. 
# write these movies onto a CSV file "possible_movies.csv"
def scrape_all_urls(cursor):
    sql_query = "SELECT DISTINCT title FROM stage_work"
    cursor.execute(sql_query)
    connection.commit()
    res = cursor.fetchall()
    titles = []
    for title in res:
        the_title = title[0].replace(" ", "-")
        titles.append(the_title)

    #titles = ["newsies", "a-little-night-music"]
    movie_list = []
    for title in titles:
        print(title)
        response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={key}&query={title}&with_genres=10402")
        res = response.json()
        total_pages = res.get("total_pages")
        total_results = res.get("total_results")
        i = 0
        while i < total_pages:
            if i > 0:
                # replace with page version
                new_response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={key}&query={title}&with_genres=10402&page={i}")
                new_res = new_response.json()
                movies = new_res.get("results")
            else:
                movies = res.get("results") # this is the list of all the search results
 
            for movie in movies:
                if movie.get("genre_ids") is not None and 10402 not in movie.get("genre_ids"):
                    continue
                movie_id = str(movie.get("id"))
                movie_url = "https://www.themoviedb.org/movie/" + movie_id
                curr = [total_results, total_pages, title, movie.get("original_title"), movie.get("title"), movie_url, movie_id]
                movie_list.append(curr)
            i+=1

    with open("possible_movies.csv", 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["total_results","pages of results","musical title", "original title", "title", "url", "id"])
        for row in movie_list:
            writer.writerow(row)

    print(movie_list)




def count_mean():
    with open("movie_counts.json") as infile:
        counts_dict = json.load(infile)

    vals = counts_dict.values()
    print(statistics.mean(vals))
    print(statistics.mode(vals))
    print(sum(vals))
    print(statistics.median(vals))



def concat_tmdb_lists():
    ids = [21608, 220201, 190849, 240462]
    all_movies = set()
    final_list = []
    for id in ids:
        print(id)
        response = requests.get(f"https://api.themoviedb.org/3/list/{id}?api_key={key}")
        res = response.json()
        total_pages = res.get("total_pages")
        total_results = res.get("total_results")
        i = 1
        while i <= total_pages:
            if i > 1:
                # replace with page version
                new_response = requests.get(f"https://api.themoviedb.org/3/list/{id}?api_key={key}&page={i}")
                new_res = new_response.json()
                movies = new_res.get("items")
            else:
                movies = res.get("items") # this is the list of all the search results
 
            for movie in movies:
                movie_id = str(movie.get("id"))
                if movie_id in all_movies:
                    continue
                all_movies.add(movie_id)
                movie_url = "https://www.themoviedb.org/movie/" + movie_id
                final_list.append([movie_id, movie_url, movie.get("original_title"), movie.get("title")])
            i+=1

    with open("more_possible_movies.csv", 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "url" "original title", "title"])
        for row in final_list:
            writer.writerow(row)

def get_person_details(p_tmdbid):
    person_response = requests.get(f"https://api.themoviedb.org/3/person/{p_tmdbid}?api_key={key}")
    person_res = person_response.json()
    birth_date = person_res.get("birthday")
    death_date = person_res.get("deathday")
    birth_place = person_res.get("place_of_birth")
    name = person_res.get("name")
    tmdb_url = "themoviedb.org/person/" + str(p_tmdbid)
    p_popularity = person_res.get("popularity")

    return birth_date, death_date, birth_place, name, tmdb_url, p_popularity


def get_movie_details():
    file = "TMDB movies.csv"
    movies_df_sheets = pd.read_csv(file)
    i = 0
    movies_df = pd.DataFrame(columns=['work_id', 'property_id', 'type_id', 'tmdb_url', 'title', 
                                      'release_date', 'us_origin', 'tmdb_popularity', 'budget', 
                                      'revenue', 'tmdb_rating', 'tmdb_vote_count', 'assoc_stage_work_id'])
    movies_df_sheets = movies_df_sheets.fillna('')
    print(movies_df_sheets)
    # keep track of the tag digits for each URL. url : digits (int)
    sequence_dict = {}
    # the largest person_id in person table right now is 0000050432. 10 characters for a person_id
    next_person_id = 50433
    visited_people = set() # use this to keep track of which people (based on their TMDB id), we have already gone through

    person_df = pd.DataFrame(columns=['person_id', 'name', 'birth_date', 'death_date', 
                                      'birth_place', 'gender', 'tmdb_url', 'tmdb_popularity'])
    work_person_df = pd.DataFrame(columns=['work_person_id', 'work_id', 'person_id', 'name', 'property_id', 'type_id', 'role', 'tmdb_url'])
    actor_df = pd.DataFrame(columns=['work_person_id', 'work_id', 'person_id', 'name', 'property_id', 'type_id', 'role', 'tmdb_url'])
    # index is the gender code that corresponds to each entry
    tmdb_genders = ['', 'Female', 'Male', 'Non-binary']

    screen_work_df = pd.DataFrame(columns=['work_id', 'property_id', 'type_id', 'title', 
                                           'release_date', 'tmdb_url', 'us_origin', 'tmdb_popularity',
                                           'budget', 'revenue', 'tmdb_rating', 'tmdb_vote_count', 'assoc_stage_work_id'])
    for key, value in movies_df_sheets.iterrows():
        tmdbid = value['TMDB id']
        print(tmdbid)
        response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdbid}?api_key={key}7&append_to_response=credits")
        res = response.json()
        # I want: title, release date, origin country, budget, revenue, popularity, cast credits, crew credits, and vote average
        title = res.get("title")
        release_date = res.get("release_date")
        origin_country = res.get("origin_country") #note: gives a list
        if "US" in origin_country:
            us_origin = 1
        else:
            us_origin = 0
        popularity = res.get("popularity")
        budget = res.get("budget")
        revenue = res.get("revenue")
        vote_average = res.get("vote_average")
        vote_count = res.get("vote_count")
        tmdb_url = "themoviedb.org/movie/" + str(tmdbid)
        if res.get("credits") is not None:
            cast_credits = res.get("credits").get("cast")
            crew_credits = res.get("credits").get("crew")
        
        # generate a work ID:
        property_id = str(value['property_id']).zfill(4)
        if value["Type"] == 'movie':
            type_id = '21'
        elif value["Type"] == 'proshot (Broadway)':
            type_id = '22'
        elif value["Type"] == 'proshot (other)':
            type_id = '23'
        elif value["Type"] == 'other':
            type_id = '24'
        
        if property_id not in sequence_dict:
            sequence_dict[property_id] = '00'
        else:
            sequence_dict[property_id] = str(int(sequence_dict[property_id]) + 1).zfill(2)
        sequence_id = sequence_dict[property_id]
        work_id = property_id + sequence_id + type_id 
        if value['assoc_stage_work_id'] != '':
            assoc_stage_work_id = str(int(value['assoc_stage_work_id'])).zfill(8)
        else:
            assoc_stage_work_id = ''
        
        screen_work_df.loc[len(screen_work_df)] = [work_id, property_id, type_id, title, 
                                           release_date, tmdb_url, us_origin, popularity,
                                           budget, revenue, vote_average, vote_count, assoc_stage_work_id]
    #     work_person_ids = {}
    #     # parse credits:
    #     for person in cast_credits:
    #         p_tmdbid= person['id']
    #         if p_tmdbid not in visited_people:
    #             curr_person_id = str(next_person_id).zfill(10)
    #             next_person_id += 1
    #             # get their info, put them into person_df
    #             visited_people.add(p_tmdbid)
    #             gender = tmdb_genders[int(person['gender'])]
    #             birth_date, death_date, birth_place, name, tmdb_url, p_popularity = get_person_details(p_tmdbid)
    #             person_df.loc[len(person_df)] = [curr_person_id, name, birth_date, death_date, birth_place, gender, tmdb_url, p_popularity]
    #         else:
    #             curr_person_id = person_df.loc[person_df['person_id']==curr_person_id, 'person_id'].values[0]
            
    #         temp_wpid = work_id + curr_person_id
    #         if temp_wpid in work_person_ids:
    #             work_person_id = temp_wpid + str(work_person_ids[temp_wpid]+ 1).zfill(2)
    #             work_person_ids[temp_wpid]+=1
    #         else:
    #             work_person_id = temp_wpid + '00'
    #             work_person_ids.update({temp_wpid:0})
            
    #         # put them into work_person_df and actor_df
    #         work_person_df.loc[len(work_person_df)] = [work_person_id, work_id, curr_person_id, person_df.loc[person_df['person_id']==curr_person_id, 'name'].values[0], property_id, type_id, 'actor', person_df.loc[person_df['person_id']==curr_person_id, 'tmdb_url'].values[0]]
    #         actor_df.loc[len(work_person_df)] = [work_person_id, work_id, curr_person_id, person_df.loc[person_df['person_id']==curr_person_id, 'name'].values[0], property_id, type_id, person['character'], person_df.loc[person_df['person_id']==curr_person_id, 'tmdb_url'].values[0]]
    #         #print(work_person_df)
        
    #     for person in crew_credits:
    #         p_tmdbid= person['id']
    #         if p_tmdbid not in visited_people:
    #             curr_person_id = str(next_person_id).zfill(10)
    #             next_person_id += 1
    #             # get their info, put them into person_df
    #             visited_people.add(p_tmdbid)
    #             gender = tmdb_genders[int(person['gender'])]
    #             birth_date, death_date, birth_place, name, tmdb_url, p_popularity = get_person_details(p_tmdbid)
    #             person_df.loc[len(person_df)] = [curr_person_id, name, birth_date, death_date, birth_place, gender, tmdb_url, p_popularity]
    #         else:
    #             curr_person_id = person_df.loc[person_df['person_id']==curr_person_id, 'person_id'].values[0]
    
    #         temp_wpid = work_id + curr_person_id
    #         if temp_wpid in work_person_ids:
    #             work_person_id = temp_wpid + str(work_person_ids[temp_wpid]+ 1).zfill(2)
    #             work_person_ids[temp_wpid]+=1
    #         else:
    #             work_person_id = temp_wpid + '00'
    #             work_person_ids.update({temp_wpid:0})

    #         work_person_df.loc[len(work_person_df)] = [work_person_id, work_id, curr_person_id, person_df.loc[person_df['person_id']==curr_person_id, 'name'].values[0], property_id, type_id, person['job'], person_df.loc[person_df['person_id']==curr_person_id, 'tmdb_url'].values[0]]
    #             # put them into work_person_df
        
    #     # print([tmdbid, title, release_date, origin_country, popularity, budget, revenue, 
    #     #        vote_average, vote_count])
    #     # i+=1
    #     # if i>5:
    #     #     break

    
    # person_df.to_csv('tmdb_person.csv')
    # work_person_df.to_csv('tmdb_work_person.csv')
    # actor_df.to_csv('tmdb_actor.csv')
    screen_work_df.to_csv('screen_works.csv')


def remove_btl():
    work_person_df = pd.read_csv("tmdb_work_person.csv")
    work_person_df = work_person_df.fillna('')
    # this is the same list I used for my JP. And adding a few musical-related ones.
    atl = set(["Co-Director", "Co-Executive Producer", 
          "Co-Producer", "Co-Writer", "Director", 
          "Director of Photography", "Executive Producer", 
          "Producer", "Screenplay", "Screenstory", "actor", 
          "Book", "Choreography", "Choreographer", "Lyricist", 
          "Music", "Musical", "Orchestrator", "Music Arranger", 
          "Orchestrator", "Original Music Composer", "Songs", "Story", "Writer"])
    atl_work_person_df = pd.DataFrame(columns=['work_person_id', 'work_id', 'person_id', 'name', 'property_id', 'type_id', 'role', 'tmdb_url'])
    for key, row in work_person_df.iterrows():
        if row['role'] in atl:
            atl_work_person_df.loc[len(atl_work_person_df)] = row

    atl_work_person_df.to_csv('tmdb_atl_work_person.csv')
        


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
        get_movie_details()
        
        print(cursor.rowcount)
        cursor.close()   
except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
