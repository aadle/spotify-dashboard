import psycopg2
import requests
import json
import time
import os
from pathlib import Path
from typing import List, Dict
import logging
import logging.config

HEADERS = {'Accept': 'application/json'}
API_URL = "https://api.reccobeats.com/v1/audio-features"

def setup_logging():
    config_file = Path("../logging_config/config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
        config["handlers"]["file"]["filename"] = f"logs/{os.path.basename(__file__)}.log"
    logging.config.dictConfig(config)

def dump_to_jsonl(data:List[Dict], full_filepath:str) -> None:
    with open(full_filepath, "w") as outfile:
        for record in data:
            json.dump(record, outfile)
            outfile.write("\n")
    logging.info(f"{full_filepath} have been successfully saved.")

def get_track_data(table_columns:List[str]) -> List[Dict]:
    table_columns_str = ", ".join(table_columns)
    retrieval_query = f"SELECT {table_columns_str} FROM temp_saved_songs ORDER BY added_at DESC;"

    pgsql_conn = psycopg2.connect(
        database="music", user="music", password="music", host="localhost"
    )
    pgsql_cursor = pgsql_conn.cursor()
    pgsql_cursor.execute(retrieval_query)
    data_db = pgsql_cursor.fetchall()
    pgsql_cursor.close()

    data_records = []
    for row in data_db:
        record = {key: val for key, val in zip(table_columns, row)}
        data_records.append(record)

    return data_records

def get_audio_features(track_id_list:List[str]) -> List[Dict] | None:
    payload = {"ids": track_id_list} 
    response = requests.get(API_URL, headers=HEADERS, params=payload)
    audio_features_records = response.json()["content"]

    if audio_features_records: # Check if response is populated
        tracks_found = len(audio_features_records)
        logging.info(
            f"Found audio features for {tracks_found} of {len(track_id_list)} tracks."
        )

        for record in audio_features_records:
            spotify_track_id = record["href"].split("/")[-1]
            record["track_id"] = spotify_track_id
            record.pop("href")

        return audio_features_records
    else:
        return None


def main():
    setup_logging()
    # Create a ReccoBeats folder 
    save_dir = "../data/reccobeats/"
    dir_path = Path(save_dir)
    if not dir_path.exists():
        dir_path.mkdir()

    table_columns = ["track_name", "main_artist", "track_id"]
    track_data = get_track_data(table_columns) # Retrieve data from Postgres

    track_data_dict = {track["track_id"]: track for track in track_data} # Better to do this outside the scope of the for-loop below?
    track_ids = list(track_data_dict.keys())

    start_track_idx = 0
    batch_size = 40
    for idx, track_idx in enumerate(
        range(start_track_idx, len(track_data), batch_size), 1
    ):
        filename = f"audio_features_{idx:03d}.jsonl"

        # Alt. 1
        # track_batch = track_data[track_idx:track_idx+batch_size]
        # query_track_ids = {track["track_id"]: track for track in track_batch}
        # audio_features = get_audio_features(list(query_track_ids.keys()))

        # if audio_features is not None:
        #     # Augmenting "main_artist" and "track_name" to the results
        #     for record in audio_features:
        #         track_id = record["track_id"]
        #         if record["track_id"] in query_track_ids:
        #             track = query_track_ids[track_id]
        #             record["main_artist"] = track["main_artist"]
        #             record["track_name"] = track["track_name"]
        #
        #     dump_to_jsonl(audio_features, save_dir+filename)
        # else:
        #     logging.warning("No audio features found for the batch of tracks.")

        # Alt. 2
        track_batch = track_ids[track_idx:track_idx+batch_size]
        audio_features = get_audio_features(track_batch)

        if audio_features is not None:
            # Augmenting "main_artist" and "track_name" to the results
            for record in audio_features:
                track_id = record["track_id"]
                track = track_data_dict[track_id]
                record["main_artist"] = track["main_artist"]
                record["track_name"] = track["track_name"]

            dump_to_jsonl(audio_features, save_dir+filename)
        else:
            logging.warning("No audio features found for the batch of tracks.")

        time.sleep(1)

if __name__ == "__main__":
    main()
