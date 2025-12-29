import streamlit as st
import pandas as pd
from utils.retrieval import get_listening_data, get_table_data

st.set_page_config(
    page_title="Spotify Dashboard app",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",)

# As a consequenec of converting local_utils into a package, logging and perhaps
# other file-dependent function are broken.

df_listening = get_listening_data()
st.session_state["listening"] = df_listening

df_artists = pd.DataFrame.from_records(
    get_table_data("artists", "SELECT * FROM artists;")
)
st.session_state["artists"] = df_artists

data_af = get_table_data("temp_audio_features", "SELECT * FROM temp_audio_features")
df_af = pd.DataFrame.from_records(data_af)
df_af = df_af[
    [
        "danceability",
        "energy",
        "instrumentalness",
        "liveness",
        "speechiness",
        "valence",
    ]
]
st.session_state["audio_features"] = df_af

# st.dataframe(df)

page_1 = st.Page("pages/1_dashboard.py", title="Joy Division Reference")
page_2 = st.Page("pages/2_annual_listening.py", title="Annual Listening")
page_3 = st.Page("pages/3_library_analysis.py", title="Library Analysis")
pages = [page_1, page_2, page_3]
pg = st.navigation(pages)


pg.run()
