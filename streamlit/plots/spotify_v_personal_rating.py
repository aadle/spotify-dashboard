# import sys
# import pathlib
#
# sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import argparse
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timezone
# from local_utils.retrieval import get_listening_data, get_table_data
from utils.retrieval import get_listening_data, get_table_data

def spotify_poplulartiy_vs_personal_ranking(df:pd.DataFrame, args):
    fig = px.scatter(
        df, 
        x="popularity", 
        y="personal_ranking",
        title="Personal ranking vs popularity on Spotify as of 16-12-2025",
        color="num_plays",
        hover_data=["followers", "artist_name", "genres", "num_plays"],
    )
    
    fig.update_traces(marker_size=25)
    fig.update_yaxes(autorange="reversed")
    
    x_line = [0, 100]
    y_line = [args.top_n, 0]
    
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            line=dict(color='rgba(128, 128, 128, 0.5)', width=2, dash='dash')
        )
    )
    fig.update_layout(showlegend=False)
    return fig

def main(args):
    df_listening = get_listening_data()
    start = datetime(args.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(args.year+1, 1, 1, tzinfo=timezone.utc)
    mask = (df_listening.listened_at >= start) & (df_listening.listened_at < end)
    df_listening = df_listening.loc[mask]

    artists = get_table_data(
        "artists", 
        "SELECT name, followers, popularity, genres FROM artists;"
    )
    df_artists = pd.DataFrame.from_records(artists)
    df_artists = df_artists.rename({"name": "artist_name"}, axis=1)

    to_lowercase = lambda x: x.lower()
    df_listening["artist_name"] = df_listening["artist_name"].apply(to_lowercase)
    df_artists["artist_name"] = df_artists["artist_name"].apply(to_lowercase)

    df_personal = df_listening.groupby(
        "artist_name", as_index=False
    ).agg(num_plays=("artist_name", "count"))
    df_personal = df_personal.sort_values(
        "num_plays", ascending=False
    ).reset_index(drop=True)
    df_personal["personal_ranking"] = df_personal.index + 1

    df = df_artists.merge(df_personal, how="left", on="artist_name")
    df = df.dropna(subset="num_plays")
    df = df.astype({"personal_ranking": int, "num_plays": int})
    df = df.query(f"personal_ranking <= {args.top_n}")
    df = df.query("popularity > 0")

    fig = spotify_poplulartiy_vs_personal_ranking(df, args)
    fig.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yearly distribution")
    parser.add_argument("--year", nargs="?", default=2025, type=int)
    parser.add_argument("--top_n", nargs="?", default=150, type=int)
    args = parser.parse_args()
    main(args)
