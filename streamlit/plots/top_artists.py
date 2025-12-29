# import sys
# import pathlib
#
# sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import argparse
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
from utils.retrieval import get_listening_data

def plot_top_artists(df:pd.DataFrame, year:int, top_n:int=20):
    fig = px.bar(
        df,
        y="artist_name",
        x="num_plays",
        color="num_plays",
        hover_name="track_name",
        hover_data=["artist_name", "num_plays", "artist_total"],
        color_continuous_scale="blugrn_r",
        title=f"Top {top_n} artists of {year}",
        labels={
            "num_plays": "# plays",
            "artist_total": "total artist plays",
            "artist_name": "artist name",
        },
    )
    fig.update_layout(showlegend=False,  
                      xaxis_title="", 
                      yaxis_title=""
                      )
    fig.update_yaxes(autorange="reversed", dtick=1)
       
    return fig

def data_setup(df:pd.DataFrame, year:int, top_n:int=20):
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year+1, 1, 1, tzinfo=timezone.utc)
    mask = (df.listened_at >= start) & (df.listened_at < end)
    df = df.loc[mask]

    df = df[["artist_name", "track_name"]].groupby(
        ["artist_name", "track_name"], as_index=False
    ).agg(num_plays=("track_name", "count"))
    df["artist_total"] = df.groupby("artist_name")["num_plays"].transform("sum")
    df = df.sort_values(["artist_total", "num_plays"], ascending=[False, True])

    # top_x_artists = df.value_counts("artist_name").iloc[:top_n]
    # df = df.query(f"artist_name == {top_x_artists.index.tolist()}")

    top_x_artists = df[["artist_name", "artist_total"]].drop_duplicates("artist_name").iloc[:top_n]
    df = df.query(f"artist_name == {top_x_artists.artist_name.tolist()}")

    # df = df.query("num_plays > 1")

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
    df["artist_total"] = df.groupby("artist_name")["num_plays"].transform("sum")
    df = df.sort_values(["artist_total", "num_plays"], ascending=[ False, True ])

    top_x_artists = df.value_counts("artist_name").iloc[:args.top_n]
    df = df.query(f"artist_name == {top_x_artists.index.tolist()}")
    # df = df.query("num_plays > 1")
    
    distribution_fig = plot_top_artists(df, args.year, args.top_n)
    distribution_fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yearly distribution")
    parser.add_argument("--year", nargs="?", default=2025, type=int)
    parser.add_argument("--top_n", nargs="?", default=25, type=int)
    args = parser.parse_args()
    main(args)
