'''
Created on Jul 13, 2021

@author: Private
'''

import os
import time
import slack
from dotenv import load_dotenv

import google_auth_oauthlib.flow
import googleapiclient.discovery

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

load_dotenv()
slack_token = os.environ.get("token")
client = slack.WebClient(token = slack_token)
client.conversations_open(users='U01EJSDGX50')

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "ytsecret.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

# Create array to track past ID's so don't repost in case video deleted
pastIds = []

client.chat_postMessage(channel='D02847J7DLL', text='Bot is now online!')

# Get ID initially, use try except to handle exceptions
try:
    request = youtube.activities().list(
        part="contentDetails",
        maxResults = 1,
        mine=True
    )
    response = request.execute()

    oldId = response['items'][0]['contentDetails']['upload']['videoId'] # gets the id from the json
    pastIds.append(oldId) # appends this old ID to the array to check. Important to note that there must be public videos already posted, otherwise this will fail.

except Exception as e: # sends failure message if necessary
    client.chat_postMessage(channel='D02847J7DLL', text='Failed in setting oldId. \n' + str(e))

while(True):
    time.sleep(60) #how often to send requests

    try:
        request = youtube.activities().list( #gets new ID
            part="contentDetails",
            maxResults = 1,
            mine=True
        )
        response = request.execute()

        newId = response['items'][0]['contentDetails']['upload']['videoId']

        if newId != oldId and not newId in pastIds: #if the new ID is diff from the old one, and the ID has not been posted before, notify of the new video
            client.chat_postMessage(channel='#admin', text='New vid has been posted! Video link: https://www.youtube.com/watch?v=' + str(newId))
            pastIds.append(newId) #adds id to the history
            oldId = newId #resets old ID for use later

        #print('Old ID: ' + str(oldId) + ' New ID: ' + str(newId))

    except Exception as e: #notifies if fail to set new id
        client.chat_postMessage(channel='D02847J7DLL', text='Failed in setting newId. \n' + str(e))