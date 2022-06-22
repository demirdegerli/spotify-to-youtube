# Spotify to YouTube
Convert your Spotify playlists into YouTube playlists.

## Get started
- Install the required packages
```
pip3 install -r requirements.txt
```
- Get Spotify credentials
    - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
    - If there is an app named `for Everything` use that's credentials.
    - If there is no app click `CREATE AN APP`.
    - Fill the form an click `CREATE`.
    - Use this app's credentials.
- Get your YouTube API credentials
    - Enable the YouTube API by clicking the `ENABLE` button at [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com).
    - Go to the [Google Cloud Platform Console](https://console.cloud.google.com/apis/credentials).
    - Create an `OAuth client ID` by clicking the `CREATE CREDENTIALS +` button.
    - Select the `Application type` to `Web application`.
    - Click `+ ADD URI` under the `Authorized redirect URIs` menu.
    - Type `http://localhost:8080/` to the opened textbox.
    - Fill the other form sections and click `CREATE`.
    - Download credentials by clicking `DOWNLOAD JSON`.
    - Rename the downloaded file to `client_secret.json` and move to the project directory.
