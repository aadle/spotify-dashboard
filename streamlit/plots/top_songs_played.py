# IDEA: in the hoverdata, add first time played and last time played of each
# song. If you want even more comprehensive data, max num played during a day.

# import sys
# import pathlib
#
# sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import argparse
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
# from local_utils.retrieval import get_listening_data
from utils.retrieval import get_listening_data

def plot_top_artists_and_songs(df:pd.DataFrame, year:int, top_n:int=20):

    # Hover data to get top_n played tracks of the month.
    fig = px.bar(
        df,
        y="y_labels",
        x="num_plays",
        color="num_plays",
        hover_name="track_name",
        color_continuous_scale="blugrn_r",
        title=f"Top {top_n} most played songs of {year}",
        labels={"num_plays": "# plays"},
        text_auto=".2s"
    )
    fig.update_layout(showlegend=False,  
                      xaxis_title="", 
                      yaxis_title=""
                      )
    fig.update_yaxes(autorange="reversed", dtick=1)
    fig.update_traces(
        textfont_size=15, textangle=0, textposition="outside", cliponaxis=False
    )
    return fig

def data_setup(df:pd.DataFrame, year:int, top_n:int=20):
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year+1, 1, 1, tzinfo=timezone.utc)
    mask = (df.listened_at >= start) & (df.listened_at < end)
    df = df.loc[mask]

    df = df[["artist_name", "track_name"]].groupby(
        ["artist_name", "track_name"], as_index=False
    ).agg(num_plays=("track_name", "count"))
    df = df.sort_values(["num_plays"], ascending=False).reset_index(drop=True)
    df["y_labels"] = df["artist_name"] + " ○ " + df["track_name"]
    df = df.iloc[:top_n]

    return df

def main(args):
    df = get_listening_data() 

    # filter data to "year" only
    start = datetime(args.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(args.year+1, 1, 1, tzinfo=timezone.utc)
    mask = (df.listened_at >= start) & (df.listened_at < end)
    df = df.loc[mask]

    df = df[["artist_name", "track_name"]].groupby(
        ["artist_name", "track_name"], as_index=False
    ).agg(num_plays=("track_name", "count"))

    df = df.sort_values(["num_plays"], ascending=False).reset_index(drop=True)
    df["y_labels"] = df["artist_name"] + " | " + df["track_name"]

    df = df.iloc[:args.top_n]
    
    distribution_fig = top_artists_and_songs(df, args.year, args.top_n)
    distribution_fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yearly distribution")
    parser.add_argument("--year", nargs="?", default=2025, type=int)
    parser.add_argument("--top_n", nargs="?", default=25, type=int)
    args = parser.parse_args()
    main(args)
