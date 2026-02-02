from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator
import pendulum
 
@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    tags=["example"],
)
def dag_():
    @task()
    def task_1():
        print("Hello, World!")
        return 0

    task_2 = BashOperator(
        task_id="print_date",
        bash_command="date",
    ) # oppgave 2 

    starting_task = task_1()
    starting_task >> task_2 # oppgave 2 følger etter at oppgave 1 er ferdig
dag_() 
