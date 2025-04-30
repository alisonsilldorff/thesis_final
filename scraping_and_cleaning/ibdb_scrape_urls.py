# Auhtor: Alison Silldorff
# Created: 10/16/2024
# File: scrape_ibdb_urls.py
# Purpose: Scrape URLs from an IBDB search page

from bs4 import BeautifulSoup
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import csv

# from our file of an ibdb search, get all the URLs. 
def geturls(file):
    soup1 = BeautifulSoup(file, 'html.parser')
    urls_code = soup1.find_all(class_="col s12")
    urls = []
    for elem in urls_code:
        elem_a = elem.find('a')
        if elem_a is not None:
            elem_href = elem_a.get('href')
            if "broadway-production" in elem_href:
                urls.append(elem_href)
    return urls

# from an HTML file of broadway theater pages, pull out all of the show URLs that are musicals.
def get_musicals(file):
    soup1 = BeautifulSoup(file, 'html.parser')
    row_class = "row"
    show_class = "col s12 m8"
    tags_class = "tag-block tag-align right-align valign hide-on-small-and-down venue-productions-list-tags"
    rows_code = soup1.find_all('div', class_=row_class)
    urls = []
    for elem in rows_code:
        if len(elem['class'])>1:
            continue
        tags_outer = elem.find('div', class_=tags_class)
        if tags_outer is not None:
            tags=tags_outer.find_all('i')
            i = 0
            while i < len(tags):
                tags[i]=tags[i].text
                i+=1
            if "Musical" in tags or "Musical " in tags:
                #print(elem['class'])
                urls.append(elem.find('div', class_=show_class).find('a').get('href'))
    return urls



def get_title(browser):
    # get title
    TITLE_CLASS = "title-label"
    title = browser.find_element(By.CLASS_NAME, TITLE_CLASS).text
    #print(browser.find_element(By.CSS_SELECTOR, ".title-label").text)
    return title


def get_tags(browser):
    # get the tags
    TAGS_CLASS = ".col.s12.txt-paddings.tag-block-compact"
    tags_elems_all = browser.find_elements(By.CSS_SELECTOR, TAGS_CLASS)
    tags_elems = tags_elems_all[1].find_elements(By.TAG_NAME, 'i')
    tags = []
    for elem in tags_elems:
        #print(elem.text)
        tags.append(elem.text)
    
    return tags

