import requests
from bs4 import BeautifulSoup
import re
import json
from html import unescape

raw = requests.get("https://courses.illinois.edu/schedule/2025/fall")
processed = BeautifulSoup(raw.content, 'html.parser')
#print(processed.prettify())

# Put tags into a list (from txt file)

file = open('class_tags.txt')
tag_list = []
for line in file:
    temp = line[0:line.find(' ')]
    tag_list.append(temp)

file.close()

for e in tag_list:
    print(e)


# Loop for accessing site of each tag on the list 
for tag in tag_list:
    tag_page = requests.get("https://courses.illinois.edu/schedule/2025/fall/" + tag)
    tag_page_processed = BeautifulSoup(tag_page.content, 'html.parser')
    tag_page_string = tag_page_processed.get_text()
    
    to_find = tag + ' '
    index = 0
    numbers = []
    found = tag_page_string.find(to_find, index, len(tag_page_string))
    while(found != -1):
        temp = tag_page_string[found+len(tag)+1: found + len(tag)+4]
        index = found + 4
        found = tag_page_string.find(to_find, index, len(tag_page_string))
        if(temp[0].isalpha()):
            continue
        numbers.append(temp)

    t = tag + "_classes.txt"
    with open(t, "w") as file:
        for i in numbers:
            file.write(i)
            file.write("\n")

    # Loop for accessing site of each course 
    for class_id in numbers:
        section_page = requests.get(f"https://courses.illinois.edu/schedule/2025/fall/{tag}/{class_id}")
        print("https://courses.illinois.edu/schedule/2025/fall/" + tag + "/" + class_id)
        section_processed = BeautifulSoup(section_page.content, 'html.parser')
        
        scripts_list = section_processed.find_all("script")
        sectionDataObj = scripts_list[3]

        text = sectionDataObj.string
        find = re.search(r'var\s+sectionDataObj\s*=\s*(\[\{.*?\}\]);', text, re.DOTALL)
        raw_json = find.group(1)
        raw_json2 = unescape(raw_json)
        raw_json3 = raw_json2.replace('\\/', '/')

        data = json.loads(raw_json3)

        for d in data:
            for key in ['status', 'section', 'time', 'location', 'instructor', 'day', 'type']:
                if d.get(key):
                    d[key] = BeautifulSoup(d[key], 'html.parser').get_text(strip=True)

        title = tag + str(class_id) + ".json"
        with open(title, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

