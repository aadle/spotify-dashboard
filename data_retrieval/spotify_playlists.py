import json
import time
import spotipy
import pathlib
import logging
import logging.config
import os
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict

def setup_logging():
    config_file = pathlib.Path("../logging_config/config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
        config["handlers"]["file"]["filename"] = f"logs/{os.path.basename(__file__)}.log"
    logging.config.dictConfig(config)

def helper_save_to_file(data:List, full_filepath:str) -> None:
    with open(full_filepath, "w") as outfile:
        for record in data:
            json.dump(record, outfile)
            outfile.write("\n")
    logging.info(f"Saved {full_filepath}.")


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

    return records_out


def main():

    setup_logging()

    PLAYLIST_NAME = "25"
    PLAYLIST_ID = "0ovRUVQQv9ZL0jEhfokytE"

    FIELDS = "next, items(added_at, track(duration_ms, id, name, popularity, album(name, id, release_date), artists.name))"
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

    extracted_data = helper_extract(results)
    filename = f"{FILENAME}_{batch_num:02d}.jsonl"
    helper_save_to_file(
        extracted_data,
        FILEPATH+filename
    )
    
    while len(results["items"]) > 0: # or check if results["next"] is not None
        offset += LIMIT
        batch_num += 1

        results = sp.playlist_items(
            playlist_id=PLAYLIST_ID,
            fields=FIELDS,
            limit=LIMIT,
            offset=offset,
        )

        extracted_data = helper_extract(results)
        filename = f"{FILENAME}_{batch_num:02d}.jsonl"
        helper_save_to_file(extracted_data, FILEPATH+filename)

        if results["next"] is None:
            break

        if ( batch_num % 5 ) == 0:
            time.sleep(5)
        else:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
