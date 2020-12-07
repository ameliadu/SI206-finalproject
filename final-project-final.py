import json
import sqlite3
import os
import requests
import billboard
import matplotlib.pyplot as plt
import numpy as np
os.environ['SPOTIPY_CLIENT_ID']='ab463a3679544f58aa17e4f5bf167b94'
os.environ['SPOTIPY_CLIENT_SECRET']='e89458c8bda14001a50cfe0208d95852'
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# create UStop100 table from BillBoard chart
def us_top100(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS UStop100 (rank INTEGER PRIMARY KEY, title TEXT, artist TEXT)')
    bbtop100 = []
    # pull from Billboard API
    chart = billboard.ChartData('hot-100')
    for song in chart:
        title = song.title
        artist = song.artist
        bbtop100.append((title.lower(), artist))
    for song in bbtop100:
        cur.execute('INSERT INTO UStop100 (title, artist) VALUES (?, ?)', (song[0], song[1]))
    conn.commit()

# create top25 table for given country from Spotify charts
def country_top25(bbtop100, playlist_id, country, cur, conn):
    table_name = country + 'top25'
    table_str = 'CREATE TABLE IF NOT EXISTS ' + table_name + ' (country_rank INTEGER PRIMARY KEY, us_rank TEXT, title TEXT)'
    cur.execute(table_str)
    # pull from Spotify API
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    ranks = []
    response = sp.playlist_tracks(playlist_id, fields=None, limit=25, offset = 1, market=None)
    for track in response['items']:
        # formatting title to match with titles in UStop100
        title1 = track['track']['name'].split('(')[0].strip()
        title = title1.lower()
        # create us_rank column as a key to refer back to UStop100 table, N/A if song not on UStop100
        if title not in bbtop100:
            us_rank = 'N/A'
        else:
            cur.execute('SELECT rank FROM UStop100 WHERE title = ?', (title, ))
            us_rank = cur.fetchone()
            us_rank = us_rank[0]
        ranks.append((us_rank, title))
    for rank in ranks:
        insert_str = 'INSERT INTO ' + table_name + ' (us_rank, title) VALUES (?, ?)'
        cur.execute(insert_str, (rank[0], rank[1]))
    conn.commit()

# initiallize a database function and define curr and conn
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# create global variable list for UStop100 with just titles
bbtop100 = []
chart = billboard.ChartData('hot-100')
for song in chart:
    title = song.title
    bbtop100.append(title.lower())

# country charts Spotify IDs
australia_top_25 = 'spotify:playlist:37i9dQZEVXbJPcfkRz0wJ0'
canada_top_25 = 'spotify:playlist:37i9dQZEVXbKj23U1GF4IR'
uk_top_25 = 'spotify:playlist:37i9dQZEVXbLnolsZ8PSNw'
ireland_top_25 = 'spotify:playlist:37i9dQZEVXbKM896FDX8L1'

# create tables in database for each country's charts
cur, conn = setUpDatabase('MusicCharts.db')
us_top100(cur, conn)
country_top25(bbtop100, australia_top_25, 'Australia', cur, conn)
country_top25(bbtop100, canada_top_25, 'Canada', cur, conn)
country_top25(bbtop100, uk_top_25, 'UK', cur, conn)
country_top25(bbtop100, ireland_top_25, 'Ireland', cur, conn)

# create lists of matching songs in each country's charts and the US chart
cur.execute('SELECT UStop100.title, Australiatop25.country_rank from UStop100 JOIN Australiatop25 ON UStop100.rank = Australiatop25.us_rank')
australia_song_matches = cur.fetchall()

cur.execute('SELECT UStop100.title, Canadatop25.country_rank from UStop100 JOIN Canadatop25 ON UStop100.rank = Canadatop25.us_rank')
canada_song_matches = cur.fetchall()

cur.execute('SELECT UStop100.title, UKtop25.country_rank from UStop100 JOIN UKtop25 ON UStop100.rank = UKtop25.us_rank')
uk_song_matches = cur.fetchall()

cur.execute('SELECT UStop100.title, Irelandtop25.country_rank from UStop100 JOIN Irelandtop25 ON UStop100.rank = Irelandtop25.us_rank')
ireland_song_matches = cur.fetchall()

# list of tuples with song match and country ranking for all of the countries
all_countries = australia_song_matches + canada_song_matches + uk_song_matches + ireland_song_matches

song_list = []
x_axis = []
us_list = []
australia = []
canada = []
ireland = []
uk = []

# create list of all matching song titles
for item in all_countries:
    title = item[0]
    song_list.append(title)
# go through list of song titles and find titles that appear 2 or more times
for song in song_list:
    if song_list.count(song) >= 2 and song not in x_axis:
        x_axis.append(song)

# go through popular song titles and create points for the song title's rank in each country
# rank = 0 if song not in country's chart
for song in x_axis:
    cur.execute('SELECT rank FROM UStop100 WHERE title = ?', (song, ))
    us_list.append(int(cur.fetchone()[0]))

    a_rank = 0
    for item in australia_song_matches:
        if item[0] == song:
            a_rank = item[1]
    australia.append(a_rank)

    c_rank = 0
    for item in canada_song_matches:
        if item[0] == song:
            c_rank = item[1]
    canada.append(c_rank)

    i_rank = 0
    for item in ireland_song_matches:
        if item[0] == song:
            i_rank = item[1]
    ireland.append(i_rank)

    u_rank = 0
    for item in uk_song_matches:
        if item[0] == song:
            u_rank = item[1]
    uk.append(u_rank)

print(us_list)
print(australia)
print(canada)
print(uk)
print(ireland)

print(x_axis)

fig, ax1 = plt.subplots()
n = len(x_axis)
width = 0.1
ind = np.arange(n)

# create bar for each country
p1 = ax1.bar(ind, us_list, width, color='blue')
p2 = ax1.bar(ind + width, australia, width, color='red')
p3 = ax1.bar(ind + 2*width, canada, width, color='green')
p4 = ax1.bar(ind + 3*width, ireland, width, color='yellow')
p5 = ax1.bar(ind + 4*width, uk, width, color='black')

ax1.set_xticks(ind + width / 5)
ax1.set_xticklabels(x_axis)
plt.xticks(rotation=90)
ax1.legend((p1[0],p2[0],p3[0],p4[0],p5[0]), ('US', 'Australia', 'Canada', 'Ireland', 'UK'))
ax1.set(xlabel='song title', ylabel='song rank',
       title='Popular Song Ranks in English Speaking Countries')
ax1.autoscale_view()

ax1.grid()

# pull whether each song on the matching songs for 2 more more countries is explicit or not from Spotify's API
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)
ex_count = 0
'''
for song in x_axis[0:11]:
    response = sp.playlist_tracks(australia_top_25, fields=None, limit=25, offset = 1, market=None)
    for track in response['items']:
        title1 = track['track']['name'].split('(')[0].strip()
        title = title1.lower()
        # counts if a song is explicit and adds it to an explicit counter
        if song == title:
            ex = track['track']['explicit']
            if ex == True:
                ex_count += 1
'''

# pull remaining songs that aren't available on Australia's top 25 
for song in x_axis:
    response = sp.playlist_tracks(canada_top_25, fields=None, limit=25, offset = 1, market=None)
    for track in response['items']:
        title1 = track['track']['name'].split('(')[0].strip()
        title = title1.lower()
        if song == title:
            ex = track['track']['explicit']
            if ex == True:
                ex_count += 1

fig2 = plt.figure(2)
labels = 'Explicit', 'Clean'
ex_size = (ex_count/15)*100
clean_size = ((15-ex_count)/15)*100
sizes = [ex_size, clean_size]
explode = (0.1, 0)
colors = ['red', 'green']
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')

plt.show()