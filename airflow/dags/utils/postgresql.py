import psycopg2
from typing import List, Tuple

def _connect_to_pgsql():
    conn = psycopg2.connect(
        database="music", user="music", password="music", host="localhost"
    )
    cur = conn.cursor()
    return cur

def make_postgres_query(query:str) -> List[Tuple]:
    cur = _connect_to_pgsql()
    cur.execute(query)
    data = cur.fetchall()
    return data

if __name__ == "__main__":
    query = """
        SELECT listened_at 
            FROM temp_listening_history
            ORDER BY listened_at DESC
        LIMIT 1;
    """
    res = make_postgres_query(query)
    print(res[0][0])
    print(int(res[0][0].timestamp()))
