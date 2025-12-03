import json
import logging
import requests
from datetime import datetime, timedelta
from pytz import utc
from typing import Dict

with open("../secrets/lastfm.json") as f:
    api_credentials = json.load(f) 

date_format = "%Y-%m-%d"

file_path = "../data/last_fm/listening_history/"

# Parameters needed for the API-request
BASE_URL = "http://ws.audioscrobbler.com/2.0/"
NUM_REQUESTS = 75 
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

def retrieve_ndays_listening_data(ndays:int=1):

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ndays_back = today - timedelta(days=ndays)
    today_timestamp = int(utc.localize(today).timestamp())
    ndays_back_timestamp = int(utc.localize(ndays_back).timestamp())

    request_parameters["from"] = today_timestamp
    request_parameters["to"] = ndays_back_timestamp 
    
    response = requests.get(
        url=BASE_URL, 
        params=request_parameters, 
        headers=headers
    )

    try: # Retrieving data
        attributes = response.json()["recenttracks"]["@attr"]
        total_pages = int(attributes["totalPages"]) 
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
