import os, csv
import calendar
import random
import subprocess
from time import sleep
import pandas as pd
import requests

# Twitch API adatok (https://dev.twitch.tv/console)
CLIENT_ID = 'ipwaum956ahx10n9gwqm4wdupfndbp'
CLIENT_SECRET = 'v160qyi3ejzs0kbk8o5n2g6vmmxnuf'
ACCESS_TOKEN = 'seke8y95pnzz4sm3s4htzh0mtniryh' # App Access Token javasolt
CLIP_PER_PAGE = 100

g_AccessToken = None
g_Headers = None

def getBearerToken():
    auth_url = 'https://id.twitch.tv/oauth2/token'
    auth_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    headers = {
     "accept": "application/json"
    }
    auth_res = requests.post(auth_url, params=auth_params, headers=headers)
    access_token = auth_res.json()['access_token']
    return access_token

def getHeaders():
    return {
        "accept": "application/json",
        'Authorization': f'Bearer {getBearerToken()}',
        'Client-ID': CLIENT_ID
    }

def getUserIdByName(Username):
    user_res = requests.get(f'https://api.twitch.tv/helix/users?login={Username}', headers=getHeaders())
    user_id = user_res.json()['data'][0]['id']
    return user_id


def getClipsByRange(outPath, broadcasterId, startdate, enddate):
    paginator = ''

    with open(outPath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([ 'created_at', 'id', 'title', 'duration', 'view_count', 'creator_name'])
        while paginator is not None:
            clips_url = f'https://api.twitch.tv/helix/clips?broadcaster_id={broadcasterId}&started_at={startdate}&ended_at={enddate}&first={CLIP_PER_PAGE}{paginator}'
            clips_res = requests.get(clips_url, headers=g_Headers)
            clips_json = clips_res.json()
            clips_data = clips_json['data']
            if 'pagination' in clips_json and 'cursor' in clips_json['pagination']:
                paginator = f"&after={clips_json['pagination']['cursor']}"
                print(f"{len(clips_data)} => {clips_json['pagination']['cursor']}")
            else:
                paginator = None

            for clip in clips_data:
                writer.writerow([
                    clip.get('created_at', ''),
                    clip.get('id', ''),
                    clip.get('title', ''),
                    clip.get('duration', ''),
                    clip.get('view_count', ''),
                    clip.get('creator_name', '')
                ])

        sleep(1)  # Rate limit elkerülése érdekében

def scrapeClips():
    broadcasterId = '135615865' #getUserIdByName('')
    global g_AccessToken, g_Headers
    g_AccessToken = getBearerToken()
    g_Headers = getHeaders()

    for month in range(1, 13):
        outPath = f"clips/{month}.csv"
        startdate = f"2025-{month:02d}-01T00:00:00Z"
        dayInMonth = calendar.monthrange(2025, month)[1]
        enddate = f"2025-{month:02d}-{dayInMonth:02d}T23:59:00Z"

        getClipsByRange(outPath, broadcasterId, startdate, enddate)

def downloadClip(clip_url, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    subprocess.run(['npx', 'twitch-dlp', clip_url], cwd=directory, shell=True)

def DownloadClips():
    for month in range(11, 12):
        month = 1

        outPath = f"clips/{month}.csv"
        directory = f"clips/{month}"
        with open(outPath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                clip_id = row['id']
                clip_url = f"https://www.twitch.tv/alf0nsine/clip/{clip_id}"
                downloadClip(clip_url, directory)
                sleep(random.uniform(1, 5))

def mergeCSVs():
    pdc = pd.read_csv('clips/1.csv')
    for month in range(2, 13):
        pdc = pd.concat([pdc, pd.read_csv(f'clips/{month}.csv')], ignore_index=True)

    pdc = pdc.sort_values(by='created_at', ascending=False)
    pdc.to_csv('clips/allclips.csv', index=False)

def stats_top_creators():
    pdc = pd.read_csv('clips/allclips.csv')

    pdc['created_at'] = pd.to_datetime(pdc['created_at'])
    pdc['month'] = pdc['created_at'].dt.to_period('M')
    top_creators = pdc.groupby(['month', 'creator_name']).agg({
        'id': 'size',
        'duration': 'sum'
    }).reset_index()
    top_creators.columns = ['month', 'creator_name', 'clip_count', 'total_duration']
    top_creators = top_creators.sort_values(['month', 'clip_count'], ascending=[True, False])
    top_creators['total_duration'] = (top_creators['total_duration'].apply(lambda x: x/60).round(0).astype(str) + ' perc')
    top_creators = top_creators.groupby('month').head(1)
    print(top_creators.to_string(index=False))

if __name__ == "__main__":
    #scrapeClips()
    #DownloadClips()
    #mergeCSVs()
    stats_top_creators()