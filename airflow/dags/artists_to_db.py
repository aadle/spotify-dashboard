import json
import pendulum
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from pathlib import Path

postgres_conn_id = "local_db"

AUDIO_FEATURES_DIR = "data/spotify/artists/"
directory = Path(AUDIO_FEATURES_DIR)

# Defining the dag
@dag(
    dag_id="artists_to_postgres",
    start_date=pendulum.datetime(2025, 12, 1, tz="UTC")
)
def SavedArtistsToPostgres():
    create_main_table = SQLExecuteQueryOperator(
        task_id = "create_artists_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS artists;
            CREATE TABLE IF NOT EXISTS artists (
                name TEXT,
                artist_id TEXT,
                genres TEXT[],
                followers INTEGER,
                popularity INTEGER
            );
        """
    )

    create_staging_table = SQLExecuteQueryOperator(
        task_id = "create_temp_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS temp_artists;
            CREATE TABLE IF NOT EXISTS temp_artists (
                name TEXT,
                artist_id TEXT,
                genres TEXT[],
                followers INTEGER,
                popularity INTEGER
            );
        """
    )
    
    @task
    def load_artists():
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        insert_statement = """
            INSERT INTO temp_artists (
                name,
                artist_id,
                genres,
                followers,
                popularity 
            )
            VALUES (
                %s,%s,%s,%s,%s
            );
        """ # Insert statement must match order of appearance in .jsonl-files

        
        for file in directory.iterdir(): # Load directory containing .jsonl-files
            # Read the .jsonl-file
            if file.name.startswith('.') or file.suffix != '.jsonl':
                continue

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
    def load_to_prod_table():
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        insert_statement = """
            INSERT INTO artists (
                name,
                artist_id,
                genres,
                followers,
                popularity 
            )
            VALUES (
                %s,%s,%s,%s,%s
            );
        """ # Insert statement must match order of appearance in .jsonl-files

        
        for file in directory.iterdir(): # Load directory containing .jsonl-files
            # Read the .jsonl-file
            if file.name.startswith('.') or file.suffix != '.jsonl':
                continue

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

    create_staging_table >> load_artists()
    create_main_table >> load_to_prod_table()

SavedArtistsToPostgres()
