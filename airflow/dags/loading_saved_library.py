# Script used to move already stored .jsonl files into GCP
import pendulum
from airflow.sdk import dag, task
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator


# Set working directory to the folder shared between local and container
# os.chdir("/opt/airflow")
FILE_SOURCE = "/opt/airflow/data/spotify/saved_songs/*.jsonl"
# print(os.listdir(data_dir))

GCS_DESTINATION = "music_library/"
GCS_BUCKET = "mbe1bce4e26e_music_library_storage"

default_args = {
    "owner": "data-enger",
    "retries": 3
}
@dag(
    dag_id="loading_saved_library",
    start_date=pendulum.datetime(2025, 12, 1, tz="UTC"),
    schedule=None,
    default_args=default_args
)

def music_library_pipeline():
    @task
    def welcome_user():
        print("Welcome. This is printed to see if it actually works :o") 
        print("Lookahead.") 

    # Send .jsonl-files to GCS
    upload_to_gcs = LocalFilesystemToGCSOperator(
            task_id="local_json_to_gcs",
            src=FILE_SOURCE,
            dst=GCS_DESTINATION,
            bucket=GCS_BUCKET,
            )

    starting = welcome_user()
    starting >> upload_to_gcs

music_library_pipeline()





