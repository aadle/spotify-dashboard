
from airflow.sdk import dag, task
from datetime import datetime
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    "owner": "default",
    "start_date": datetime(2025, 10, 24),
    "retries": 3
}

def welcome_user(user="default"):
    current_time = datetime.now()
    print(30*"=" + f" Welcome user {user}. Today's date is {current_time.today().date()}. "
        + 30*"=")
    print(30*"=" + f" Current time is {current_time.time()}. " 
        + 30*"=")

@dag(
    dag_id="test_postgres_connection",
    schedule="5 * * * *",
    tags=["tutorial_project", "dataskew"],
    default_args=default_args
)
def Pipeline2():
    greeting = PythonOperator(
        task_id="welcome_user",
        python_callable=welcome_user,
    )    

    sleep = BashOperator(
        task_id="sleep",
        bash_command="sleep 2",
        retries=1
    ) 

    @task
    def test_connection():
        try:
            postgres_hook = PostgresHook(postgres_conn_id="local_db")
            conn = postgres_hook.get_conn()
            cur = conn.cursor()
            print(0)
            return 0
        except Exception:
            print(1)
            return 1 

    q = test_connection()
    greeting >> sleep >> q 
    

Pipeline2()
