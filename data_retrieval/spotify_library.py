# Idea: 
# This script is to get the initial library as a whole. For the future, we can
# retrieve maybe 100 songs a month and call it quits as I rarely go over 50 songs, but
# just in case
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
import spotipy
import time 
import logging
from spotipy.oauth2 import SpotifyOAuth
from local_utils.logging import setup_logging, get_current_filename
from local_utils.loading import save_to_jsonl
from local_utils.spotify import extract_track_data 

def main():

    filename = get_current_filename()
    setup_logging(filename)

    with open("../secrets/data-retriever.json") as f:
        client_json = json.load(f)

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_json["client_id"],
            client_secret=client_json["client_secret"],
            redirect_uri="http://127.0.0.1:8000/callback",
            scope="user-library-read")
    )

    # Initial results
    offset = 0 # 94*50 # Last page of results in my library
    limit = 50

    batch_nr = 1
    results = sp.current_user_saved_tracks(offset=offset, limit=limit)

    extracted_data = extract_track_data(results)

    filepath = "../data/spotify/saved_songs_incl_artist_ids/"
    filename = f"spotify_library_batch_{batch_nr:03d}.jsonl"

    dir_path = pathlib.Path(filepath)
    if not dir_path.exists():
        dir_path.mkdir()

    save_to_jsonl(extracted_data, filepath+filename)

    while len(results["items"]) > 0:
        offset += 50 # Increment by the limit to get to next set of songs 
        batch_nr += 1 # Increment the batch

        results = sp.current_user_saved_tracks(offset=offset, limit=limit)

        # Check if returned .json has key "status".
        if "status" in results.keys():
            message = results["message"]
            status_code = results["status_code"]
            logging.critical(
                f"""
                Retrieval stopped due to API-error.
                Message{message}
                Status code: {status_code}.
                """
            )
            logging.critical(f"Restart the retrieval process with `offset={offset}`")
            break

        if len(results["items"]) == 0:
            logging.warning("No more songs to be saved. Quitting...")
            break

        # Use helper function to retrieve the data we wish to save
        extracted_data = extract_track_data(results)

        # Use helper function to save the data to a .json-file.
        filename = f"spotify_library_batch_{batch_nr:03d}.jsonl"
        save_to_jsonl(extracted_data, filepath+filename)

        if ( batch_nr % 5 ) == 0:
            logging.info("Sleeping to not spam the API.")
            time.sleep(5)
        else:
            time.sleep(0.5)

if __name__ == "__main__":
    main()

    

