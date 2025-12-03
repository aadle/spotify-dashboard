# TODO:
# - [ ] Need to account for possible failures with API? E.g.
    # {
    #     "message": "Operation failed - Most likely the backend service failed. Please try again.",
    #     "error": 8
    # }
# - [ ] For logging, save logs somewhere


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

file_path = "../data/last_fm/listening_history/"

# Parameters needed for the API-request
BASE_URL = "http://ws.audioscrobbler.com/2.0/"
NUM_REQUESTS = 100
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
    "page": 1 # we start indexing from page 1, 2, ...
    }
headers = {"user-agent": "GammelPerson_2025_data"} # identifier for the API. Recommended by the "unofficial" last.fm docs.

# Logging 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

def request_helper() -> (int, Dict): # alt. name: send_get_request()
    
    response = requests.get(
        url=BASE_URL, 
        params=request_parameters, 
        headers=headers
    )

    try: # Retrieving data
        attributes = response.json()["recenttracks"]["@attr"]
        total_pages = int(attributes["totalPages"]) 
        print(response.url)
        return total_pages, response.json()
    except KeyError:  
        # If we get a faulty response we will get a .json-file with format 
        # {
        #   "message":"Operation failed - Most likely the backend service failed. Please try again.",
        #   "error":8
        # }
        message = response.json()["message"]
        error_code = response.json()["error"]
        logging.error(
            f"Data retrieval failed. Response code: {response.status_code}."
        )
        logging.error(f"API error: '{message}'. Error code: {error_code}.")
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

def retrieve_listening_data(
    start:str, 
    end:str, 
    page_offset:int=1 # Offset must be set to the page which was not retrieved properly
):

    # Converting dates into UNIX timestamps in seconds
    start_datetime = datetime.strptime(start, date_format)
    end_datetime = datetime.strptime(end, date_format)
    start_unix_seconds = int(
        utc.localize(start_datetime).timestamp()
    )
    end_unix_seconds = int(
        utc.localize(end_datetime).timestamp()
    )

    # Because of possible API-instability, we can provide an offset to pick up 
    # from where the API malfunctioned according to the logs.
    request_parameters["page"] = page_offset
    logger.info(f"Starting data retrieval from page {page_offset}.")

    # Retrieving months from start and end date used for the filename
    start_str = start_datetime.strftime("%b").lower()
    end_str = end_datetime.strftime("%b").lower()
    file_name = f"2025_{start_str}_to_{end_str}_{page_offset:05d}.json" # e.g. "2025_jan_to_nov_00001.json"

    # Set the period from which we are retrieving data from
    request_parameters["start"] = start_unix_seconds
    request_parameters["end"] = end_unix_seconds

    # First GET-request to assess how many pages of results the period covers.
    total_pages, response = request_helper()
    logger.info(f"Total of pages retrieved: {total_pages}.")

    # Followed by dumping the first page of results into a .json-file.
    dump_response_to_json(
        response=response, 
        full_save_path=file_path+file_name
    ) 

    # For the remaining pages of our query, we repeat the process as done above.
    # We index the remaining pages of our request, and dump the results into
    # .json-files.
    for page in range(page_offset+1, total_pages+1):
        time.sleep(0.5) # Don't know how the rate limit works for the API, so I'll do this to ensure that I don't overflow it with GET-requests

        request_parameters["page"] = page
        file_name = f"2025_{start_str}_to_{end_str}_{page:05d}.json"

        total_pages, response = request_helper()
        if total_pages != 0:
            dump_response_to_json(
                response=response, 
                full_save_path=file_path+file_name
            )
        else:
            logger.error(
                f"No data retrieved. Restart the process with `page_offset={page}`."
            )
            break

        if (page % 10) == 0:
            logger.info(f"{page} requests have been processed.")
        elif (page % 40) == 0: # I think that the API is capped to 49 total requests of size 50.
            logger.info(
                f"""
                Sleeping to see if we can retrieve more data before the API terminates our request. 
                Currently on page {page}.
                """
            )
            time.sleep(10)


if __name__ == "__main__":
    start = "2025-01-01"
    end = "2025-07-01"
    page_offset = 1

    retrieve_listening_data(start=start, end=end, page_offset=page_offset)
    # time.sleep(2)
    # q, response = request_helper(start=start, end=end) 
    # print(q)
    #
    # save_path = "../data/last_fm/listening_history/test.json"
    # dump_response_to_json(response=response, full_save_path=save_path)


