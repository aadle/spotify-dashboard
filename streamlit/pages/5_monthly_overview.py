import streamlit as st
import pandas as pd

# Utils
def filter_dataframe(df:pd.DataFrame, year:int, month:int) -> pd.DataFrame:
    df_filtered = df.loc[df["listened_at"].dt.year == year]
    df_filtered = df_filtered.loc[df["month"] == month]

    return df_filtered.sort_values("listened_at", axis=0, ascending=True)

# Page
st.title("monthly summary")

df_listening = st.session_state["listening"]
df_listening["month"] = df_listening["listened_at"].dt.month

with st.container(horizontal=True):
    year = st.selectbox(
        "Year",
        options=[x for x in range(2021, 2025+1)][::-1],
        width=100,
    )

    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    month = st.selectbox(
        "Month",
        options=list(months.keys()),
        format_func=lambda x: months[x],
        width=150,
        index=0
    )
    
df_current = filter_dataframe(df_listening, year, month)
df_prev = filter_dataframe(df_listening, year, month-1)
    
# Most listened artist
df_top_artists = df_current[["artist_name"]].groupby(
        ["artist_name"], as_index=False
    ).agg(num_plays=("artist_name", "count"))
df_top_artists = df_top_artists.sort_values(["num_plays"], ascending=False).reset_index(drop=True)

# Most listened tracks
df_top_tracks = df_current[["artist_name", "track_name"]].groupby(
        ["artist_name", "track_name"], as_index=False
    ).agg(num_plays=("track_name", "count"))
df_top_tracks = df_top_tracks.sort_values(["num_plays"], ascending=False).reset_index(drop=True)

col1, col2 = st.columns(spec=[0.5, 0.5])

with col1:
    st.subheader("most played artists")
    st.dataframe(df_top_artists, hide_index=True)
with col2:
    st.subheader("most played songs")
    st.dataframe(df_top_tracks, hide_index=True)

st.divider()

# Group artist, get frequency of each day of the month
df_grouped = df_current.copy()
df_grouped["date"] = df_grouped['listened_at'].dt.date
artist_freq = df_grouped.groupby([ "artist_name", "date" ]).size()
artist_freq = artist_freq.unstack(fill_value=0).apply(list,axis=1).reset_index(name="freq")
artist_freq["total"] = artist_freq["freq"].apply(lambda x: sum(x))
artist_freq = artist_freq.sort_values("total",ascending=False).reset_index(drop=True)

st.subheader("artist frequency over the month")
st.dataframe(
    artist_freq,
    column_config={
        "artist_name": "Artist",
        "freq": st.column_config.LineChartColumn("freq", y_min=0, y_max=15)
    },
    hide_index=True
)
