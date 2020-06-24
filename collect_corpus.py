import sys
import spotipy
import spotipy.util as util
from pprint import pprint
import json
import requests
import time
import pickle
import pandas as pd

username = "burnedthumb"
scope = "user-library-read"


def get_lyrics(trackname, artist):
    """Retrieve and parse the lyrics"""
    lyrics = ""
    try:
        response = requests.get("https://api.lyrics.ovh/v1/" + artist + "/" + trackname)
        if response.status_code == 200:
            data = response.json()
            lyrics = parse_lyrics(data["lyrics"])
        time.sleep(0.25)
    except:
        print("Can't get lyrics for %s - %s" % (artist, trackname))
    return lyrics


def parse_lyrics(lyrics):
    """Parse the lyrics"""
    # TODO remove invalid characters and garbage
    try:
        lines = lyrics.split("\n")
    except:
        pass

    result = []
    for line in lines:
        line = line.rstrip()
        words = line.split(" ")

        for word in words:
            if word == "":
                continue
            result.append(word)
    return " ".join(result)


def artist_genre(sp, artist_id):
    try:
        artistinfo = sp.artist(artist_id)
        return ",".join(artistinfo['genres'])
    except:
        return None

def track_info_and_lyrics():
    token = util.prompt_for_user_token(username, scope)
    limit_per_query = 50
    if token:
        sp = spotipy.Spotify(auth=token)
        corpus = list()

        try:
            for i in range(0, 2000, limit_per_query):
                print("%s%%" % round((i / 2000.0) * 100, 1), end="\r")
                results = sp.current_user_saved_tracks(limit=limit_per_query, offset=i)
                for item in results["items"]:
                    track = item["track"]

                    lyrics = get_lyrics(track["name"], track["artists"][0]["name"])
                    audio_features = sp.audio_features(track["uri"])
                    track_info = {
                        "added_at": item["added_at"],
                        "name": track["name"],
                        "artist": track["artists"][0]["name"],
                        "artist_id": track["artists"][0]["id"],
                        'genres': artist_genre(sp,track["artists"][0]["id"]),
                        "uri": track["uri"],
                        "lyrics": lyrics,
                        "audio_features": audio_features,
                    }
                    corpus.append(track_info)
            print("100%% done")
        except ValueError as err:
            print("Someting with wrong", err)
        finally:
            # If it horribly dies save the data to disk:
            with open("data_with_lyrics.json", "w") as outfile:
                json.dump(corpus, outfile)

    else:
        print("Can't get token for", username)

if __name__ == "__main__":
    track_info_and_lyrics()
