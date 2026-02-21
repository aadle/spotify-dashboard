from airflow.sdk import dag
from airflow.providers.standard.operators.bash import BashOperator
from pathlib import Path
from utils.postgresql import make_postgres_query
from typing import Dict
# from urllib3.util import Retry
import json
import pendulum
import requests
import logging
import time

# calculate timestamp for current day at 00:00 UTC
today_unixstamp = eval(pendulum.today("UTC").format("X"))

# from DB, get latest entry w.r.t. listened at
query = """
    SELECT listened_at 
        FROM temp_listening_history
        ORDER BY listened_at DESC
    LIMIT 1;
"""
latest_unixstamp = int(make_postgres_query(query)[0][0])

# Set the parameters for querying last.fm API
dirpath = "secrets/lastfm"

dir = Path(dirpath)
with open(dirpath+"/lastfm.json") as f:
    api_credentials = json.load(f)
    print(api_credentials)
    print(f)

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
USER = "GammelPerson"
request_parameters = {
    "artist": None, # Iteratively change
    "autocorrect": 1,
    "username": "GammelPerson",
    "api_key": api_credentials["client_id"],
    "format": "json",
    "method": "artist.getInfo"
    }
headers = {"user-agent": "GammelPerson_2025_data"} # identifier for the API. Recommended by the "unofficial" last.fm docs.

def send_lastfm_request() -> Dict:
    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )
    # if "error" in response.json().keys():
    #     return None
    # else:
    results = response.json()
    return results
    

def try_fetch_latest_lastfm(max_retries=5):
    for i in range(max_retries):
        try:
            results = send_lastfm_request()
            data = results["recenttracks"]["@attr"]
            return data
        except KeyError:
            logging.error(f"Error code: {results["error"]}. {results["message"]}")
            logging.info(f"Attempt #{i} of fetching data.")
            time.sleep(1.6**i) # approximate to fibonacci backoff strategy

def fetch_lastfm_data():

    # Get list of artists to get data on
    # - Have some criterion to which artists should be collected data on?
    #   If so, requires joing with 'temp_listening_history' such that we can get
    #   frequency and include if > 5 total listens or something.

    artists_list = []
    request_parameters["artist"] = artists_list[0]

    init_data = try_fetch_latest_lastfm()
    # write to .jsonl file...

    for artist in artists_list[1:]:
        request_parameters["artist"] = artist
        data = try_fetch_latest_lastfm()

        # save data in a desireable format

@dag(
    dag_id="get_latest_lastfm_data",
    start_date=pendulum.datetime(2026, 2, 17, tz="UTC")
)
def GetLatestLastfmData():
    t1 = BashOperator(
    task_id="print_date",
    bash_command="date",
    )

    t1 

GetLatestLastfmData()

