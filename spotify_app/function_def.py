import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import pandas as pd
import os
from flask import session, url_for
from spotify_app import clientid, clientsecret, TOKEN_INFO

def get_liked_songs(sp):
    all_songs = []
    it=0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=it*50)['items']
        it += 1
        all_songs +=items
        if len(items)<50:
            break
    return all_songs

def create_dataframe(all_songs, sp, caller=0):
    """
    Create dataframe from liked songs that could be displayed to the flask application being created
    """
    track_names = []
    track_ids = []
    added = []
    release_dates = []
    track_artists = []
    track_popularity = []
    track_duration = []
    for i in range(len(all_songs)):
        track_name = all_songs[i]['track']['name']
        track_id = all_songs[i]['track']['id']
        if caller==0:
            added_at = all_songs[i]['added_at']
        else:
            added_at = all_songs[i]['played_at']
        release_date = all_songs[i]['track']['album']['release_date']
        artists = all_songs[i]['track']['album']['artists']
        artist_list = []
        for j in range(len(artists)):
            artist_list.append(artists[j]['name'])
        popularity = all_songs[i]['track']['popularity']
        duration = all_songs[i]['track']['duration_ms']
        track_names.append(track_name)
        track_ids.append(track_id)
        release_dates.append(release_date)
        track_artists.append(",".join(artist_list))
        track_popularity.append(popularity)
        track_duration.append(duration)
        added.append(added_at)
    track_danceability = []
    track_energy = []
    track_key = []
    track_loudness = []
    track_mode = []
    track_speechiness = []
    track_acousticness = []
    track_instrumentalness = []
    track_liveness = []
    track_valence = []
    track_tempo = []
    # print(sp.audio_features(track_ids[0]))

    for i in range(0, len(track_ids), 10):
        track_info = sp.audio_features(track_ids[i:min(i+10, len(track_ids))])
        track_danceability += [ti['danceability'] for ti in track_info]
        track_energy += [ti['energy'] for ti in track_info]
        track_key += [ti['key'] for ti in track_info]
        track_loudness += [ti['loudness'] for ti in track_info]
        track_mode += [ti['mode'] for ti in track_info]
        track_speechiness += [ti['speechiness'] for ti in track_info]
        track_acousticness += [ti['acousticness'] for ti in track_info]
        track_instrumentalness += [ti['instrumentalness'] for ti in track_info]
        track_liveness += [ti['liveness'] for ti in track_info]
        track_valence += [ti['valence'] for ti in track_info]
        track_tempo += [ti['tempo'] for ti in track_info]
    
    if caller==0:
        track_dict = {'Track_Name':track_names, 
                'Track_ID': track_ids,
                'Added_On':added,
                'Release_Date':release_dates,
                'Artists':track_artists,
                'Popularity':track_popularity,
                'Duration':track_duration,
                'Danceability':track_danceability,
                'Energy':track_energy,
                'Key':track_key,
                'Loudness':track_loudness,
                'Mode':track_mode,
                'Speechiness':track_speechiness,
                'Acousticness':track_acousticness,
                'Instrumentalness':track_instrumentalness,
                'Liveness':track_liveness,
                'Valence':track_valence,
                'Tempo':track_tempo
        }
    else:
        track_dict = {'Track_Name':track_names, 
                'Track_ID': track_ids,
                'Played_On':added,
                'Release_Date':release_dates,
                'Artists':track_artists,
                'Popularity':track_popularity,
                'Duration':track_duration,
                'Danceability':track_danceability,
                'Energy':track_energy,
                'Key':track_key,
                'Loudness':track_loudness,
                'Mode':track_mode,
                'Speechiness':track_speechiness,
                'Acousticness':track_acousticness,
                'Instrumentalness':track_instrumentalness,
                'Liveness':track_liveness,
                'Valence':track_valence,
                'Tempo':track_tempo
        }
    df = pd.DataFrame(track_dict)
    return df

def get_daily_played(sp):
    daily_played=[]
    recently_played = sp.current_user_recently_played(limit=50)
    print(recently_played['items'][0].keys())
    return recently_played['items']

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=clientid,
        client_secret=clientsecret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-read-private user-read-email user-modify-playback-state user-read-playback-position user-library-read streaming user-read-playback-state user-read-recently-played playlist-read-private"
    )