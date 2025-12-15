import json
import pendulum
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from pathlib import Path

postgres_conn_id = "local_db"

AUDIO_FEATURES_DIR = "data/reccobeats"
directory = Path(AUDIO_FEATURES_DIR)

# Defining the dag
@dag(
    dag_id="audio_features_to_postgres",
    start_date=pendulum.datetime(2025, 12, 1, tz="UTC")
)
def SavedAudioFeaturesToPostgres():
    create_main_table = SQLExecuteQueryOperator(
        task_id = "create_audio_features_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS audio_features;
            CREATE TABLE IF NOT EXISTS audio_features (
                reccobeats_id TEXT,
                acousticness FLOAT,
                danceability FLOAT,
                energy FLOAT,
                instrumentalness FLOAT,
                key INTEGER,
                liveness FLOAT,
                loudness FLOAT,
                mode INTEGER,
                speechiness FLOAT,
                tempo FLOAT,
                valence FLOAT,
                track_id TEXT,
                main_artist TEXT,
                track_name TEXT
            );
        """
    )

    create_staging_table = SQLExecuteQueryOperator(
        task_id = "create_temp_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS temp_audio_features;
            CREATE TABLE IF NOT EXISTS temp_audio_features (
                reccobeats_id TEXT,
                acousticness FLOAT,
                danceability FLOAT,
                energy FLOAT,
                instrumentalness FLOAT,
                key INTEGER,
                liveness FLOAT,
                loudness FLOAT,
                mode INTEGER,
                speechiness FLOAT,
                tempo FLOAT,
                valence FLOAT,
                track_id TEXT,
                main_artist TEXT,
                track_name TEXT
            );
        """
    )

    
    @task
    def load_saved_songs():
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        insert_statement = """
            INSERT INTO temp_audio_features (
                reccobeats_id,
                acousticness,
                danceability,
                energy,
                instrumentalness,
                key,
                liveness,
                loudness,
                mode,
                speechiness,
                tempo,
                valence,
                track_id,
                main_artist,
                track_name
            )
            VALUES (
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s
            );
        """ # Insert statement must match order of appearance in .jsonl-files

        for file in directory.iterdir(): # Load directory containing .jsonl-files
            # Read the .jsonl-file
            with open(file) as input_file:
                docs = input_file.readlines()

            # Loop over records in the .jsonl-file 
            for doc in docs:
                record_out = json.loads(doc)
                print(len(record_out.values()))
                postgres_hook.run(
                    insert_statement,
                    parameters=list(record_out.values())
                )

    @task
    def staging_to_final_table():
        pass

    [ create_staging_table, create_main_table ] >> load_saved_songs()

SavedAudioFeaturesToPostgres()
