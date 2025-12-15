import json
import time
import spotipy
import pathlib
from spotipy.oauth2 import SpotifyOAuth

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from local_utils.logging import setup_logging, get_current_filename
from local_utils.loading import save_to_jsonl
from local_utils.spotify import extract_track_data

def main():

    current_filename = get_current_filename()
    setup_logging(current_filename)

    PLAYLIST_NAME = "25"
    PLAYLIST_ID = "0ovRUVQQv9ZL0jEhfokytE"

    FIELDS = "next, items(added_at, track(duration_ms, id, name, popularity, album(name, id, release_date), artists(name, id)))"
    FILEPATH = "../data/spotify/playlists/"
    FILENAME = PLAYLIST_NAME + "_" + PLAYLIST_ID # actual playlist name + its Spotify ID
    LIMIT = 50 

    batch_num = 1
    offset = 0

    with open("../secrets/data-retriever.json") as f:
        client_json = json.load(f)

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_json["client_id"],
            client_secret=client_json["client_secret"],
            redirect_uri="http://127.0.0.1:8000/callback",
            scope="playlist-read-private")
    )
    
    results = sp.playlist_items(
        playlist_id=PLAYLIST_ID,
        fields=FIELDS,
        limit=LIMIT,
        offset=offset,
    )

    extracted_data = extract_track_data(results)
    filename = f"{FILENAME}_{batch_num:02d}.jsonl"
    save_to_jsonl(extracted_data, FILEPATH + filename)
    
    while len(results["items"]) > 0: # or check if results["next"] is not None
        offset += LIMIT
        batch_num += 1

        results = sp.playlist_items(
            playlist_id=PLAYLIST_ID,
            fields=FIELDS,
            limit=LIMIT,
            offset=offset,
        )

        extracted_data = extract_track_data(results)
        filename = f"{FILENAME}_{batch_num:02d}.jsonl"
        save_to_jsonl(extracted_data, FILEPATH+filename)

        if results["next"] is None:
            break

        if ( batch_num % 5 ) == 0:
            time.sleep(5)
        else:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
