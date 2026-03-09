import pendulum
import json
from pathlib import Path
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

postgres_conn_id = "local_db"

AUDIO_FEATURES_DIR = "data/last_fm"
directory = Path(AUDIO_FEATURES_DIR)

@dag(
    dag_id="artists_to_postgres_lastfm",
    start_date=pendulum.datetime(2026, 2, 23, tz="UTC")
)
def ArtistToPostgresLastFm():
    create_table = SQLExecuteQueryOperator(
        task_id = "create_artists_table",
        conn_id = postgres_conn_id,
        sql="""
            DROP TABLE IF EXISTS artists_lastfm;
            CREATE TABLE IF NOT EXISTS artists_lastfm (
                name TEXT,
                artist_id TEXT,
                artist_url TEXT,
                image_url TEXT,
                listeners BIGINT,
                playcount BIGINT,
                userplaycount BIGINT,
                genres TEXT[]
            );
        """
    )
    @task
    def load_artists():
        postgres_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        # insert_statement = """
        #     INSERT INTO artists_lastfm (
        #         name,
        #         artist_id,
        #         artist_url,
        #         image_url,
        #         listeners,
        #         playcount,
        #         userplaycount,
        #         genres
        #     )
        #     VALUES (
        #         %s,%s,%s,%s,%s,%s,%s,%s
        #     );
        # """ # Insert statement must match order of appearance in .jsonl-files
        
        with open(directory/"lastfm_artist_data.jsonl") as input_file:
            docs = input_file.readlines()

        # # Loop over records in the .jsonl-file 
        # for doc in docs:
        #     record_out = json.loads(doc)
        #     print(len(record_out.values()))
        #     postgres_hook.run(
        #         insert_statement,
        #         parameters=list(record_out.values())
        #     )

        rows = [tuple(json.loads(doc).values()) for doc in docs]

        # Insert all at once
        postgres_hook.insert_rows(
            table='artists_lastfm',
            rows=rows,
            target_fields=['name', 'artist_id', 'artist_url', 'image_url', 
                           'listeners', 'playcount', 'userplaycount', 'genres'
            ]
        )

    create_table >> load_artists()

ArtistToPostgresLastFm()
