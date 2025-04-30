# Author: Alison Silldorff
# Date Created: 10/16/24
# ibdb_scrape.py
# Purpose: scrape IBDB data from a single page for various musical theater metrics

from bs4 import BeautifulSoup
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
import requests

parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
args = parser.parse_args()


# use this for the HTML of the search page
filename = "ibdb_search"
file1 = open(filename, 'r', encoding='utf-8').read()

soup1 = BeautifulSoup(file1, 'html.parser')
urls_code = soup1.find_all(class_="col s12")
urls = []
for elem in urls_code:
    #urls.append(elem.find('a').find('href'))
    elem_a = elem.find('a')
    if elem_a is not None:
        urls.append("https://ibdb.com/" + elem_a.get('href'))
print(urls)
print(len(urls))

#for url in urls:
response = requests.post(urls[1])
print(response)
# curlUrl = "curl https://ibdb.con"
# status, output = subprocess.getstatusoutput(curlUrl)
# print(output)

# driver = webdriver.Firefox()
# driver.get(URL)

# here, i need to output the HTML code of the URL to a file that the soup uses.

filename = args.file
file = open(filename, 'r').read()

soup = BeautifulSoup(file, 'html.parser')

# get the show title
TITLE_CLASS = "title-label"
title = soup.find(class_ = TITLE_CLASS).text
print("title: " + title)

# get the tags
TAGS_CLASS = "col s12 txt-paddings tag-block-compact"
tags = soup.find(class_ = TAGS_CLASS).find_all('i')
i = 0
while i < len(tags):
    tags[i] = tags[i].text
    i += 1
print(tags)

# get the opening date
OPENING_DATE_CLASS = "col s5 m3 l5 txt-paddings"
opening = soup.find(class_ = OPENING_DATE_CLASS).find(class_ = "xt-main-title").text
print("opening: ",opening)

# get the first preview date
PREVIEW_DATE_CLASS = "col s3 txt-paddings vertical-divider hide-on-small-and-down hide-on-large-only show-on-medium"
preview = soup.find(class_ = PREVIEW_DATE_CLASS).find(class_ = "xt-main-title").text
print("preview: " + preview)

# get the number of previews
NUM_PREVIEWS_CLASS = "col s5 m6 l5 txt-paddings"
num_previews = soup.find(class_=NUM_PREVIEWS_CLASS).find(class_="xt-main-title").text
print("num_previews: " + num_previews)

# get the closing date and number of performances
CLOSING_DATE_CLASS = "col s7 m6 l7 txt-paddings vertical-divider"
closing_and_performances = soup.find_all(class_ = CLOSING_DATE_CLASS)
i = 0
closing = ''
num_performances = ''
for elem in closing_and_performances:
    curr = elem.find(class_ = "xt-main-title").text
    if i == 0:
        closing = curr
    else:
        num_performances = curr
    i += 1
print("Closing: "+ closing)
print("num_performances: " + num_performances)

# i think for all the people I have to pull them all down bc it isn't consistent across pages.

def parse_prodpeople(line):
    i = 0
    creds_dict = {}
    curr_key = ''
    for elem in line:
        # lines either are a key, a value, or a comma
        # detect key
        if i == 0 or ';' in elem:
            creds_dict.update({elem:[]})
            curr_key = elem
        # comma case
        elif ',' in elem:
            continue
        # content case
        else:
            new_value_list = creds_dict.get(curr_key)
            new_value_list.append(elem.text)
            creds_dict.update({curr_key:new_value_list})
        i += 1
    return creds_dict 


# get all prod team info
OUTER_PROD_CLASS = "collapsible-body prod-people"
stuff = soup.find(class_ = OUTER_PROD_CLASS).find(id = "ProductionStaff")
res = {}
for line in stuff:
    linestr = str(line)
    # dependent on this section always having these words in them
    if "Book by" in linestr and "Lyrics by" in linestr:
        res = parse_prodpeople(line)

for key in res:
    print(key)
    print(res.get(key))

# get the link to this page on IBDB ?


# TA_CLASS = "kgrOn o"
# for elem in soup.find_all(class_=TA_CLASS):
#     inner = elem.find_all('a')
#     print("tripadvisor.com"+ inner[1].get('href') + ' ,')

