from airflow.sdk import dag, task, task_group
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
from utils.lastfm import extract_track_data
from utils.loading import save_to_jsonl 
import json
import pendulum
import requests
import logging
import time
import shutil

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

    # get timestamp from latest entry in the DB
    query = """
        SELECT 
            date_played_unix
        FROM 
            listening_history
        ORDER BY 
            date_played_unix 
        DESC
        LIMIT 1;
    """
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)
    result = hook.get_records(sql=query)

    # calculate timestamp for current day at 00:00 UTC
    # request_parameters["to"] = int(pendulum.today("UTC").format("X")) 
    request_parameters["to"] = int(pendulum.now("UTC").format("X")) 
    request_parameters["from"] = int(result[0][0]) + 1

    logging.info(
        f"Getting results from {request_parameters["from"]} to {request_parameters["to"]}."
    )

    time.sleep(1)
    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )
    results = response.json()
    print("from lastfm:", results)

    total_pages = int(results["recenttracks"]["@attr"]["totalPages"])
    return list(range(1, total_pages + 1))


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

    # get timestamp from latest entry in the DB
    query = """
        SELECT 
            date_played_unix
        FROM 
            listening_history
        ORDER BY 
            date_played_unix 
        DESC
        LIMIT 1;
    """
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)
    result = hook.get_records(sql=query)

    # get latest entry and nudge by one to not get a duplicate result
    request_parameters["from"] = int(result[0][0]) + 1

    # calculate timestamp for current day at 00:00 UTC
    # request_parameters["to"] = int(pendulum.today("UTC").format("X")) 
    request_parameters["to"] = int(pendulum.now("UTC").format("X")) 

    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )
    results = response.json()

    for i in range(retries):
        try:
            data = results
            logging.info(f"Page {page} retrieved from API-fetch.")
            return data
        except KeyError:
            sleep_duration = 1.6**i # approximate to Fibonacci backoff strategy
            logging.warning(f"Error code: {results["error"]}. {results["message"]}")
            logging.warning(f"Attempt #{i} of fetching data.")
            time.sleep(sleep_duration)

@task 
def print_out(res):
    print("Output value:", res)

@task
def save_to_file(response, page:int):
    current_date = datetime.today().strftime("%Y-%m-%d")
    dir_path = Path("./data")
    extracted_data = extract_track_data(response)

    # Not good, will send duplicates into DB
    for subdir in dir_path.iterdir():
        if subdir.is_dir():
            print(subdir)
    return save_to_jsonl(
        extracted_data, 
        dir_path/f"temp_lastfm/{current_date}_lastfm_daily_{page}.jsonl"
    )

@task
def load_to_postgres():
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)
    dir_path = Path("./data/temp_lastfm")

    insert_query = """
            INSERT INTO listening_history (
                artist_name,
                artist_mbid,
                album_name,
                album_mbid,
                track_name,
                track_mbid,
                date_played_unix,
                listened_at
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s
            );
        """ # Insert statement must match order of appearance in .jsonl-files

    for file in dir_path.iterdir():
        if file.name.startswith('.') or file.suffix != '.jsonl':
            continue

        with open(file, encoding="utf-8", errors="replace") as input_file:
                docs = input_file.readlines()

        # Loop over records in the .jsonl-file 
        for doc in docs:
            record_in = json.loads(doc)
            listened_at = datetime.fromtimestamp(
                record_in["date_played_unix"], timezone.utc
            )
            values_out = list(record_in.values()) + [listened_at]
            hook.run(
                insert_query, parameters=values_out
            )
            logging.info(f"{doc} loaded to listening_history.")

@task
def move_files_to_archive():
    source_path = Path("./data/temp_lastfm")
    destination_path = Path("./data/temp_lastfm/archived")  

    for file in source_path.iterdir():
        filename = file.name # 'file' gives you the full path of each file
        if file.name.startswith('.') or file.suffix != '.jsonl':
            continue

        shutil.move(source_path/filename, destination_path/filename)
        logging.info(f"Moved {source_path/filename} -> {destination_path/filename}")

@dag(
    dag_id="get_latest_lastfm_data",
    start_date=pendulum.datetime(2026, 2, 17, tz="UTC"),
    schedule="@daily"
)
def GetLatestLastfmData():
    
    total_pages = fetch_total_pages()

    @task_group(group_id="etl_grouping")
    def extract_group(page):
        page_response = fetch_latest(page)
        print_out(page_response)
        # save_to_file(page_response, page)

    # extract_group.expand(page=total_pages) >> load_to_postgres() >> move_files_to_archive()

    extract_group.expand(page=total_pages)

GetLatestLastfmData()

