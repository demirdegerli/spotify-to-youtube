from spotipy import SpotifyClientCredentials, Spotify
import ytmusicapi
from http.server import BaseHTTPRequestHandler, HTTPServer
import validators
import os
from dotenv import load_dotenv
from time import sleep

if not os.path.exists("oauth.txt"):
    print("oauth.txt file is not found. Quitting...")
    quit()
with open("oauth.txt") as file:
    try:
        ytmusicapi.setup(filepath="oauth.json", headers_raw=file.read())
    except:
        print("The credentials in the oauth.txt file are missing or wrong. Please paste the YouTube credentials into the oauth.txt file correctly. Quitting...")
        quit()
load_dotenv()
if not os.getenv("SPOTIFY_CLIENT_ID") or not os.getenv("SPOTIFY_CLIENT_SECRET"):
    credentials_p = input("Spotify client ID or Spotify client secret are not found. Do you want to set them now? (yes/no) > ")
    if credentials_p == "yes":
        spotify_client_id = input("Spotify client ID: ")
        while not spotify_client_id:
            spotify_client_id = input("Spotify client ID: ")
        spotify_client_secret = input("Spotify client secret: ")
        while not spotify_client_secret:
            spotify_client_secret = input("Spotify client secret: ")
        env = open(".env", "w")
        env.write("""
SPOTIFY_CLIENT_ID="{}"
SPOTIFY_CLIENT_SECRET="{}"
""".format(spotify_client_id, spotify_client_secret))
        env.close()

        continue_prompt = input("Credentials are succesfully configured. Continue? (yes/no) > ")
        if continue_prompt == "yes":
            pass
        else:
            print("Quitting...")
            quit()
    else:
        print("Quitting...")
        quit()

load_dotenv()
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)
sp = Spotify(auth_manager=auth_manager)

def getFullName(item):
    try:
        def getAllArtists(artist):
            return artist['name']
        track = item['track']
        artists = ", ".join(list(map(getAllArtists, track['artists'])))
        return "{} - {}".format(artists, track['name'])
    except:
        return False

url = input("Spotify playlist URL: ")
while not validators.url(url):
    url = input("Spotify playlist URL: ")
playlist = False
while not playlist:
    try:
        playlist = sp.playlist(url, fields='name, description, tracks.total')
    except:
        url = input("Spotify playlist URL: ")

total = playlist['tracks']['total']
print("Playlist has {} items, fetching playlist items...".format(total))
items = []
offset = 0
while True:
    response = sp.playlist_items(url,
                                 offset=offset,
                                 fields='items(track.artists(name),track.name)',
                                 additional_types=['track'])

    if len(response['items']) == 0:
        break

    items += response['items']
    offset = offset + len(response['items'])
    print(offset, "/", total)

playlist_name = playlist['name']
playlist_description = playlist['description']

playlist_tracks = [name for name in list(map(getFullName, items)) if name]
print("{} items on your playlist are not songs, they will be excluded.".format(total-len(playlist_tracks)))
total = len(playlist_tracks)
print("Finding YouTube equalities of tracks...")

yt = ytmusicapi.YTMusic("oauth.json")
youtube_equalities = []
index = 1
not_found = []
for track in playlist_tracks:
    results = yt.search(track, filter='songs')
    if len(results) > 0:
        youtube_equalities.append(results[0]['videoId'])
        print("{}/{} Found: {}".format(index, total, track))
    else:
        not_found.append(track)
        print("{}/{} Not found: {}, skipping...".format(index, total, track))
    index += 1

print("\n{} YouTube equalities found. {} of them are not found. Creating YouTube playlist...".format(len(youtube_equalities), total-len(youtube_equalities)))
playlist_id = False
try:
    user_playlists = yt.get_library_playlists(None)
    for playlist in user_playlists:
        if playlist['title'] == playlist_name + " - Spotify":
            playlist_id = playlist['playlistId']
            break
    if not playlist_id:
        playlist_id = yt.create_playlist(playlist_name + " - Spotify", playlist_description)
except:
    print("Your YouTube credentials are expired or incorrect. Please replace the credentials in the oauth.txt. Quitting...")
    quit()

print("YouTube playlist created. Adding YouTube equalities...")

for track in yt.get_playlist(playlist_id, None)["tracks"]:
    if track["videoId"] in youtube_equalities:
        youtube_equalities.remove(track["videoId"])

yt.add_playlist_items(playlist_id, youtube_equalities, duplicates=True)

if len(not_found) > 0:
    print("\nNot found on YouTube:\n- {}".format("\n- ".join(not_found)))

print("\nYouTube playlist is ready. Playlist URL: https://music.youtube.com/playlist?list={}".format(playlist_id))
