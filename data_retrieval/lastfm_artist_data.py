import requests
import time
import json
import psycopg2

with open("../secrets/lastfm.json") as f:
    API_KEY = json.load(f)["client_id"]
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

def get_artist_info(artist_name: str) -> dict | None:
    params = {
        "method": "artist.getInfo",
        "artist": artist_name,
        "api_key": API_KEY,
        "format": "json",
        "autocorrect": 1,
        "username": "GammelPerson",
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print(f"[Last.fm error] {artist_name}: {data['message']}")
            return None

        return data

    except requests.exceptions.RequestException as e:
        print(f"[Request error] {artist_name}: {e}")
        return None

def pull_info_from_response(response:dict):
    out = {}

    artist_info = response["artist"]
    out["artist_name"] = artist_info["name"]
    try:
        out["artist_mbid"] = artist_info["mbid"]
    except KeyError:
        out["artist_mbid"] = None
    out["artist_url"] = artist_info["url"]
    out["image_url"] = next(x["#text"] for x in artist_info["image"] if x["size"] == "extralarge")

    stats = artist_info["stats"]
    out["listeners"] = eval(stats["listeners"])
    out["playcount"] = eval(stats["playcount"])
    out["userplaycount"] = eval(stats["userplaycount"])

    out["genres"] = [tag["name"].lower() for tag in artist_info["tags"]["tag"]]

    return out

def fetch_all_artists(artist_names: list[str], delay: float = 0.25) -> list:
    results = []

    for i, name in enumerate(artist_names, start=1):
        print(f"[{i}/{len(artist_names)}] Fetching: {name}")
        info = get_artist_info(name)
        if info:
            print(f"Got {name}.")
            extracted_info = pull_info_from_response(info) 
            results.append(extracted_info)
        time.sleep(delay)  # Be polite to the API

    return results



def main():
    artists = [
        "Radiohead",
        "Portishead",
        "Massive Attack",
        # ... or load from your database/list
    ]
    conn = psycopg2.connect(
        database="music", user="music", password="music", host="localhost"
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT(artist_name) FROM temp_listening_history;"
    )
    artists = [artist[0] for artist in cur.fetchall()]

    all_data = fetch_all_artists(artists)

    # dump to .jsonl-files

    with open("../data/last_fm/lastfm_artist_data.jsonl", "w") as file_out:
        for artist in all_data:
            json.dump(artist, file_out)
            file_out.write("\n")



if __name__ == "__main__":
    main()
    
