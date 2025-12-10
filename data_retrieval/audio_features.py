import psycopg2
import pandas as pd
import requests
import time
import json
from pathlib import Path
from typing import List, Dict
# Retrieval from PostgreSQL

HEADERS = {
  'Accept': 'application/json'
}
API_URL = "https://api.reccobeats.com/v1/audio-features"

def get_track_data(table_columns:List[str]) -> List[Dict]:

    # Idea: input argument is list of columns, but how can we change the string
    # input dynamically based on the size of the list?
    table_columns_str = ", ".join(table_columns)
    retrieval_query = f"SELECT {table_columns_str} FROM temp_saved_songs;"

    pgsql_conn = psycopg2.connect(
        database="music", user="music", password="music", host="localhost"
    )

    pgsql_cursor = pgsql_conn.cursor()
    pgsql_cursor.execute(retrieval_query)

    data_db = pgsql_cursor.fetchall()
    pgsql_cursor.close()

    data_records = []
    for row in data_db:
        record = {k: v for k, v in zip(table_columns, row)}
        data_records.append(record)

    return data_records

def get_audio_features(track_id_list:List) -> List[Dict]:
    payload = {"ids": track_id_list} 
    response = requests.get(API_URL, headers=HEADERS, params=payload)
    audio_features_records = response.json()["content"]

    for record in audio_features_records:
        spotify_track_id = record["href"].split("/")[-1]
        record["track_id"] = spotify_track_id
        record.pop("href")

    return audio_features_records

def dump_to_jsonl(data:List, full_filepath:str) -> None:

    with open(full_filepath, "w") as outfile:
        for record in data:
            json.dump(record, outfile)
            outfile.write("\n")
    # logging.info(f"{full_filepath} have been successfully saved.")

def main():
    table_columns = ["track_name", "main_artist", "track_id"]
    track_data = get_track_data(table_columns) 



    df_track = pd.DataFrame.from_records(track_data)
    track_ids = df_track["track_id"].to_list()

    audio_features_records = []
    for track_id in track_ids: # Q: Process 40 at a time...
        audio_features = get_audio_features(track_id)
        audio_features_records += audio_features
        time.sleep(2)

    # Create a reccobeats directory

    save_dir = "../data/reccobeats"
    dir_path = Path(save_dir)
    if not dir_path.exists():
        dir_path.mkdir()
    
    filename = "audio_features.jsonl"
    dump_to_jsonl(audio_features_records, save_dir+filename)

    # dump to jsonl files...


# Future problem: combining results from ReccoBeats to existing data. Solution:
# split on "/" and retrieve last part of "href".

if __name__ == "__main__":
    main()
