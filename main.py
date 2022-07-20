from spotipy import SpotifyClientCredentials, Spotify
from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
import pytube
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import webbrowser
import validators
import json
import os
from dotenv import load_dotenv

load_dotenv()
if not os.path.exists("client_secret.json"):
    print("client_secret.json file not found. Quiting...")
    quit()
if not os.getenv("SPOTIFY_CLIENT_ID") or not os.getenv("SPOTIFY_CLIENT_SECRET"):
    spotify_credentials_p = input("Spotify client id and Spotify client secret not found. Do you want to set them now? (yes/no) > ")
    if spotify_credentials_p == "yes":
        spotify_client_id = input("Spotify client id: ")
        while not spotify_client_id:
            spotify_client_id = input("Spotify client id: ")
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
            print("Quiting...")
            quit()
    else:
        print("Quiting...")
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
        playlist = sp.playlist(url)
    except:
        url = input("Spotify playlist URL: ")

playlist_name = playlist['name']
playlist_description = playlist['description']
print("Playlist has {} tracks, finding YouTube equalities of tracks...".format(len(playlist['tracks']['items'])))
playlistTracks = list(map(getFullName, playlist['tracks']['items']))

youtube_equalities = []
for track in playlistTracks:
    search = pytube.Search(track)
    results = search.results
    if results[0]:
        video_id = results[0].vid_info['videoDetails']['videoId']
        if video_id:
            youtube_equalities.append(video_id)
    else:
        print("No YouTube equality found for {}, skipping...".format(track))
print("{} YouTube equalities found. Authorizing...".format(len(youtube_equalities)))


scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

client_secrets_file = "client_secret.json"
client_secrets_data = json.load(open(client_secrets_file))

# Get credentials and create an API client
flow = Flow.from_client_secrets_file(
    client_secrets_file,
    scopes,
    redirect_uri=client_secrets_data['web']['redirect_uris'][0]
)

# Automatically go to the authorization URL.
auth_url = flow.authorization_url(prompt='consent')
auth_url = auth_url[0]
webbrowser.open_new_tab(auth_url)

code = False
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global code
        query = urlparse.urlparse(self.path).query
        code = urlparse.parse_qs(query).get('code', None)
        if code:
            code = code[0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("You can close the tab.", "utf-8"))

webServer = HTTPServer(("localhost", 8080), MyServer)

while not code:
    webServer.handle_request()

# login with the code
flow.fetch_token(code=code)

print("Authorization successful. Creating YouTube playlist...")
# create youtube playlist
youtube = googleapiclient.discovery.build(
    "youtube",
    "v3",
    credentials=flow.credentials
)

request = youtube.playlists().insert(
    part="snippet,status",
    body={
      "snippet": {
        "title": playlist_name + " - Spotify",
        "description": playlist_description,
      },
      "status": {
        "privacyStatus": "private"
      }
    }
)

response = request.execute()
print("YouTube playlist created. Adding YouTube videos...")

playlist_id = response['id']

# add tracks to playlist
for video_id in youtube_equalities:
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
              "playlistId": playlist_id,
              "position": 0,
              "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
                }
              }
        }
    )

    request.execute()
print("YouTube playlist is ready. Playlist URL: https://www.youtube.com/playlist?list={}".format(playlist_id))
