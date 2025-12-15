from utils.utils import get_table_data

table = "temp_listening_history"
retrieval_query = f"SELECT main_artist, artist_id from {table}"

data = get_table_data(table, retrieval_query)


