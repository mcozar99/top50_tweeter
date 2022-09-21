"""
This module extracts a playlist features given a name
"""
import time

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from keys import ID, ID_SECRET, redirect_uri, scope
from datetime import datetime
import requests

def update_top50():
    # Dataframe a actualizar y dataframe del dia anterior, con las entradas y las salidas
    df = pd.DataFrame(columns=['id', 'name', 'artists', 'days'])
    previous = pd.read_excel('data/top50.xlsx')
    entradas = pd.DataFrame(columns=['id', 'name', 'artists'])
    try:
        salidas = pd.read_excel('data/salidas.xlsx')
    except:
        salidas = pd.DataFrame(columns=['id', 'name', 'artists', 'days', 'date'])

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= ID, client_secret=ID_SECRET, redirect_uri=redirect_uri, scope= scope))
    #sacamos pl
    pl = sp.playlist('37i9dQZEVXbMDoHDwVN2tF')


    #parseamos el df
    tracks = pl['tracks']['items']
    i=0
    for track in tracks:
        track = track['track']
        id, name, artists = track['id'], track['name'], []
        for artist in track['artists']:
            artists.append(artist['name'])
        artists = ', '.join(artists)
        i+=1
        # actualizamos los dias y las entradas
        if id in previous.id.to_list():
            item = previous[previous.id == id]
            days = item.days.item() + 1
        else:
            days = 1
            entradas.loc[i, :] = [id, name, artists]
        df.loc[i, :] = [id, name, artists, days]

    # Actualizacion de salidas (les anadimos la fecha tb)
    for id in previous.id:
        if id not in df.id.to_list():
            # Sale por primera vez del top o no (se suman los dias)
            if id not in salidas.id.to_list():
                track = previous[previous.id == id]
                salidas.loc[len(salidas), :] = [track.id.item(), track.name.item(), track.artists.item(),
                                                track.days.item(), datetime.today().strftime('%Y-%m-%d')]
            else:
                track = previous[previous.id == id]
                salida = salidas[salidas.id == id]
                salidas.loc[salida.index, :] = [track.id.item(), track.name.item(), track.artists.item(),
                                                track.days.item() + salida.days.item(),
                                                datetime.today().strftime('%Y-%m-%d')]

    df.to_excel('data/top50.xlsx', index = False)
    entradas.to_excel('data/entradas.xlsx', index = False)
    salidas.to_excel('data/salidas.xlsx', index =False)
    previous.to_excel('data/day_before.xlsx', index = False)
    return df, entradas, salidas

def get_top_track_media():
    """
    Descarga la portada de la cancion top global
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= ID, client_secret=ID_SECRET, redirect_uri=redirect_uri, scope= scope))
    #sacamos pl
    pl = sp.playlist('37i9dQZEVXbMDoHDwVN2tF')
    url = pl['tracks']['items'][0]['track']['album']['images'][0]['url']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
    }
    req = requests.get(url, headers)
    f = open('downloads/top_track.png', 'wb')
    f.write(req.content)
    f.close()

def get_artist_media(artist, name):
    """Descarga la foto de un artista"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= ID, client_secret=ID_SECRET, redirect_uri=redirect_uri, scope= scope))
    #sacamos pl
    artist = sp.search(artist, limit=1, type='artist')
    url = artist['artists']['items'][0]['images'][0]['url']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
    }
    req = requests.get(url, headers)
    f = open('downloads/%s.png'%name, 'wb')
    f.write(req.content)
    f.close()

def get_track_media(track_name, name):
    """Descarga la foto de una cancion"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= ID, client_secret=ID_SECRET, redirect_uri=redirect_uri, scope= scope))
    track = sp.search(track_name, limit=1)
    url = track['tracks']['items'][0]['album']['images'][0]['url']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
    }
    req = requests.get(url, headers)
    f = open('downloads/%s.png'%name, 'wb')
    f.write(req.content)
    f.close()

def get_best_and_worse():
    """Saca la mayor subida y la mayor caida en el top"""
    previous = pd.read_excel('data/day_before.xlsx')
    current = pd.read_excel('data/top50.xlsx')
    max, min, max_id, min_id, max_position, min_position = 0, 0, 0, 0, 0, 0
    iterable = pd.concat([current, previous]).drop_duplicates('id')
    for id in iterable['id'].to_list():
        try:
            current_position = current[current.id == id].index[0]
        except:
            current_position = 50
        try:
            last_position = previous[previous.id == id].index[0]
        except:
            last_position = 50
        if current_position - last_position > min:
            min = current_position - last_position
            min_id = id
            min_position = current_position + 1 if current_position < 50 else "<50"
        if current_position - last_position < max:
            max = current_position - last_position
            max_id = id
            max_position = current_position + 1
    df = pd.DataFrame(columns=['name', 'artists', 'positions', 'rank'])
    df.loc[0, :] = [iterable[iterable.id == max_id].name.item(), iterable[iterable.id == max_id].artists.item(), -max, max_position]
    df.loc[1, :] = [iterable[iterable.id == min_id].name.item(), iterable[iterable.id == min_id].artists.item(), -min, min_position]
    return df
