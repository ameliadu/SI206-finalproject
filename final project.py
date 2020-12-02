import json
import sqlite3
import os
import requests
import billboard

def get_top10():
    top10 = []
    chart = billboard.ChartData('hot-100')
    songs = chart[0:10]
    for song in songs:
        title = song.title
        artist = song.artist
        top10.append((title, artist))
    return top10

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def database(data):
    cur, conn = setUpDatabase('top10.db')
    cur.execute('CREATE TABLE IF NOT EXISTS Top10 (rank INTEGER PRIMARY KEY, title TEXT, artist TEXT)')
    for song in data:
        cur.execute('INSERT INTO Top10 (title, artist) VALUES (?, ?)', (song[0], song[1]))
    conn.commit()

data = get_top10()
database(data)

# spotify API
def spotifysearch(playlist):
    url = 'https://api.spotify.com/v1/playlists'
    page = requests.get(url + playlist)
    return page.json()

