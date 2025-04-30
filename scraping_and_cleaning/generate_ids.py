# File: generate_ids
# Author: Alison Silldorff
# Date: 1/3/25
# Purpose: Using the proerty and sequence digits that we have generated, get the tag id and make a full ID.

import json
import csv

file1 = "musicals info small with ids.csv"
file2 = open("musicals_info.json")

# keep track of the tag digits for each URL. url : digits (int)
id = {}

# musicals is the json file in dictionary form.
musicals = json.load(file2)
musicals_values = musicals.values()
# iterate through all values in the dictionary
# for row in musicals.values():
#     print(row["tags"])

with open(file1) as file_obj:
    reader = csv.reader(file_obj)
    # iterate through every URL that we gave an ID
    for row in reader:
        full_url = row[1]
        if full_url == "url":
            continue
        url = full_url.split("ibdb.com")[1]
        tags = musicals[url]["tags"]
        if "Original" in tags:
            type = "11"
        elif "Revival" in tags:
            type = "12"
        else:
            print(url)
            type = "13"
        property_id = str(row[3]).zfill(4)
        sequence_id = str(row[4]).zfill(2)
        full_id = property_id + sequence_id + type
        print(full_id)

        id.update({full_url:full_id})
#print(type_digits)

json_object = json.dumps(id, indent=4)
with open("urls_and_ids.json", "w") as outfile:
    outfile.write(json_object)


        



# at each url, go to that spot in the dictionary and look at the tags.
# depending on the tags, assign them a tag id.