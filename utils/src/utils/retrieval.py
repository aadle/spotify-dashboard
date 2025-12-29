import psycopg2
import pandas as pd
from typing import List, Tuple


def _connect_to_pgsql():
    conn = psycopg2.connect(
        database="music", user="music", password="music", host="localhost"
    )
    cur = conn.cursor()
    return cur


def get_table_data(table_name: str, query: str = None) -> List[Tuple]:
    cur = _connect_to_pgsql()

    if query:
        cur.execute(query)
        table_columns = [desc[0] for desc in cur.description]
    else:
        column_name_query = f"""
        SELECT 
            column_name 
        FROM 
            information_schema.columns 
        WHERE
            table_name = '{table_name}'
        ORDER BY ordinal_position;
        """  # "ORDER BY ordinal_position" needed such that the columns come out in the order for a normal query.
        cur.execute(column_name_query)
        table_columns = [col_name[0] for col_name in cur.fetchall()]

        cur.execute(f"SELECT * FROM {table_name};")

    table_data = cur.fetchall()

    data_records = []
    for entry in table_data:
        d = {key: value for key, value in zip(table_columns, entry)}
        data_records.append(d)

    cur.close()

    return data_records

def get_listening_data() -> pd.DataFrame:
    listening_data_lastfm = get_table_data(
        table_name="temp_listening_history",
        query="SELECT artist_name, track_name, listened_at FROM temp_listening_history;"
    ) 
    df_listening = pd.DataFrame.from_records(listening_data_lastfm)

    df_missing_listening = pd.read_csv("../data/spotify/missing_data_feb_mar_2025.csv")
    df_missing_listening = df_missing_listening[['ts', 'master_metadata_track_name', 'master_metadata_album_artist_name']]
    df_missing_listening = df_missing_listening.rename(
        {
            "ts": "listened_at",
            "master_metadata_track_name": "track_name",
            "master_metadata_album_artist_name": "artist_name",
        },
        axis=1,
    )
    df_missing_listening["listened_at"] = pd.to_datetime(
        df_missing_listening.listened_at, utc=True
    )

    df_listening = pd.concat([df_missing_listening, df_listening])
    df_listening = df_listening.sort_values("listened_at").reset_index(drop=True)

    return df_listening

