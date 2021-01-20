from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import re
from urllib.request import urlopen
import json
from pandas.io.json import json_normalize
import pandas as pd, numpy as np
import os
import requests

# username profile to scrape
username='willsmith'

# path to chromedriver
browser = webdriver.Chrome('C:/Program Files (x86)/Google/Chrome/Application/chromedriver')
browser.get('https://www.instagram.com/'+username+'/?hl=en')
Pagelength = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# uncomment to scrape a hashtag
#hashtag='bigdata'
#browser = webdriver.Chrome('C:/Program Files (x86)/Google/Chrome/Application/chromedriver')
#browser.get('https://www.instagram.com/explore/tags/'+hashtag)
#Pagelength = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# extract links from user profile page
links=[]
source = browser.page_source
data=bs(source, 'html.parser')
body = data.find('body')
script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
page_json = script.string.split(' = ', 1)[1].rstrip(';')
data = json.loads(page_json)
# try 'script.string' instead of script.text if you get error on index out of range

# extract links from hashtag page
#links=[]
#source = browser.page_source
#data=bs(source, 'html.parser')
#body = data.find('body')
#script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
#page_json = script.text.split(' = ', 1)[1].rstrip(';')
#data = json.loads(page_json)
#for link in data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
#    links.append('https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/')

for link in data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
    links.append('https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/')
# try with ['display_url'] instead of ['shortcode'] if you don't get links

# info is stored in the dataframe result
result = pd.DataFrame()

for i in range(len(links)):
    try:
        page = urlopen(links[i]).read()
        data = bs(page, 'html.parser')
        body = data.find('body')
        script = body.find('script')
        raw = script.string.strip().replace('window._sharedData = ','').replace(';', '')
        json_data = json.loads(raw)
        posts = json_data['entry_data']['PostPage'][0]['graphql']
        posts = json.dumps(posts)
        posts = json.loads(posts)
        x = pd.DataFrame.from_dict(pd.json_normalize(posts), orient = 'columns')
        x.columns = x.columns.str.replace('shortcode_media.', "")
        print(x)
        result = result.append(x)
    except:
        np.nan

result = result.drop_duplicates(subset = 'shortcode')
result.index = range(len(result.index))

# check the variables stored
result.info()

result.index = range(len(result.index))
directory="./images/"

# store the username images and videos
if not os.path.exists(directory):
    os.makedirs(directory) # make directory using the target path if it doesn't exist already

for i in range(len(result)):
    r = requests.get(result['display_url'][i])
    with open(directory+result['shortcode'][i]+".jpg", 'wb') as f:
                    f.write(r.content)
