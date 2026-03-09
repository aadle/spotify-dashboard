from airflow.sdk import dag, task, task_group
from pathlib import Path
# from utils.postgresql import make_postgres_query
from airflow.providers.postgres.hooks.postgres import PostgresHook
import time
import json
import logging
import requests
import pendulum

# Set the parameters for querying last.fm API
dirpath = "secrets/lastfm"

dir = Path(dirpath)
with open(dirpath+"/lastfm.json") as f:
    api_credentials = json.load(f)
    print(api_credentials)
    print(f)

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
NUM_REQUESTS = 200
USER = "GammelPerson"
POSTGRES_CONNECTION_ID = "local_db"

@task
def fetch_total_pages():
    request_parameters = {
        "limit": NUM_REQUESTS,
        "user": USER,
        "api_key": api_credentials["client_id"],
        "format": "json",
        "method": "library.getArtists",
    }
    headers = {"user-agent": "GammelPerson_2025_data"}

    time.sleep(0.25)
    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )
    results = response.json()
    print("from lastfm:", results)

    total_pages = int(results["artists"]["@attr"]["totalPages"])
    return list(range(1, total_pages + 1))[:10]

@task
def fetch_artists():
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)
    query = """
        SELECT 
            DISTINCT(artist_name)
        FROM
            temp_listening_history;
    """
    result = hook.get_records(sql=query)
    artists = [artist[0] for artist in result]
    return artists

@task(pool="lastfm_pool", pool_slots=1)
def fetch_artist_data(artist:str, retries=5):
    request_parameters = {
        "limit": NUM_REQUESTS,
        "user": USER,
        "api_key": api_credentials["client_id"],
        "format": "json",
        # "method": "library.getArtists",
        "artist": artist,
        "method": "artist.getInfo",
        "autocorrect": 1,
    }
    headers = {"user-agent": "GammelPerson_2025_data"}

    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )
    results = response.json()

    for i in range(retries):
        try:
            data = results
            logging.info(f"Artist '{artist}' retrieved from API-method '{request_parameters["method"]}'.")
            return data
        except KeyError:
            sleep_duration = 1.6**i
            logging.warning(f"""
            Error code '{results["error"]}': 
                {results["message"]}
            """
            )
            logging.warning(f"Attempt #{i} of fetching data.")
            time.sleep(sleep_duration) # approximate to fibonacci backoff strategy

@task
def save_to_file(data):
    pass

@task
def load_to_postgres():
    pass

@task 
def print_out(res):
    print(res)

@dag(
    dag_id="get_artist_info_lastfm",
    start_date=pendulum.datetime(2026, 2, 17, tz="UTC")
)
def GetArtistInfoLastfm():
    artists = fetch_artists()

    @task_group(group_id="etl_grouping")
    def extract_group(artist):
        page_response = fetch_artist_data(artist)
        # save_to_file(page_response)

    extract_group.expand(artist=artists) >> print_out()
    # >> load_to_postgres()
     

GetArtistInfoLastfm()

