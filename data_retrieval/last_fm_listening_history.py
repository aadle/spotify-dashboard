# TODO:
# - [ ] Replace dumping logic with function call instead.
# - [ ] Need to account for possible failures with API? E.g.
    # {
    #     "message": "Operation failed - Most likely the backend service failed. Please try again.",
    #     "error": 8
    # }

import json
import logging
import requests
import time
from pytz import utc
from datetime import datetime
from typing import Dict

with open("../secrets/lastfm.json") as f:
    api_credentials = json.load(f) 

date_format = "%Y-%m-%d"

file_path = "../data/last_fm_listening_history/"

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
NUM_REQUESTS = 50
USER = "GammelPerson"

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

# A function which finds the number of pages to process for a request?
def request_helper(start:str, end:str) -> (int, Dict):
    start_unix_seconds = int(
        utc.localize(datetime.strptime(start, date_format)).timestamp()
    )
    end_unix_seconds = int(
        utc.localize(datetime.strptime(end, date_format)).timestamp()
    )

    request_parameters["from"] = start_unix_seconds
    request_parameters["to"] = end_unix_seconds 

    response = requests.get(url=BASE_URL, params=request_parameters)

    # TODO: 
    # - [ ] Improve upon the design here. 
    # - [ ] Catch edge cases when the API isn't responsive.
        # Cases:
        # - status_code is not 200
        # - status_code is 200 but the returned .json-file containts keys "message" and "error"

    try:
        # Retrieving data
        attributes = response.json()["recenttracks"]["@attr"]
        num_pages = int(attributes["totalPages"]) 
        return num_pages, response.json()
    except KeyError:
        # If we get a faulty response, its likely one of two cases.
        if response.status_code != 200:
            logging.error(
                f"Data retrieval failed. Response code: {response.status_code}."
            )
        else:
            message = response.json()["message"]
            error_code = response.json()["error"]
            logging.error(
                f"API error: {message}. Error code: {error_code}."
            )
        return 0, {}
        

def dump_response_to_json(response:Dict, full_save_path:str):
    json_out = {}
    json_out["tracks"] = []
    tracks = response["recenttracks"]["track"]
    for track in tracks:
        track_info = {
                "artist_name": track["artist"]["#text"],
                "artist_mbid": track["artist"]["mbid"],
                "album_name": track["album"]["#text"],
                "album_mbid": track["album"]["mbid"],
                "track_name": track["name"],
                "track_mbid": track["mbid"],
                "date_played_unix": int(track["date"]["uts"])
            }
        json_out["tracks"].append(track_info)
    
    with open(full_save_path, "w") as outfile:
        json.dump(json_out, outfile, indent=4)

    logger.info(f"{full_save_path} have successfully been saved.")

# A function to actually handle the data
def retrieve_listening_data(start:str, end:str):

    # Converting dates into UNIX timestamps in seconds
    start_datetime = datetime.strptime(start, date_format)
    end_datetime = datetime.strptime(end, date_format)
    start_unix_seconds = int(
        utc.localize(start_datetime).timestamp()
    )
    end_unix_seconds = int(
        utc.localize(end_datetime).timestamp()
    )

    # Retrieving months from start and end date used for the filename
    start_str = start_datetime.strftime("%b").lower()
    end_str = end_datetime.strftime("%b").lower()
    file_name = f"{start}_to_{end}_{1:05d}.json" # "2025_january_to_november_00001.json"

    # Set the interval to start retrieving data from
    request_parameters["start"] = start_unix_seconds
    request_parameters["end"] = end_unix_seconds

    # First GET-request to assess how many pages the overall search has.
    # Followed by dumping the result into a .json-file.
    num_pages, response = request_helper(start, end)
    dump_response_to_json(
        response=response, 
        full_save_path=file_path+file_name
    )

    # For the remaining pages of our query, we repeat the process as done above.
    for page in range(2, num_pages+1):
        time.sleep(1) # Don't know how the rate limit works for the API, so I'll do this to ensure that I don't overflow it with GET-requests

        request_parameters["page"] = page
        file_name = f"{start_str}_to_{end_str}_{page:05d}.json"

        _, response = request_helper(start, end)
        dump_response_to_json(
            response=response, full_save_path=file_path+file_name
        )

if __name__ == "__main__":
    start = "2025-11-24"
    end = "2025-12-01"
    time.sleep(2)
    q, response = request_helper(start=start, end=end) 
    print(q)

    save_path = "../data/last_fm/listening_history/test.json"
    dump_response_to_json(response=response, full_save_path=save_path)


