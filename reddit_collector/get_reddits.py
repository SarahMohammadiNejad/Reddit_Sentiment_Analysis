"""
This script gets reddits titles from the reddit api 
and serve in the first step of the dockerized pipeline.
- add Mongodb connection with pymongo and insert reddits into Mongodb 
"""


import requests
import re
from requests.auth import HTTPBasicAuth
import sys
import pymongo
import logging
from datetime import datetime

headers = {
    'User-Agent': 'sarah_redit_app'
}


import os

# application user/pass
basic_auth = HTTPBasicAuth(
    username='client_id in token', #'client_id' in token
    password='secret in token' #'secret' in token
)
#reddit account user/pass
GRANT_INFORMATION = dict(
    grant_type="password",
    username='username in token', # REDDIT USERNAME ('username' in token)
    password='password in token' # REDDIT PASSWORD ('password' in token)
)


### POST REQUEST FOR ACCESS TOKEN
POST_URL = "https://www.reddit.com/api/v1/access_token"

access_post_response = requests.post(
    url=POST_URL,
    headers=headers,
    data=GRANT_INFORMATION,
    auth=basic_auth
).json()



# Print the Bearer Token sent by the API
# print(access_post_response)

### ADDING TO HEADERS THE Authorization KEY
headers['Authorization'] = access_post_response['token_type'] + ' ' + access_post_response['access_token']

## Send a get request to download most popular (hot) Python subreddits title using the new headers.
topic = 'climate'
URL = f"https://oauth.reddit.com/r/{topic}/hot"
params = {
    'limit': 100,                # Number of posts to retrieve
}
response = requests.get(
    url=URL,
    params=params,
    headers=headers
).json()

full_response = response['data']['children']


# establish connection to client
client = pymongo.MongoClient('my_mongo', port=27017)  # when within docker pipeline: replace 'localhost' with the name of the service

# define db 
db = client.my_db # 'my_db' is name of db

# empty the database
client.drop_database('my_db')

# define collection
dbcoll = db.my_collection # includes database and collection name


# Go through the full response and define a mongo_input dict
# filled with reddit title and corresponding id
for post in full_response:
    #_id = post['data']['id']
    title = post['data']['title']
    parts = title.split("|")



    # Extract the first part (before the first "|")
    title1 = parts[0].strip()  # Using strip() to remove leading and trailing whitespaces

    created_utc = post['data']['created_utc']

    # Convert Unix timestamp to human-readable date
    created_date = datetime.utcfromtimestamp(created_utc).strftime('%Y-%m-%d')# %H:%M:%S



    mongo_input = {'found_reddit' : {'reddit': title1[:60], 'date':created_date}}
    dbcoll.insert_one(mongo_input) # fake_doc is document




