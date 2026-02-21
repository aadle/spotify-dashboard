import streamlit as st
import pandas as pd

# Utils
def filter_dataframe(df:pd.DataFrame, year:int, week:int) -> pd.DataFrame:
    df_filtered = df.loc[df["listened_at"].dt.year == year]
    df_filtered = df_filtered.loc[df["week"] == week]

    # Edge case, first week of the year.
    if week == 1:
        df_prev_year = df[
            ( df["listened_at"].dt.year == year-1 ) & 
            ( df["listened_at"].dt.month == 12) & 
            ( df["listened_at"].dt.isocalendar().week == week)
        ]
        df_filtered = pd.concat([df_filtered, df_prev_year], axis=0, ignore_index=True)

    
    return df_filtered.sort_values("listened_at", axis=0, ascending=True)

# Page
st.title("weekly summary")

df_listening = st.session_state["listening"]
df_listening["week"] = df_listening["listened_at"].dt.isocalendar().week

with st.container(horizontal=True):
    year = st.selectbox(
        "Year",
        options=[x for x in range(2021, 2025+1)][::-1],
        width=100,
    ) 

    if year == 2021:
       year_opts = [x for x in range(20, 52+1)][::-1]
    else:
       year_opts = [x for x in range(1, 52+1)][::-1]
    week = st.selectbox(
        "Week",
        options=year_opts,
        width=100,
        index=2
    )
    
df_current = filter_dataframe(df_listening, year, week)
df_prev = filter_dataframe(df_listening, year, week-1)
# st.dataframe(df_prev)
    
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
    st.subheader("most listened artists")
    st.dataframe(df_top_artists, hide_index=True)
with col2:
    st.subheader("most listened songs")
    st.dataframe(df_top_tracks, hide_index=True)

st.divider()

# Group artist, get frequency of each day of the week
df_grouped = df_current.copy()
df_grouped["date"] = df_grouped['listened_at'].dt.date
artist_freq = df_grouped.groupby([ "artist_name", "date" ]).size()
artist_freq = artist_freq.unstack(fill_value=0).apply(list, axis=1).reset_index(name="freq")
artist_freq["total"] = artist_freq["freq"].apply(lambda x: sum(x))
artist_freq = artist_freq.sort_values("total",ascending=False).reset_index(drop=True)

st.subheader("artist frequency over the week")
st.dataframe(
    artist_freq,
    column_config={
        "artist_name": "Artist",
        "freq": st.column_config.LineChartColumn("freq", y_min=0, y_max=15),
    },
    hide_index=True
)
# Listening clock

# Calculate all of the above, for the week previous if applicable.

# Show differences between the two

# Frequency 
