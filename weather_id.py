import requests
from bs4 import BeautifulSoup
import re

xml = requests.get('http://weather.livedoor.com/forecast/rss/primary_area.xml')
soup = BeautifulSoup(xml.text, 'html.parser')
place_id = []
for tag in soup.findAll('city'):
    try:
        tmp = []
        place_name = tag.get('title')
        id = tag.get('id')
        tmp.append(place_name)
        tmp.append(id)
        place_id.append(tmp)
    except:
        pass
place_id = dict(place_id)

with open('data/place_code.txt', 'w', encoding='utf-8') as f:
    for name, id in place_id.items():
        f.write(name + "\t" + id + "\n")


