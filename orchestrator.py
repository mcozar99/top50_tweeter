import pandas as pd
from tweeter import *
from playlist_builder import *
from datetime import datetime
from collections import Counter

def flatten(t):
  return [item for sublist in t for item in sublist]

# Variables para despues
today = datetime.today().strftime('%Y-%m-%d')
url = 'https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF'
api = login()

# Actualizacion de la playlist
top, entradas, salidas =  update_top50()
get_top_track_media()

#entradas = pd.read_excel('data/entradas.xlsx')
#salidas = pd.read_excel('data/salidas.xlsx')
#top = pd.read_excel('data/top50.xlsx')

top = top.reset_index(drop=True)
entradas = entradas.reset_index(drop=True)
salidas = salidas.reset_index(drop=True)

## PRIMER TWEET
text = "\N{fire}\N{fire} #Spotify #Top50Global UPDATE (%s)\N{fire}\N{fire}\n\n"%today
emojis = ["\N{first place medal}", "\N{second place medal}", "\N{third place medal}", "4️⃣", "5️⃣"]
for i in range(0, 5):
    text = text + emojis[i] + ': ' + top.loc[i, 'name'] + ' (' + top.loc[i, 'artists'] + ')\n'

tweet = tweet_something(text, api, media=['downloads/top_track.png'])

# SEGUNDO TWEET CON LAS CAIDAS DEL TOP
text = "🔴🔴 DROPPED FROM TOP 🔴🔴\n\n"
salidas = salidas[salidas.date == today].reset_index(drop = True)
if len(salidas) != 0:
    for i in range(0, len(salidas)):
        text = text + "🔴 %s (%s) \n"%(salidas.loc[i, 'name'], salidas.loc[i, 'artists'])
    get_track_media(salidas.loc[0, 'name'], 'salidas')
    tweet = thread(tweet, text, api, media=['downloads/salidas.png'])
else:
    text = "🔴🔴 NO DROPS FROM TOP 🔴🔴"
    tweet = thread(tweet, text, api)

# TERCER TWEET CON LAS NUEVAS ENTRADAS
text = "🟢🟢 NEW APPEARANCES 🟢🟢\n\n"
if len(entradas) != 0:
    for i in range(0, len(entradas)):
        text = text + "🟢 %s (%s) \n"%(entradas.loc[i, 'name'], entradas.loc[i, 'artists'])
    get_track_media(entradas.loc[0, 'name'], 'entradas')
    tweet = thread(tweet, text, api, media=['downloads/entradas.png'])
else:
    text = "🟢🟢 NO NEW APPEARANCES 🟢🟢"
    tweet = thread(tweet, text, api)

# TRACK ON FIRE AND TRACK FALLING
tracks = get_best_and_worse()
text = "🚀🚀 Track on fire 🚀🚀\n🚀\n🚀"
text = text + " %s (%s), +%s positions), rank %s"%(tracks.loc[0, 'name'], tracks.loc[0, 'artists'], str(tracks.loc[0, 'positions']), str(tracks.loc[0, 'rank']))
text = text + "\n\n⏬⏬ Track Falling ⏬⏬\n⏬\n⏬"
text = text + " %s (%s), %s positions, rank %s"%(tracks.loc[1, 'name'], tracks.loc[1, 'artists'], str(tracks.loc[1, 'positions']), str(tracks.loc[1, 'rank']))

get_track_media(tracks.loc[0, 'name'], 'onfire')
get_track_media(tracks.loc[1, 'name'], 'falling')
tweet = thread(tweet, text, api, media=['downloads/onfire.png', 'downloads/falling.png'])

# ULTIMO TWEET CON EL RANKING DE ARTISTAS
artists = Counter(flatten(top['artists'].apply(lambda x: x.split(', ')).to_list())).most_common(5)
text = "\N{fire}\N{fire} ARTISTS OF THE MOMENT \N{fire}\N{fire}\n\n"
for i in range(0, 5):
    if i < 3:
        get_artist_media(artists[i][0], 'top_artist%s'%str(i+1))
    text = text + emojis[i] + ': #' + ''.join(artists[i][0])\
           + ' (' + str(artists[i][1]) + ' songs on Top)\n'

tweet = thread(tweet, text, api, media=['downloads/top_artist1.png', 'downloads/top_artist2.png', 'downloads/top_artist3.png'])