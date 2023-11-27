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

specific_playlist = False
if input("If you want to add the songs to a specific YouTube playlist instead of creating a new one, enter the playlist ID. Only paste the PLAYLIST_ID in https://music.youtube.com/playlist?list=PLAYLIST_ID. If not, press enter without typing anything. > "):
    specific_playlist = True

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
print("Playlist has {} tracks, fetching playlist items...".format(total))
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
print("Finding YouTube equalities of tracks...")
playlistTracks = list(map(getFullName, items))

yt = ytmusicapi.YTMusic("oauth.json")
youtube_equalities = []
index = 1
not_found = []
for track in playlistTracks:
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
    if specific_playlist:
        playlist_id = specific_playlist
    else:
        playlist_id = yt.create_playlist(playlist_name + " - Spotify", playlist_description)
except:
    print("Your YouTube credentials are expired or incorrect. Please replace the credentials in the oauth.txt. Quitting...")
    quit()

print("YouTube playlist created. Adding YouTube equalities...")
index = 1
not_added = []
for video_id in youtube_equalities:
    try:
        yt.add_playlist_items(playlist_id, [video_id], duplicates=False)
        print("{}/{} Added song with the video ID: {}".format(index, len(youtube_equalities), video_id))
    except:
        print("{}/{} Can't add the song with the video ID: {}".format(index, len(youtube_equalities), video_id))
        not_added.append(video_id)
    index += 1
if len(not_added) > 0:
    names_and_ids = []
    for item in not_added:
        try:
            video_details = yt.get_song(item)['videoDetails']
            names_and_ids.append("{} - {} | {}".format(video_details['author'], video_details['name'], item))
        except:
            names_and_ids.append("[Can't get video info, YouTube has blocked this request] | {}".format(item))
    print("Names and video IDs of the songs that couldn't be added: (please keep in mind that duplicate songs are not added)\n- {}\n\nYou can try running this script after a while. Songs that are added before won't be added on the future runs.".format("\n- ".join(names_and_ids)))

print("\nYouTube playlist is ready. Playlist URL: https://music.youtube.com/playlist?list={}\nIf this link doesn't work please check your library and the playlist ID you entered if you entered the playlist ID manually.".format(playlist_id))
if len(not_found) > 0:
    print("\nNot found on YouTube:\n- {}".format(playlist_id, "\n- ".join(not_found)))
