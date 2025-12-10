# Two ways of doing this

# 1. Pandas. Load .jsonl to pandas -> pandas to SQLalchemy (create scheme of table with
# pandas) -> SQLalchemy to Postgres

# 2. Airflow.

# Either way, we need to spin up the Docker container with Postgres

# Design question: Have a separate Docker container with Postgres which we
# can read and write to. Then how do we connect that DB with the DAGs?
import json
import pendulum
from datetime import datetime
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from pathlib import Path

postgres_conn_id = "local_db"
# hook = PostgresHook(postgres_conn_id=postgres_conn_id)
# conn = hook.get_conn()
# cur = conn.cursor()

SAVED_SONGS_DIR = "data/spotify/saved_songs"
directory = Path(SAVED_SONGS_DIR)

def standardize_date(date_str):
    """
    Spotify's album released date data have three types of precision –
    'year', 'month' and 'day' – which can mess up the ingestion process when
    data is loaded into PostgreSQL with data type DATE. To fix this
    ambiguity in precision I check the precision of the date string and adjust it
    accordingly. If only the year is known, we set the date to the 1st of January of
    that year.
    """
    date_str = date_str.strip()

    # Full date string, 'day' precision
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # 'month' precision
    try:
        dt = datetime.strptime(date_str, '%Y-%m')
        return dt.strftime('%Y-%m') + '-01'
    except ValueError:
        pass 

    # 'year' precision
    try:
        dt = datetime.strptime(date_str, '%Y')
        return dt.strftime('%Y') + '-01-01'
    except ValueError:
        print(f"Error: Could not parse '{date_str}' as a date.")
        return date_str 


# Defining the dag
@dag(
    dag_id="load_saved_songs_to_postgres",
    start_date=pendulum.datetime(2025, 12, 1, tz="UTC")
)
def SavedSongsToPostgres():
    create_main_table = SQLExecuteQueryOperator(
        task_id = "create_saved_songs_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS saved_songs;
            CREATE TABLE IF NOT EXISTS saved_songs (
                track_id TEXT,
                track_name TEXT,
                main_artist TEXT,
                featured_artists TEXT[],
                track_duration_ms INTEGER,
                album_name TEXT,
                album_id TEXT,
                album_release_date DATE,
                added_at TIMESTAMP WITH TIME ZONE
            );
        """
    )

    create_staging_table = SQLExecuteQueryOperator(
        task_id = "create_temp_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS temp_saved_songs;
            CREATE TABLE IF NOT EXISTS temp_saved_songs (
                track_id TEXT,
                track_name TEXT,
                main_artist TEXT,
                featured_artists TEXT[],
                track_duration_ms INTEGER,
                album_name TEXT,
                album_id TEXT,
                album_release_date DATE,
                added_at TIMESTAMP WITH TIME ZONE
            );
        """
    )

    
    @task
    def load_saved_songs():
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        insert_statement = """
            INSERT INTO temp_saved_songs (
                track_id, track_name, main_artist, featured_artists, added_at,
                track_duration_ms, album_name, album_release_date, album_id
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """ # Insert statement must match order of appearance in .jsonl-files

        for file in directory.iterdir(): # Load directory containing .jsonl-files
            if file.is_file():
                print(file)

            # Read the .jsonl-file
            with open(file) as input_file:
                docs = input_file.readlines()

            # Loop over records in the .jsonl-file 
            for doc in docs:
                record_out = json.loads(doc)

                record_out["album_release_date"] = standardize_date(record_out["album_release_date"])

                postgres_hook.run(
                    insert_statement,
                    parameters=list(record_out.values())
                )

    @task
    def staging_to_final_table():
        pass

    [ create_staging_table, create_main_table ] >> load_saved_songs()

SavedSongsToPostgres()