def get_opening(browser):
    OPENING_DATE_CLASS = ".col.s5.m3.l5.txt-paddings"
    opening = browser.find_element(By.CSS_SELECTOR, OPENING_DATE_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
    return opening

# get the first preview date
# Note: some shows don't have a preview date
def get_first_preview(browser):
    try: 
        PREVIEW_DATE_CLASS = ".col.s12.txt-paddings"
        preview_classes = browser.find_elements(By.CSS_SELECTOR, PREVIEW_DATE_CLASS)
        # magic number 1 because it is the second occurence of this class/class prefix that we want to use!
        preview = preview_classes[1].find_element(By.CLASS_NAME, "xt-main-title").text
    except:
        preview = ''
    return preview

# get the number of previews (note: some shows don't have a preview date)
def get_num_previews(browser):
    try:
        NUM_PREVIEWS_CLASS = ".col.s5.m6.l5.txt-paddings"
        num_previews = browser.find_element(By.CSS_SELECTOR, NUM_PREVIEWS_CLASS).find_element(By.CLASS_NAME, "xt-main-title").text
    except:
        num_previews = ''
    return num_previews

# get the closing date and number of performances
def get_closing_num_perfs(browser):
    CLOSING_DATE_CLASS = ".col.s7.m6.l7.txt-paddings.vertical-divider"
    closing_and_perfs = browser.find_elements(By.CSS_SELECTOR, CLOSING_DATE_CLASS)
    i = 0
    closing = ''
    num_perfs = ''
    try: 
        while i < len(closing_and_perfs):
            curr = closing_and_perfs[i].find_element(By.CLASS_NAME, "xt-main-title").text
            if i == 0:
                closing = curr
            else:
                num_perfs = curr
            i += 1
    except:
        closing = ''
        num_perfs = ''
    return closing, num_perfs

# get people info (who wrote the show etc)
def get_people(browser):
    OUTER_PROD_CLASS = ".collapsible-body.prod-people"
    try:
        stuff = browser.find_element(By.ID, "ProductionStaff").find_elements(By.CSS_SELECTOR, ".col.s12")
        people_res = []
        links = []
        for elem in stuff:
            linestr = elem.text
            if "Book by" in linestr and "Lyrics by" in linestr:
                people_res = linestr.split(";")
                linkshtml = elem.find_elements(By.TAG_NAME, 'a')
                for link in linkshtml:
                    links.append(link.get_attribute('href'))
                break
    except:
        people_res = []
        links = []
    return people_res, links

# get the opening night cast
def get_opening_cast(browser):
    OUTER_ID = "OpeningNightCast"
    try:
        cast = browser.find_element(By.ID, OUTER_ID).find_elements(By.CSS_SELECTOR, ".row.mobile-a-align")
        # [actor url, actor name, {role name:role dates}, Broadway debut (true/false)]
        # if there is no date, put an empty string in both. Later I'll populate this with the opening date and the current date etc
        people_res = {}
        mult_roles = False
        for elem in cast:
            curr_res = {}
            stuff = elem.find_elements(By.CSS_SELECTOR, ".col.m4.s12")

            # if this is the first time we are encountering this actor, get their name, url, and debut (t/f)
            if not mult_roles:
                try:
                    first = stuff[0].find_element(By.TAG_NAME, 'a')
                    actor = first.get_attribute('text')
                    actor_url = first.get_attribute('href')
                    try:
                        # see whether it is an actor's Broadway debut
                        debut_html = stuff[0].find_element(By.CSS_SELECTOR, ".role_status").get_attribute('outerHTML').split('>')
                        debut_html = debut_html[1].split('<')
                        if debut_html[0] == "Broadway debut":
                            debut= True
                        else:
                            debut=False
                    except:
                        debut = False         
                except:
                    actor = ''
                    actor_url = ''
                    debut = False

            # get the role
            second = stuff[1].get_attribute('innerHTML')
            role = second.split('<')[0].strip()

            # get the role dates
            role_dates = stuff[2].find_element(By.CLASS_NAME, "role_dates").get_attribute('text')
            if role_dates is None:
                role_dates = ''

            if not mult_roles:
                curr_res = {"url":actor_url, "actor":actor, "roles":{role:role_dates}, "debut":debut}
                people_res.update({actor_url:curr_res})
            else:
                people_res[actor_url]["roles"].update({role:role_dates})
                #people_res[-1][2].update({role:role_dates})

            if elem.get_attribute('class') == "row mobile-a-align ":
                mult_roles = False
            elif elem.get_attribute('class') == 'row mobile-a-align clear-marg':
                mult_roles = True
    except:
        people_res = {}

    return people_res

def get_replacement_cast(browser):
    OUTER_ID = "Replacements"
    try:
        cast = browser.find_element(By.ID, OUTER_ID).find_elements(By.CSS_SELECTOR, ".row.mobile-a-align")
        people_res = {}
        # [actor url, actor name, {role name:role dates}, Broadway debut (true/false)]
        # if there is no date, put an empty string in both. Later I'll populate this with the opening date and the current date or wtvr
        mult_roles = False
        for elem in cast:
            curr_res = {}
            stuff = elem.find_elements(By.CSS_SELECTOR, ".col.m4.s12")

            # if this is the first time we are encountering this actor, get their name, url, and debut (t/f)
            if not mult_roles:
                try:
                    first = stuff[0].find_element(By.TAG_NAME, 'a')
                    actor = first.get_attribute('text')
                    actor_url = first.get_attribute('href')
                    try:
                        # see whether it is an actor's Broadway debut
                        debut_html = stuff[0].find_element(By.CSS_SELECTOR, ".role_status").get_attribute('outerHTML').split('>')
                        debut_html = debut_html[1].split('<')
                        if debut_html[0] == "Broadway debut":
                            debut= True
                        else:
                            debut=False
                    except:
                        debut = False         
                except:
                    actor = ''
                    actor_url = ''
                    debut = False

            # get the role
            second = stuff[1].get_attribute('innerHTML')
            role = second.split('<')[0].strip()

            # get the role dates
            role_dates = stuff[2].find_element(By.CLASS_NAME, "role_dates").get_attribute('text')
            if role_dates is None:
                role_dates = ''

            if not mult_roles:
                curr_res = {"url":actor_url, "actor":actor, "roles":{role:role_dates}, "debut":debut}
                people_res.update({actor_url:curr_res})
            else:
                people_res[actor_url]["roles"].update({role:role_dates})

            if elem.get_attribute('class') == "row mobile-a-align ":
                mult_roles = False
            elif elem.get_attribute('class') == 'row mobile-a-align clear-marg':
                mult_roles = True
    except:
        people_res = {}

    return people_res


# gets details for an IBDB url, returns a list of all those details
# [title, ___, ___, ...]
def getdetails(browser, url):
    browser.get(url)
    print(url)

    title = get_title(browser)
    tags = get_tags(browser)
    opening = get_opening(browser)
    preview = get_first_preview(browser)
    num_previews = get_num_previews(browser)
    closing, num_perfs = get_closing_num_perfs(browser)
    people_res, links = get_people(browser)
    opening_cast_res = get_opening_cast(browser)
    replacement_cast_res = get_replacement_cast(browser)

    dict = {"url": url, "title":title, "tags":tags, "opening":opening, "preview":preview, "num_previews":num_previews, "closing":closing, "num_perfs":num_perfs, "people":people_res, "people_links":links, "opening_cast":opening_cast_res, "replacement_cast":replacement_cast_res}
    small_list = [url, title, opening, preview, num_previews, closing, num_perfs]
    return dict, small_list

# file2 = open("thrs_all_html", 'r', encoding='utf-8').read()
# urls = get_musicals(file2)
# print(urls)

#urls = ["/broadway-production/chicago-4804", "/broadway-production/the-outsiders-537824"]
urls = ["/broadway-production/spring-awakening-448811", "/broadway-production/sweeney-todd-400379", "/broadway-production/hello-dolly-4308", "/broadway-production/the-best-little-whorehouse-goes-public-4609", "/broadway-production/fine-and-dandy-9442", "/broadway-production/the-dancing-girl-9195", "/broadway-production/the-passing-show-of-1922-9114", "/broadway-production/the-regatta-girl-415940"]

browser = webdriver.Firefox()
large_infodict = {}
small_infolist = [["url", "title", "opening_date", "first_preview", "num_previews", "closing_date", "num_perfs"]]
# For each URL, get all of the info and update the small list and large dictionary
for u in urls:
    if u in large_infodict:
        continue
    try:
        resdict, smallreslist = getdetails(browser, "https://ibdb.com" + u)
    except:
        resdict = {"url":u , "title":'', "tags":'', "opening":'', "preview":'', "num_previews":'', "closing":'', "num_perfs":'', "people":'', "people_links":'', "opening_cast":'', "replacement_cast":''}
        smallreslist = [u, '', '', '', '', '', '']
    small_infolist.append(smallreslist)
    large_infodict.update({u:resdict})

# Write the full set of info to a JSON file
json_object = json.dumps(large_infodict, indent=4)
with open("extra_musicals_info.json", "w") as outfile:
    outfile.write(json_object)


# Write the smaller list of info to a CSV file
with open("extra_musicals_info_small.csv", 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(small_infolist)

# browser.get("https://www.ibdb.com/broadway-production/hamilton-499521")
# actor_info = get_replacement_cast(browser)
# for row in actor_info:
#     print(row)
