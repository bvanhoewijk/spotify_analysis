#!/usr/bin/env python

#search for song
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import time
import json

class Genius:
    base_url = 'https://api.genius.com'

    def __init__(self, token):
        self.client_access_token = token
        self.headers = {'Authorization': 'Bearer {}'.format(client_access_token)}
        
        
    def search_song(self, artist, song):    
        request_uri = '/'.join([self.base_url, 'search/'])
        params = {'q': artist + " " +  song}
        
        r = requests.get(request_uri, params=params, headers=self.headers)
        hits = r.json()['response']['hits']

        return hits

    def retrieve_lyrics(self, song_url):
        '''Retrieves lyrics from genius website using the url'''

        page = requests.get(song_url)

        # Get the HTML:
        html = BeautifulSoup(page.text, "html.parser")

        # Parse HTML and grab the lyrics div:
        lyrics_div = html.find("div", class_="lyrics")
        if lyrics_div:
            song_text =  lyrics_div.get_text()
            # Remove newlines and sections like [Bridge]:
            text_lines = [line for line in song_text.split('\n') if not line.startswith("[")]
            return " ".join(text_lines).rstrip()
        return None


def genius_lyrics(client_access_token, song, artist):
    """Use the genius api to retrieve the song information"""
    g = Genius(client_access_token)
    hits = g.search_song(song=song, artist=artist)
    try:        
        url = hits[0]['result']['url']
        if hits[0]['result']['primary_artist']['name'].lower() != artist.lower():
            return None
    except:
        print ("No hits for %s - %s" % (song, artist))
        return None

    # Sometimes it crashes so try three times:
    song_text = g.retrieve_lyrics(url)
    if not song_text:
        time.sleep(0.5)
        song_text = g.retrieve_lyrics(url)
    if not song_text:
        time.sleep(0.5)
        song_text = g.retrieve_lyrics(url)
    
    return song_text

if __name__ == "__main__":
    client_access_token = ''
    
    with open("data_with_lyrics.json") as f:
        data_with_lyrics = json.load(f)

    
    for i in range(len(data_with_lyrics)):
        song = data_with_lyrics[i]['name']
        artist = data_with_lyrics[i]['artist']
        lyrics = data_with_lyrics[i]['lyrics']
        
        if len(lyrics) == 0:
            song_lyrics = genius_lyrics(client_access_token, song, artist)
            if song_lyrics:
                print("%s Found lyrics for %s - %s" % (i, song, artist))
                data_with_lyrics[i]['lyrics'] = song_lyrics
            else:
                print("%s Did not find lyrics for %s - %s" % (i, song, artist))
    
    with open('data_with_genius_lyrics.json', 'w') as fp:
        json.dump(data_with_lyrics, fp)



