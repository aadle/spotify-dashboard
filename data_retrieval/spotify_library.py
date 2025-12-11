# Idea: 
# This script is to get the initial library as a whole. For the future, we can
# retrieve maybe 100 songs a month and call it quits as I rarely go over 50 songs, but
# just in case
import json
import spotipy
import time 
import logging.config
import logging
import pathlib
from spotipy.oauth2 import SpotifyOAuth
from typing import Dict, List

def setup_logging():
    config_file = pathlib.Path("../logging_config/config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)

# helper function to get out necessary data from the response
def helper_extract(data:Dict) -> List: # need better name
    # Extract out:
    # - ["track"]["id"] - Spotify ID for the track

    # - ["track"]["name"] - track name
    # - ["track"]["artists"]["name"] - DETTE ER EN LISTE!!!
        # - artist: [0] er hovedartist
            # if len() > 0
            # - features: [1:] indekser utover er features
            # else:
            # - features = [""]

    # - ["added_at"] - timestamp when track was added
    # - ["track"]["duration_ms"] - duration in ms

    # - ["track"]["album"]["name"] - Album name
    # - ["track"]["album"]["release_date"] - Release date of album
    # - ["track"]["album"]["id"] - Spotify ID for album
    # - 
    # - ["track"]["popularity"] - fluctuating popularity metric 

    items = data["items"]

    records_out = [] 

    for idx, item in enumerate(items):
        track_entry = {}
        track = item["track"]

        track_entry["track_id"] = track["id"]

        track_entry["track_name"] = track["name"]
        track_entry["main_artist"] = track["artists"][0]["name"]

        if len(track["artists"]) > 1:
            track_entry["featured_artists"] = [
                feature["name"] for feature in track["artists"][1:]
            ]
        else:
            track_entry["featured_artists"] = None

        track_entry["added_at"] = item["added_at"]
        track_entry["duration_ms"] = track["duration_ms"]

        track_entry["album_name"] = track["album"]["name"]
        track_entry["album_release_date"] = track["album"]["release_date"]
        track_entry["album_id"] = track["album"]["id"]

        records_out.append(track_entry)

    # return dict_out
    return records_out

def helper_save_to_file(data:List, full_filepath:str) -> None:
    with open(full_filepath, "w") as outfile:
        for record in data:
            json.dump(record, outfile)
            outfile.write("\n")
    logging.info(f"{full_filepath} have been successfully saved.")

def main():
    setup_logging()

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

    extracted_data = helper_extract(results)

    filepath = "../data/spotify/saved_songs/"
    filename = f"spotify_library_batch_{batch_nr:03d}.jsonl"

    helper_save_to_file(extracted_data, filepath+filename)

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
            logging.critical(f"Restart retrieval process with `offset={offset}`")
            break

        # Use helper function to retrieve the data we wish to save
        extracted_data = helper_extract(results)

        if len(results["items"]) == 0:
            logging.warning("No more songs to be saved. Quitting...")
            break

        # Use helper function to save the data to a .json-file.
        filename = f"spotify_library_batch_{batch_nr:03d}.jsonl"
        helper_save_to_file(extracted_data, filepath+filename)

        if ( batch_nr % 5 ) == 0:
            logging.info("Sleeping to not spam the API.")
            time.sleep(5)
        else:
            time.sleep(0.5)

if __name__ == "__main__":
    main()

    

