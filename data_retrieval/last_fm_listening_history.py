# 2025-12-15: The script actually retrieved all data available, not restricted
# by the interval set.

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
import logging
import requests
import time
from pytz import utc
from datetime import datetime
from typing import Dict

from local_utils.logging import setup_logging, get_current_filename
from local_utils.last_fm import extract_track_data
from local_utils.loading import save_to_jsonl

with open("../secrets/lastfm.json") as f:
    api_credentials = json.load(f)

date_format = "%Y-%m-%d"

file_path = "../data/last_fm/listening_history_full/"

dir_path = pathlib.Path(file_path)
if not dir_path.exists():
    dir_path.mkdir()

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
    "page": 1,  # we start indexing from page 1, 2, ...
}
headers = {
    "user-agent": "GammelPerson_2025_data"
}  # identifier for the API. Recommended by the "unofficial" last.fm docs.


def request_helper() -> tuple[int, Dict]:  # alt. name: send_get_request()
    response = requests.get(
        url=BASE_URL, params=request_parameters, headers=headers
    )

    try:  # Retrieving data
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


def retrieve_listening_data(
    start: str,
    end: str,
    page_offset: int = 1,  # Offset must be set to the page which was not retrieved properly
):
    current_filename = get_current_filename()
    setup_logging(current_filename)

    # Converting dates into UNIX timestamps in seconds
    start_datetime = datetime.strptime(start, date_format)
    end_datetime = datetime.strptime(end, date_format)
    start_unix_seconds = int(utc.localize(start_datetime).timestamp())
    end_unix_seconds = int(utc.localize(end_datetime).timestamp())

    # Because of possible API-instability, we can provide an offset to pick up
    # from where the API malfunctioned according to the logs.
    request_parameters["page"] = page_offset
    logging.info(f"Starting data retrieval from page {page_offset}.")

    # Retrieving months from start and end date used for the filename
    start_str = start_datetime.strftime("%b").lower()
    end_str = end_datetime.strftime("%b").lower()
    file_name = f"2020_{start_str}_to_2025_{end_str}_{page_offset:04d}.jsonl"  # e.g. "2025_jan_to_nov_00001.json"

    # Set the period from which we are retrieving data from
    request_parameters["start"] = start_unix_seconds
    request_parameters["end"] = end_unix_seconds

    # First GET-request to assess how many pages of results the period covers.
    total_pages, response = request_helper()
    logging.info(f"Total of pages retrieved: {total_pages}.")

    # Followed by dumping the first page of results into a .json-file.
    extracted_data = extract_track_data(response=response)
    save_to_jsonl(extracted_data, full_filepath=file_path + file_name)

    # For the remaining pages of our query, we repeat the process as done above.
    # We index the remaining pages of our request, and dump the results into
    # .json-files.
    for page in range(page_offset + 1, total_pages + 1):
        time.sleep(
            2
        )  # Don't know how the rate limit works for the API, so I'll do this to ensure that I don't overflow it with GET-requests

        request_parameters["page"] = page
        file_name = f"2020_{start_str}_to_2025_{end_str}_{page:04d}.jsonl"  # e.g. "2025_jan_to_nov_00001.json"

        total_pages, response = request_helper()
        if total_pages != 0:
            extracted_data = extract_track_data(response=response)
            save_to_jsonl(extracted_data, full_filepath=file_path + file_name)

        else:
            logging.error(
                f"No data retrieved. Restart the process with `page_offset={page}`."
            )
            break

        if (page % 10) == 0:
            logging.info(f"{page} requests have been processed. Sleeping...")
            time.sleep(5)
        elif (
            (page % 20) == 0
        ):  # I think that the API is capped to 49 total requests of size 50.
            logging.info(
                f"""
                Sleeping to see if we can retrieve more data before the API terminates our request. 
                Currently on page {page}.
                """
            )
            time.sleep(5)


if __name__ == "__main__":
    start = "2020-04-01"
    end = "2025-12-17"
    page_offset = 983  # HAR IKKE KJØRT 1003

    retrieve_listening_data(start=start, end=end, page_offset=page_offset)
    # time.sleep(2)
    # q, response = request_helper(start=start, end=end)
    # print(q)
    #
    # save_path = "../data/last_fm/listening_history/test.json"
    # dump_response_to_json(response=response, full_save_path=save_path)

# Retry mechanism would be huge, e.g. try three times. Reset if it works.
