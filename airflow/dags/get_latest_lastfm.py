from airflow.sdk import dag, task, task_group
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pathlib import Path
# from utils.postgresql import make_postgres_query
from typing import Dict
from utils.lastfm import extract_track_data
from utils.loading import save_to_jsonl 
# from urllib3.util import Retry
import json
import pendulum
import requests
import logging
import time

# Set the parameters for querying last.fm API
dirpath = "secrets/lastfm"

dir = Path(dirpath)
with open(dirpath+"/lastfm.json") as f:
    api_credentials = json.load(f)
    print(api_credentials)
    print(f)

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
NUM_REQUESTS = 100
USER = "GammelPerson"
POSTGRES_CONNECTION_ID = "local_db"

@task
def fetch_total_pages():
    request_parameters = {
        "limit": NUM_REQUESTS,
        "user": USER,
        "extended": 0,
        "api_key": api_credentials["client_id"],
        "format": "json",
        "method": "user.getrecenttracks",
        "page": 1,  # we start indexing from page 1, 2, ...
    }
    headers = {"user-agent": "GammelPerson_2025_data"}
    request_parameters["limit"] = 1 # delete later

    # get timestamp from latest entry in the DB
    query = """
        SELECT 
            listened_at
        FROM 
            temp_listening_history
        ORDER BY 
            listened_at 
        DESC
        LIMIT 1;
    """
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)
    result = hook.get_records(sql=query)

    # calculate timestamp for current day at 00:00 UTC
    request_parameters["to"] = eval(pendulum.today("UTC").format("X")) 
    request_parameters["from"] = int(result[0][0].timestamp())

    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )
    results = response.json()

    return list(range(1, int(results["totalPages"])+1))
    return int(results["totalPages"])
    # return results


@task
def fetch_latest(page:int, retries=5) -> Dict:
    request_parameters = {
        "limit": NUM_REQUESTS,
        "user": USER,
        "extended": 0,
        "api_key": api_credentials["client_id"],
        "format": "json",
        "method": "user.getrecenttracks",
        "page": page,  # we start indexing from page 1, 2, ...
    }
    headers = {"user-agent": "GammelPerson_2025_data"}
    request_parameters["limit"] = 1 # delete later

    # get timestamp from latest entry in the DB
    query = """
        SELECT 
            listened_at
        FROM 
            temp_listening_history
        ORDER BY 
            listened_at 
        DESC
        LIMIT 1;
    """
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)
    result = hook.get_records(sql=query)

    # calculate timestamp for current day at 00:00 UTC
    request_parameters["to"] = eval(pendulum.today("UTC").format("X")) 
    request_parameters["from"] = int(result[0][0].timestamp())

    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )
    results = response.json()

    for i in range(retries):
        try:
            data = results["recenttracks"]["@attr"]
            logging.info(f"Page {page} retrieved from API-fetch.")
            return data
        except KeyError:
            sleep_duration = 1.6**i
            logging.warning(f"Error code: {results["error"]}. {results["message"]}")
            logging.warning(f"Attempt #{i} of fetching data.")
            time.sleep(sleep_duration) # approximate to fibonacci backoff strategy

@task 
def print_out(res):
    print(res)

@task
def save_to_file(response):
    filepath = Path("./data")
    extracted_data = extract_track_data(response)
    for subdir in filepath.iterdir():
        if subdir.is_dir():
            print(subdir)
    return save_to_jsonl(extracted_data, filepath/"temp_lastfm/test.jsonl")

@dag(
    dag_id="get_latest_lastfm_data",
    start_date=pendulum.datetime(2026, 2, 17, tz="UTC")
)
def GetLatestLastfmData():
    
    total_pages = fetch_total_pages()
    # print_out(total_pages)
    # fetch_latest.expand(page=total_pages)

    @task_group(group_id="etl_grouping")
    def etl_group(page):
        page_response = fetch_latest(page)
        save_to_file(page_response)
    # save_to_file(total_pages)

    etl_group.expand(page=total_pages)

    # t1 >> test_get_latest_entry >> use_result()

GetLatestLastfmData()

