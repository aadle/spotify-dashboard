import psycopg2
from typing import List, Tuple


def _connect_to_pgsql():
    conn = psycopg2.connect(
        database="music", user="music", password="music", host="localhost"
    )
    cur = conn.cursor()
    return cur


def get_table_data(table_name: str) -> List[Tuple]:
    cur = _connect_to_pgsql()

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
    db_column_names = [col_name[0] for col_name in cur.fetchall()]

    cur.execute(f"SELECT * FROM {table_name};")
    table_data = cur.fetchall()

    data_records = []
    for entry in table_data:
        d = {key: value for key, value in zip(db_column_names, entry)}
        data_records.append(d)

    cur.close()

    return data_records
