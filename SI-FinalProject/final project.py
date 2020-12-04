import json
import sqlite3
import os
import requests
import billboard
os.environ['SPOTIPY_CLIENT_ID']='ab463a3679544f58aa17e4f5bf167b94'
os.environ['SPOTIPY_CLIENT_SECRET']='a9c2cb89d03b4610a3682f758765ad95'
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def us_top25(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS UStop25 (rank INTEGER PRIMARY KEY, title TEXT, artist TEXT)')
    top25 = []
    chart = billboard.ChartData('hot-100')
    songs = chart[0:25]
    for song in songs:
        title = song.title
        artist = song.artist
        top25.append((title, artist))
    for song in top25:
        cur.execute('INSERT INTO UStop25 (title, artist) VALUES (?, ?)', (song[0], song[1]))
    conn.commit()

def country_top25(playlist_id, country, cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Countriestop25 (rank INTEGER PRIMARY KEY, title TEXT, artist TEXT, country TEXT)')
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    top25 = []
    response = sp.playlist_tracks(playlist_id, fields=None, limit=25, offset = 1, market=None)
    for track in response['items']:
        artist = track['track']['album']['artists'][0]['name']
        title = track['track']['album']['name']
        top25.append((title, artist))
    for song in top25:
        cur.execute('INSERT INTO Countriestop25 (title, artist, country) VALUES (?, ?, ?)', (song[0], song[1], country))
    conn.commit()

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


australia_top_25 = 'spotify:playlist:37i9dQZEVXbJPcfkRz0wJ0'
canada_top_25 = 'spotify:playlist:37i9dQZEVXbKj23U1GF4IR'
uk_top_25 = 'spotify:playlist:37i9dQZEVXbLnolsZ8PSNw'
cur, conn = setUpDatabase('top25.db')
us_top25(cur, conn)
country_top25(australia_top_25, 'Australia', cur, conn)
country_top25(canada_top_25, 'Canada', cur, conn)
country_top25(uk_top_25, 'UK', cur, conn)