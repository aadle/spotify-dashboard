from typing import Dict

def extract_track_data(response: Dict) -> [Dict]:
    records_out = []
    tracks = response["recenttracks"]["track"]
    for track in tracks:
        track_info = {
            "artist_name": track["artist"]["#text"],
            "artist_mbid": track["artist"]["mbid"],
            "album_name": track["album"]["#text"],
            "album_mbid": track["album"]["mbid"],
            "track_name": track["name"],
            "track_mbid": track["mbid"],
            "date_played_unix": int(track["date"]["uts"]),
        }
        records_out.append(track_info)

    return records_out

