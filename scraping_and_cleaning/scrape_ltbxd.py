# File: scrape_ltbxd.py
# Author: Alison Silldorff
# Date: 3/4/25
# Purpose: scrape all movies from a set of list URLs from Letterboxd


from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
import requests
import csv


url_list = ['https://letterboxd.com/lexielvc/list/musicals/',
            'https://letterboxd.com/lipe0004/list/musicals/',
            'https://letterboxd.com/fuchsiadyke/list/musicals/',
            'https://letterboxd.com/lilly_eve/list/musicals/',
            'https://letterboxd.com/hopefulwonderer/list/musicals/',
            'https://letterboxd.com/b4dwolf/list/musicals/',
            'https://letterboxd.com/jadedbee22/list/musical-theater/',
            'https://letterboxd.com/mckenseyh/list/musical-theater/',
            'https://letterboxd.com/geeshrimps/list/musical-theater/',
            'https://letterboxd.com/frnkieromustdie/list/musical-theater/',
            'https://letterboxd.com/mediocremae/list/musical-theater/',
            'https://letterboxd.com/benji_0/list/musical-theater/',
            'https://letterboxd.com/sammyslife/list/musical-theater/',
            'https://letterboxd.com/mcfroggyswaggy/list/musical-theater/',
            'https://letterboxd.com/amazingpransin/list/musical-theater/',
            'https://letterboxd.com/heathercate/list/musical-theater/',
            'https://letterboxd.com/raquelbraga242/list/musical-theatre/',
            'https://letterboxd.com/emptymasks/list/of-phantoms-felines-and-french-revolutions/',
            'https://letterboxd.com/tunamilkshake/list/musical-theatre/',
            'https://letterboxd.com/winecooler123/list/musical-theatre/',
            'https://letterboxd.com/silkensail/list/musical-theatre/',
            'https://letterboxd.com/rendierman/list/musical-theatre/',
            'https://letterboxd.com/jellyjam_24/list/musical-theatre/',
            'https://letterboxd.com/natasa_romanof/list/musical-theatre-magic/',
            'https://letterboxd.com/spn_cowboy/list/musical-theatre/',
            'https://letterboxd.com/hamishpbox/list/musical-theatre/',
            'https://letterboxd.com/osling/list/musical-theatre/',
            'https://letterboxd.com/linamollebo/list/musical-theatre/',
            'https://letterboxd.com/avery_pm/list/musical-theatre/',
            'https://letterboxd.com/barbiegirl10/list/musical-theatre/',
            'https://letterboxd.com/tilwatchesfilms/list/musical-theatre/',
            'https://letterboxd.com/isabelvals/list/musical-theatre/',
            'https://letterboxd.com/jusido/list/broadway/',
            'https://letterboxd.com/sar4/list/broadway/',
            'https://letterboxd.com/ndrslls/list/broadway/',
            'https://letterboxd.com/camcraw2207/list/broadway/',
            'https://letterboxd.com/sachimi/list/broadway/',
            'https://letterboxd.com/jimenazzo/list/broadway/',
            'https://letterboxd.com/anaverdile/list/broadway/',
            'https://letterboxd.com/eddanny/list/broadway-1/',
            'https://letterboxd.com/joepelizzari/list/broadway/',
            'https://letterboxd.com/babyjuules/list/broadway/',
            'https://letterboxd.com/manusaads/list/broadway/',
            'https://letterboxd.com/pilumonte/list/broadway/',
            'https://letterboxd.com/henry_swans0n/list/broadway/',
            'https://letterboxd.com/lill_grevt/list/broadway/',
            'https://letterboxd.com/babyjuules/list/broadway/',
            'https://letterboxd.com/emhami109/list/broadway/',
            'https://letterboxd.com/henry_swans0n/list/broadway/',
            'https://letterboxd.com/pilumonte/list/broadway/',
            'https://letterboxd.com/lill_grevt/list/broadway/',
            'https://letterboxd.com/dhrdbswo/list/broadway/',
            'https://letterboxd.com/liaonpluto/list/broadway-musicals/',
            'https://letterboxd.com/igormania/list/broadway-musicals/',
            'https://letterboxd.com/moose7533/list/broadway-musicals/',
            'https://letterboxd.com/grace__472/list/broadway-musicals/',
            'https://letterboxd.com/ieb/list/broadway-musicals/',
            'https://letterboxd.com/graaccee/list/broadway-musicals/',
            'https://letterboxd.com/mochisumo15/list/broadway-musicals/',
            'https://letterboxd.com/frvlrs/list/broadway-musicals/',
            'https://letterboxd.com/ieb/list/broadway-musicals/',
            'https://letterboxd.com/coolcatcassie/list/broadway-musicals/',
            'https://letterboxd.com/nilssonruben/list/broadway-musicals/',
            'https://letterboxd.com/melina1384/list/broadway-musicals/',
            'https://letterboxd.com/lucafonteau/list/broadway-musicals-to-film/',
            ]
#url_list = ['https://letterboxd.com/igormania/list/broadway-musicals/']

def scrape_lists():
    browser = webdriver.Firefox()

    movie_urls = set()

    for list in url_list:
        print(list)
        browser.get(list)
        try:
            num_pages = int(browser.find_elements(By.CLASS_NAME, "paginate-page")[-1].text)
        except:
            num_pages = 1
        i = 1
        while i <= num_pages: 
            if i > 1:
                print('here')
                browser.get(list + "page/" + str(i)+"/")
            movies = browser.find_elements(By.CLASS_NAME, "poster-container")
            for movie in movies:
                movie_info_elem = movie.find_element(By.TAG_NAME, "div")
                movie_url = movie_info_elem.get_attribute("data-film-slug")
                #print(movie_url)
                full_movie_url = "letterboxd.com/film/" + movie_url
                if full_movie_url not in movie_urls:
                    #print(full_movie_url)
                    movie_urls.add(full_movie_url)
            i += 1

    with open("ltbxd_movies.csv", 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(movie_urls)

            




        # try:
        #     resdict, smallreslist = getdetails(browser, "https://ibdb.com" + u)
        # except:
        #     resdict = {"url":u , "title":'', "tags":'', "opening":'', "preview":'', "num_previews":'', "closing":'', "num_perfs":'', "people":'', "people_links":'', "opening_cast":'', "replacement_cast":''}
        #     smallreslist = [u, '', '', '', '', '', '']
        # small_infolist.append(smallreslist)
        # large_infodict.update({u:resdict})


def tmdb_to_ltbxd():
    browser = webdriver.Firefox()
    file = "tmdb_ids_prelim.csv"
    labeled_films = set()
    with open(file) as rfile:
        reader = csv.reader(rfile)
        for row in reader:
            browser.get("https://letterboxd.com/tmdb/"+row[0])
            labeled_films.add(str(browser.current_url))
    
    print(labeled_films)
    
    unlabeled_films = set()
    with open("ltbxd_movies.csv") as rfile:
        reader = csv.reader(rfile)
        films = next(reader)
        for url in films:
            url = "https://" + url + '/'
            if url not in labeled_films:
                unlabeled_films.add(url)
            else:
                print("here")

    with open("ltbxd_movies_unlabeled.csv", 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(unlabeled_films)

#scrape_lists()
tmdb_to_ltbxd()