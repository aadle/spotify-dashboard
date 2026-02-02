# import sys
# import pathlib
#
# sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import argparse
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timezone
# from local_utils.retrieval import get_listening_data
from utils.retrieval import get_listening_data


def yearly_distribution_fig(df:pd.DataFrame, year:int, top_n:int=5):
    df_dist = df.groupby(df.listened_at.dt.strftime("%Y-%m"), as_index=False).size()
    df_dist = df_dist.sort_values("listened_at")
    
    df_monthly_tracks = (
        df.groupby([df["listened_at"].dt.strftime("%Y-%m"), "track_name", "artist_name"])
        .size()
        .reset_index(name="freq")
        .rename(columns={"listened_at": "month"})
    )

    # top_tracks = (
    #     df_monthly_tracks.sort_values("freq", ascending=False)
    #     .groupby("month")
    #     .first()
    #     .reset_index()
    # )
    #
    # df_dist = df_dist.merge(top_tracks, left_on="listened_at", right_on="month", how="left")
    #
    # hover_text = [
    #     # f"<b>Most played track: {track}</b><br>by {artist}<br>{freq} plays"
    #     f"<b>Total tracks played:</b> {y}<br><b>Most played track:</b><br>{track} by {artist}<br>{freq} plays"
    #     for y, track, artist, freq in zip(df_dist["size"], df_dist["track_name"], df_dist["artist_name"], df_dist["freq"])
    # ]

    top_n_tracks = (
        df_monthly_tracks.sort_values("freq", ascending=False)
        .groupby("month")
        .head(top_n)
        .reset_index(drop=True)
    )

    top_n_dict = {}
    for month in top_n_tracks["month"].unique():
        tracks = top_n_tracks[top_n_tracks["month"] == month]
        top_n_dict[month] = tracks[["track_name", "artist_name", "freq"]].values.tolist()

    # Build hover text with top 5 tracks
    hover_text = []
    for month, y in zip(df_dist["listened_at"], df_dist["size"]):
        hover = f"<b>Total tracks played:</b> {y}<br><b>Top {top_n} tracks:</b><br>"
        
        if month in top_n_dict:
            for i, (track, artist, freq) in enumerate(top_n_dict[month], 1):
                hover += f"    <b>{i}</b>. {track} ○ {artist} ({freq} plays)<br>"
        
        hover_text.append(hover)
        
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Bar(
            x=df_dist["listened_at"],
            y=df_dist["size"],
            hovertext=hover_text,
            hoverinfo="text",
            marker=dict(
                color="#4CA083"
    ,
            )
        ))
        
    fig_dist.update_layout(
        title=f"Music consumption + live shows {year}",
        xaxis_title="Month",
        yaxis_title="# tracks played"
    )

    formatted_labels = [
        datetime.strptime(date, "%Y-%m").strftime("%B %Y") 
        for date in df_dist["listened_at"]
    ]
    fig_dist.update_xaxes(
        tickvals=df_dist["listened_at"],
        ticktext=formatted_labels,
        tickangle=-45
    )

    # # Annotations

    if year==2025:
        # Porter Robinson live
        fig_dist.add_annotation(
            x="2025-02",
            y=df_dist.query("listened_at == '2025-02'")["size"].values[0],
            text="Saw Porter Robinson live in Februray!",
            showarrow=True,
            ax=-40,
            ay=-100,
        )

        fig_dist.add_annotation(
            x="2025-04",
            y=df_dist.query("listened_at == '2025-04'")["size"].values[0],
            text="""
            Ride live
            """,
            showarrow=True,
            ax=-20,
            ay=-20,
        )

        fig_dist.add_annotation(
            x="2025-05",
            y=df_dist.query("listened_at == '2025-05'")["size"].values[0],
            text="""
            Mark William Lewis, Astrid Sonne and Fine live in Aarhus. <br>
            Tyler, the Creator live at Oslo Spektrum.""",
            showarrow=True,
            ax=-20,
            ay=-70,
        )
        

        fig_dist.add_annotation(
            x="2025-06",
            y=df_dist.query("listened_at == '2025-06'")["size"].values[0],
            text="Japanese Breakfast in Oslo",
            showarrow=True,
            ax=10,
            ay=-50,
        )

        fig_dist.add_annotation(
            x="2025-08",
            y=df_dist.query("listened_at == '2025-08'")["size"].values[0],
            text="ØYA",
            showarrow=True,
            ax=-40,
            ay=-50,
        )

        fig_dist.add_annotation(
            x="2025-10",
            y=df_dist.query("listened_at == '2025-10'")["size"].values[0],
            text="Black Country, New Road & <br> Elias Rønnenfelt live!",
            showarrow=True,
            ax=-40,
            ay=-100,
        )
        fig_dist.add_annotation(
            x="2025-11",
            y=df_dist.query("listened_at == '2025-11'")["size"].values[0],
            text="""
            Bassvictim, Evita Manji, <br>
            FAKETHIAS & Valeria Litvakov live!
            """,
            showarrow=True,
            ax=40,
            ay=-100,
        )

    if year==2024:
        # Mk.gee drops
        fig_dist.add_annotation(
            x="2024-02",
            y=df_dist.query("listened_at == '2024-02'")["size"].values[0],
            text="""
            Mk.gee releases 'Two Star & The Dream Police'
            """,
            showarrow=True,
            ax=-40,
            ay=-100,
        )

        # Surprise release by Bladee with "COLD VISIONS"
        fig_dist.add_annotation(
            x="2024-05",
            y=df_dist.query("listened_at == '2024-05'")["size"].values[0],
            text="""
            Bladee drops 'COLD VISIONS' as a huge<br>
            surprise in late April
            """,
            showarrow=True,
            ax=-40,
            ay=-90,
        )

        # Snow Strippers mania after CPH
        fig_dist.add_annotation(
            x="2024-06",
            y=df_dist.query("listened_at == '2024-06'")["size"].values[0],
            text="""
            Got hooked on Snow Strippers<br> 
            after a great show in Copenhagen!! <br>
            Faye Webster as well in CPH
            """,
            showarrow=True,
            ax=-30,
            ay=-100,
        )

        fig_dist.add_annotation(
            x="2024-08",
            y=df_dist.query("listened_at == '2024-08'")["size"].values[0],
            text="ØYA",
            showarrow=True,
            ax=-40,
            ay=-50,
        )

    if year==2023:
        fig_dist.add_annotation(
            x="2023-08",
            y=df_dist.query("listened_at == '2023-08'")["size"].values[0],
            text="""
            Gæste Gutter at Parkteateret, <br>
            ØYA
            """,
            showarrow=True,
            ax=-40,
            ay=-100,
        )

    # if year==2021:
    #     fig_dist.add_annotation(
    #         x="2022-03",
    #         y=df_dist.query("listened_at == '2021-03'")["size"].values[0],
    #         text="""
    #         Yung Lean at Sentrum Scene
    #         """,
    #         showarrow=True,
    #         ax=-40,
    #         ay=-100,
    #     )

    return fig_dist


