from typing import Dict, List

def extract_track_data(data:Dict) -> List: # need better name
    """
    The Spotify Web API returns data relating to a track, or multiple tracks, in 
    a consistant format. This means we can write  
    """
    # Extract out:
    # - ["track"]["id"] - Spotify ID for the track

    # - ["track"]["name"] - track name
    # - ["track"]["artists"]["name"] - DETTE ER EN LISTE!!!
        # - artist: [0] er hovedartist
            # if len() > 0
            # - features: [1:] indekser utover er features
            # else:
            # - features = [""]

    # - ["added_at"] - timestamp when track was added
    # - ["track"]["duration_ms"] - duration in ms

    # - ["track"]["album"]["name"] - Album name
    # - ["track"]["album"]["release_date"] - Release date of album
    # - ["track"]["album"]["id"] - Spotify ID for album
    # - 
    # - ["track"]["popularity"] - fluctuating popularity metric 

    items = data["items"]

    records_out = [] 

    for idx, item in enumerate(items):
        track_entry = {}
        track = item["track"]

        track_entry["track_id"] = track["id"]

        track_entry["track_name"] = track["name"]
        track_entry["main_artist"] = track["artists"][0]["name"]
        track_entry["main_artist_id"] = track["artists"][0]["id"]

        if len(track["artists"]) > 1:
            track_entry["featured_artists"] = [
                feature["name"] for feature in track["artists"][1:]
            ]
            track_entry["featured_artists_ids"] = [
                feature["id"] for feature in track["artists"][1:]
            ]
        else:
            track_entry["featured_artists"] = None
            track_entry["featured_artists_ids"] = None

        track_entry["added_at"] = item["added_at"]
        track_entry["duration_ms"] = track["duration_ms"]

        track_entry["album_name"] = track["album"]["name"]
        track_entry["album_release_date"] = track["album"]["release_date"]
        track_entry["album_id"] = track["album"]["id"]
        track_entry["popularity"] = track["popularity"]

        records_out.append(track_entry)

    return records_out
