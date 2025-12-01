import pytz
import requests
import webbrowser
from datetime import datetime, timedelta
today = pytz.utc.localize(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
yesterday = today - timedelta(days=5)
today_ms = int(today.timestamp())
yesterday_ms = int(yesterday.timestamp())

base_url = "http://ws.audioscrobbler.com/2.0/"

recent_tracks_params = {
    "limit": 20,
    "user": "GammelPerson",
    "from": yesterday_ms,
    "to": today_ms,
    "extended": 0,
    "api_key": client_json["client_id"],
    "format": "json",
    "method": "user.getrecenttracks",
}

r = requests.get(base_url, headers=headers, params=recent_tracks_params)
webbrowser.open(r.url)
r.status_code

# TODO
# - [ ] Function to set up parameters
# - [ ] Function to run a query
    # - [ ] If the query returns multiple pages, index through them. How?
# - [ ] Dump the returned data into .json-file 

# - [ ] New script to load from json to postgres, can be loaded with Airflow
# (one time use?)
# - [ ] New script: Scheduled DAG to retrieve listening history from the
# previous day.