def data_setup(df:pd.DataFrame, year:int=2025):
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year+1, 1, 1, tzinfo=timezone.utc)
    mask = (df.listened_at >= start) & (df.listened_at < end)
    df_202x = df.loc[mask]

    return df_202x

def main(args):
    df = get_listening_data() 
    print(df.columns)
    # filter data to 2025 only
    start = datetime(args.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(args.year+1, 1, 1, tzinfo=timezone.utc)
    mask = (df.listened_at >= start) & (df.listened_at < end)
    df_202x = df.loc[mask]

    # Group by month and artist or track. The goal is to get the frequency of
    # track/artists per month.

    df_monthly_tracks = (
    df_202x.groupby([df_202x["listened_at"].dt.month, "track_name"])
    .size()
    .reset_index(name="freq")
    .rename(columns={"listened_at": "month"})
    )

    top_3_tracks_per_month = (
    df_monthly_tracks.sort_values("freq", ascending=False)
    .groupby("month")
    .head(3)
    .reset_index(drop=True)
)
    print(top_3_tracks_per_month)
    distribution_fig = yearly_distribution_fig(df_202x, args.year)
    distribution_fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yearly distribution")
    parser.add_argument("--year", nargs="?", default=2025, type=int)
    args = parser.parse_args()
    main(args)
