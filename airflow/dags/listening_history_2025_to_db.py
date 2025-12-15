# SPARK HADDE VÆRT FINT FOR AKKURAT DETTE. SNAKK OM 1000+ FILER MED 200 ENTRIES
# HVER.
import json
import pendulum
import logging
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from pathlib import Path

postgres_conn_id = "local_db"

AUDIO_FEATURES_DIR = "data/last_fm/listening_history"
directory = Path(AUDIO_FEATURES_DIR)

# Defining the dag
@dag(
    dag_id="listening_history_to_postgres",
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
                date_played_unix
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s
            );
        """ # Insert statement must match order of appearance in .jsonl-files

        for idx, file in enumerate(directory.iterdir()): # Load directory containing .json-files
            # Read the .json-file

            if file.name.startswith('.') or file.suffix != '.json':
                continue

            with open(file, encoding="utf-8", errors="replace") as input_file:
                logging.warning(f"File number {idx}: { file.__fspath__ }")
                input_json = json.load(input_file)
                docs = input_json["tracks"]

            # Loop over records in the .jsonl-file 
            for doc in docs:
                postgres_hook.run(
                    insert_statement, parameters=list(doc.values())
                )

    @task
    def staging_to_final_table():
        pass

    [ create_staging_table, create_main_table ] >> load_listening_history()

SavedListeningHistoryToPostgres()
