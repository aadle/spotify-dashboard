# SPARK HADDE VÆRT FINT FOR AKKURAT DETTE. SNAKK OM 1000+ FILER MED 200 ENTRIES
# HVER.
import json
import pendulum
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from pathlib import Path
from datetime import datetime, timezone

postgres_conn_id = "local_db"

AUDIO_FEATURES_DIR = "data/last_fm/listening_history_full"
directory = Path(AUDIO_FEATURES_DIR)

# Defining the dag
@dag(
    dag_id="listening_history_to_postgres_full",
    start_date=pendulum.datetime(2025, 12, 1, tz="UTC")
)
def SavedListeningHistoryToPostgres():
    create_main_table = SQLExecuteQueryOperator(
        task_id = "create_audio_features_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS listening_history;
            CREATE TABLE IF NOT EXISTS listening_history (
                artist_name TEXT,
                track_name TEXT,
                album_name TEXT,
                date_played_unix INTEGER,
                listened_at TIMESTAMP WITH TIME ZONE,
                artist_mbid TEXT,
                track_mbid TEXT,
                album_mbid TEXT
            );
        """
    )

    create_staging_table = SQLExecuteQueryOperator(
        task_id = "create_temp_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS temp_listening_history;
            CREATE TABLE IF NOT EXISTS temp_listening_history (
                artist_name TEXT,
                track_name TEXT,
                album_name TEXT,
                date_played_unix INTEGER,
                listened_at TIMESTAMP WITH TIME ZONE,
                artist_mbid TEXT,
                track_mbid TEXT,
                album_mbid TEXT
            );
        """
    )

    
    @task
    def load_listening_history():
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        insert_statement = """
            INSERT INTO temp_listening_history (
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

        for idx, file in enumerate(directory.iterdir()): # Load directory containing .json-files
            # Read the .json-file

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
                values_out =  list(record_in.values()) + [listened_at]
                postgres_hook.run(
                    insert_statement, parameters=values_out
                )

    @task
    def load_to_prod_table():
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        insert_statement = """
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

        for idx, file in enumerate(directory.iterdir()): # Load directory containing .json-files
            # Read the .json-file

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
                values_out =  list(record_in.values()) + [listened_at]
                postgres_hook.run(
                    insert_statement, parameters=values_out
                )

    [create_staging_table, create_main_table] >> load_listening_history() # >> load_to_prod_table()

SavedListeningHistoryToPostgres()
