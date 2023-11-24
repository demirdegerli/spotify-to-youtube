# Spotify to YouTube
Convert your Spotify playlists into YouTube playlists.

## Get started
- Install the required packages
```
pip3 install -r requirements.txt
```
- Get Spotify credentials
    - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
    - If there is an app named `for Everything` use it's credentials.
    - If there is no app click `CREATE AN APP`.
    - Type `http://localhost:8080/` to the 'Redirect URI` textbox.
    - Select `Web API` in the `Which API/SDKs are you planning to use?` section.
    - Fill the other sections if you want and click `CREATE`.
    - Click `Settings`, copy `Client ID` and `Client Secret`.
    - You'll use these credentials once you run the script. So keep them in your clipboard or save them.
- Get YouTube credentials
    - Open a new tab
    - Open the developer tools (Ctrl-Shift-I) and select the “Network” tab
    - Go to https://music.youtube.com and ensure you are logged in
    - Find an authenticated POST request. The simplest way is to filter by /browse using the search bar of the developer tools. If you don’t see the request, try scrolling down a bit or clicking on the library button in the top bar.
    - If you're using Firefox (easiest way)
        - Verify that the request looks like this: Status 200, Method POST, Domain music.youtube.com, File browse?...
        - Copy the request headers (right click > copy > copy request headers)
    - If you're using a Chromium based browser like Chrome, Edge etc.
        - Verify that the request looks like this: Status 200, Name browse?...
        - Click on the Name of any matching request. In the “Headers” tab, scroll to the section “Request headers” and copy everything starting from “accept: */*” to the end of the section
    - Create a file called `oauth.txt` in the project directory. Paste the credentials that you copied. Close the file.

## Run
```
python3 main.py
```
