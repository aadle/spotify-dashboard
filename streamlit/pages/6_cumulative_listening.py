import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy import signal

def cumulative_listening(df:pd.DataFrame) -> pd.DataFrame:
    df_grouped = df.groupby(["date"]).size()
    date_range = pd.date_range(
        start=df_grouped.index.min(), 
        end=df_grouped.index.max()
    )
    df_grouped = df_grouped.reindex(date_range.date, fill_value=0)
    
    return df_grouped.cumsum()

df_listening = st.session_state["listening"]
df_listening["date"] = df_listening["listened_at"].dt.date
df_listening["year"] = df_listening["listened_at"].dt.year
df_listening["md"] = df_listening["listened_at"].dt.strftime("%m-%d")
df_listening["day_of_year"] = df_listening["listened_at"].dt.day_of_year


daily_counts = (
    df_listening.groupby(["year", "date", "day_of_year", "md"])
    .size()
    .reset_index(name="plays")
)
daily_counts["cumulative_plays"] = daily_counts.groupby("year")["plays"].cumsum()

st.dataframe(daily_counts)

fig = go.Figure()
for year in list(range(2021, 2026+1)):
    df_y = daily_counts.loc[daily_counts.year == year]
    fig.add_trace(
        go.Scatter(
            x=df_y["day_of_year"],
            y=signal.savgol_filter(df_y["cumulative_plays"], 10, 3,).astype("int"),
            # y=df_y["cumulative_plays"],
            mode="lines",
            name=year,
        )
    )

fig.update_layout(
    xaxis=dict(title=dict(text="# day of year")),
    yaxis=dict(title=dict(text="frequency")),
    title=dict(
        text="Cumulative frequency over the year"
    ),
)
st.plotly_chart(fig)
