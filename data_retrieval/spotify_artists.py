import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from local_utils.retrieval import get_table_data

table = "temp_listening_history"
retrieval_query = f"SELECT main_artist, main_artist_id from {table}"

data = get_table_data(table, retrieval_query)

# Retrieve data from saved_songs 
# - main_artist and main_artist_id
# - feature_artists and feature_artists_ids
# - Gjøre dem om til Pandas-dataframes
# - Concat dem og fjerne alle NaNs og duplicates.
