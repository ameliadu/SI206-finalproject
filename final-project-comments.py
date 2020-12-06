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

# create global list for the billboard hot 100
bbtop25 = []
chart = billboard.ChartData('hot-100')
for song in chart:
    title = song.title
    bbtop25.append(title.lower())

#create function for billboard hot 100, creates table through SQlite
def us_top25(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS UStop100 (rank INTEGER PRIMARY KEY, title TEXT, artist TEXT)')
    top25 = []
    chart = billboard.ChartData('hot-100')
    #loops through sonds on chart to create a list of lowercase titles
    for song in chart:
        title = song.title
        artist = song.artist
        top25.append((title.lower(), artist))
    for song in top25:
        cur.execute('INSERT INTO UStop100 (title, artist) VALUES (?, ?)', (song[0], song[1]))
    conn.commit()

#create a function that creates a table for each given input country and their songs through spotify's international top 50 playlist
def country_top25(bbtop25, playlist_id, country, cur, conn):
    table_name = country + 'top25'
    table_str = 'CREATE TABLE IF NOT EXISTS ' + table_name + ' (country_rank INTEGER PRIMARY KEY, us_rank TEXT, title TEXT)'
    cur.execute(table_str)
    #pulls from given API
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    ranks = []
    response = sp.playlist_tracks(playlist_id, fields=None, limit=25, offset = 1, market=None)
    #loops through API playist songs to index through the nested dictionary to get the sing title and it;s ranking
    for track in response['items']:
        title1 = track['track']['name'].split('(')[0].strip()
        title = title1.lower()
        #checks if the song is also in the billboard hot 100 and  puts its rank on the chart, if not it puts N/A
        if title not in bbtop25:
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

#initiallizes a database function and defines curr and conn
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#refrences the spotify playlist's URI's for each internation country and gives their refrence link
australia_top_25 = 'spotify:playlist:37i9dQZEVXbJPcfkRz0wJ0'
canada_top_25 = 'spotify:playlist:37i9dQZEVXbKj23U1GF4IR'
uk_top_25 = 'spotify:playlist:37i9dQZEVXbLnolsZ8PSNw'
ireland_top_25 = 'spotify:playlist:37i9dQZEVXbKM896FDX8L1'
cur, conn = setUpDatabase('top25.db')
#set up database for each country given their playlist URI
us_top25(cur, conn)
country_top25(bbtop25, australia_top_25, 'Australia', cur, conn)
country_top25(bbtop25, canada_top_25, 'Canada', cur, conn)
country_top25(bbtop25, uk_top_25, 'UK', cur, conn)
country_top25(bbtop25, ireland_top_25, 'Ireland', cur, conn)

#Joins each countries data base by the us song rank which is the billboard hot 100, does not return the ones with N/A
australia_song_matches1 = cur.execute('SELECT UStop100.title, Australiatop25.country_rank from UStop100 JOIN Australiatop25 ON UStop100.rank = Australiatop25.us_rank')
australia_song_matches = australia_song_matches1.fetchall()

canada_song_matches1 = cur.execute('SELECT UStop100.title, Canadatop25.country_rank from UStop100 JOIN Canadatop25 ON UStop100.rank = Canadatop25.us_rank')
canada_song_matches = canada_song_matches1.fetchall()

uk_song_matches1 = cur.execute('SELECT UStop100.title, UKtop25.country_rank from UStop100 JOIN UKtop25 ON UStop100.rank = UKtop25.us_rank')
uk_song_matches = uk_song_matches1.fetchall()

ireland_song_matches1 = cur.execute('SELECT UStop100.title, Irelandtop25.country_rank from UStop100 JOIN Irelandtop25 ON UStop100.rank = Irelandtop25.us_rank')
ireland_song_matches = ireland_song_matches1.fetchall()

#creates a list of tuples of all the song titles and ranks in each country
all_countries = australia_song_matches + canada_song_matches + uk_song_matches + ireland_song_matches
song_list = []
x_axis = []
us_list = []
australia = []
canada = []
ireland = []
uk = []

#goes through the list tuples and appends the song titles to a song list
for item in all_countries:
    title = item[0]
    song_list.append(title)
#goes through the song list and appends the songs that appear 2 or more times to the x axis list
for song in song_list:
    if song_list.count(song) >= 2 and song not in x_axis:
        x_axis.append(song)

#loops through x axis list and selects the rank for each country of that song
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

#initializes the bar graph we are using
def CreateBarGraph():
    fig, ax = plt.subplots()
    n = 15
    width = 0.1
    ind = np.arange(n)

#sets up the plots for each countrie's bar
    p1 = ax.bar(ind, us_list, width, color='blue')
    p2 = ax.bar(ind + width, australia, width, color='red')
    p3 = ax.bar(ind + 2*width, canada, width, color='green')
    p4 = ax.bar(ind + 3*width, ireland, width, color='yellow')
    p5 = ax.bar(ind + 4*width, uk, width, color='black')

#defines and set up the axes
    ax.set_xticks(ind + width / 5)
    ax.set_xticklabels(x_axis)
    plt.xticks(rotation=90)
    ax.legend((p1[0],p2[0],p3[0],p4[0],p5[0]), ('US', 'Australia', 'Canada', 'Ireland', 'UK'))
    ax.autoscale_view()

#show plot
    ax.grid()
    plt.show()

#pulls whether each song on the matching songs for 2 more more countries is explicit or not from spotify's API
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)
ex_count = 0
for song in x_axis[0:11]:
    response = sp.playlist_tracks(australia_top_25, fields=None, limit=25, offset = 1, market=None)
    for track in response['items']:
        title1 = track['track']['name'].split('(')[0].strip()
        title = title1.lower()
#counts whether or not a song is explicit and adds it to an explicit counter
        if song == title:
            ex = track['track']['explicit']
            if ex == True:
                ex_count += 1

#pulls the remaining songs that aren't available on australia's top 25 
for song in x_axis[11:]:
    response = sp.playlist_tracks(canada_top_25, fields=None, limit=25, offset = 1, market=None)
    for track in response['items']:
        title1 = track['track']['name'].split('(')[0].strip()
        title = title1.lower()
        if song == title:
            ex = track['track']['explicit']
            if ex == True:
                ex_count += 1

def CreatePieChart():
#initializes axes
    fig2, ax` = plt.subplots()
#defines labels and pie chart's ratios of explicit songs
    labels = 'Explicit', 'Clean'
    ex_size = (ex_count/15)*100
    clean_size = ((15-ex_count)/15)*100
    sizes = [ex_size, clean_size]
    explode = (0.1, 0)
    colors = ['red', 'green']

#sets up pie chart and shows it
    ax1.pie(sizes, explode=explode, label=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')
    plt.show()

CreateBarGraph()
CreatePieChart()