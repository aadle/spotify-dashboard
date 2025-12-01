# Retrieve data in a user set specific period, and dump it into .json-files.

# TODO:
# - [ ] Replace dumping logic with function call instead.

import json
import requests
import time
from pytz import utc
from datetime import datetime
from typing import Dict

with open("../secrets/lastfm.json") as f:
    api_credentials = json.load(f) 

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
NUM_REQUESTS = 50
USER = "GammelPerson"

date_format = "%Y-%m-%d"

request_parameters = {
    "limit": NUM_REQUESTS,
    "user": "GammelPerson",
    "from": None,
    "to": None,
    "extended": 0,
    "api_key": api_credentials["client_id"],
    "format": "json",
    "method": "user.getrecenttracks",
    "page": 1
    }


# A function which finds the number of pages to process for a request?
def request_helper(start:str, end:str, num_requests:int=NUM_REQUESTS):
    start_unix_seconds = int(
        utc.localize(datetime.strptime(start, date_format)).timestamp()
    )
    end_unix_seconds = int(
        utc.localize(datetime.strptime(end, date_format)).timestamp()
    )

    # Move out of function, set "from" and "to" as None and overwrite in
    # function? E.g.
        # request_parameters["from"] = start
        # request_parameters["to"] = end 

    request_parameters = {
        "limit":num_requests,
        "user": "GammelPerson",
        "from": start_unix_seconds,
        "to": end_unix_seconds,
        "extended": 0,
        "api_key": api_credentials["client_id"],
        "format": "json",
        "method": "user.getrecenttracks"
    }

    response = requests.get(url=BASE_URL, params=request_parameters)

    if response.status_code != 200:
        print(f"Failed. Actual response code: {response.status_code}.")
        return None, None
    else:
        attributes = response.json()["recenttracks"]["@attr"]
        print(attributes)
        num_pages = int(attributes["totalPages"])
        return num_pages, response.json()

def dump_response_to_json(response:Dict, full_save_path:str):
    out_file = {}
    out_file["tracks"] = []
    tracks = response["recenttracks"]["track"]
    for i, track in enumerate(tracks, 1):
        track_info = {
                "artist_name": track["artist"]["#text"],
                "artist_mbid": track["artist"]["mbid"],
                "album_name": track["album"]["#text"],
                "album_mbid": track["album"]["mbid"],
                "track_name": track["name"],
                "track_mbid": track["mbid"],
                "date_played_unix": int(track["date"]["uts"])
            }
        out_file["tracks"].append(track_info)
    
    with open(full_save_path, "w") as outfile:
        json.dump(out_file, outfile, indent=4)

# A function to actually handle the data
def retrieve_listening_data(start:str, end:str, num_requests:int=NUM_REQUESTS):
    # Qs:
    # - Best way to parse in a date as input? E.g. "2025-01-12"

    file_path = "../data/last_fm_listening_history/"

    start_unix_seconds = int(
        utc.localize(datetime.strptime(start, date_format)).timestamp()
    )
    end_unix_seconds = int(
        utc.localize(datetime.strptime(end, date_format)).timestamp()
    )

    request_parameters["start"] = start_unix_seconds
    request_parameters["end"] = end_unix_seconds

    number_of_pages, response = request_helper(start, end, num_requests) # Redundant because we call the API two times at this point for the same results
    # response = requests.get(url=BASE_URL, params=request_parameters)

    # Need to account for possible failures with API? E.g.
    # {
    #     "message": "Operation failed - Most likely the backend service failed. Please try again.",
    #     "error": 8
    # }

    # Write a function which extracts the fields from the .json file, instead of
    # having to do this multiple times
    file_name = f"{start}_to_{end}_1.json" # -> "2025-01-01_to_2025-12-01_X.json"
    dump_response_to_json(response=response, full_save_path=file_path+file_name)
    
    # alternative: 
    # - 2025_january_to_november_00001.json <- convert start and end to
    # datetime, retrieve their months and concatenate.
    

    for page in range(2, number_of_pages+1):
        for record in response["recentrtracks"]["track"]:
            track_info = {
                "artist_name": record["artist"]["#text"],
                "artist_mbid": record["artist"]["mdib"],
                "album_name": record["album"]["#text"],
                "album_mbid": record["album"]["mbid"],
                "track_name": record["name"],
                "track_mbid": record["mbid"],
                "date_played_unix": int(record["date"]["uts"])
            }
            file_name = f"{start}_to_{end}_{page}.json" 
            json.dump(track_info, file_path+file_name)

    pass

if __name__ == "__main__":
    start = "2025-11-24"
    end = "2025-12-01"
    time.sleep(2)
    q, response = request_helper(start=start, end=end) 
    print(q)

    save_path = "../data/last_fm/listening_history/test.json"
    dump_response_to_json(response=response, full_save_path=save_path)


