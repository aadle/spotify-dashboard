import argparse
import pandas as pd
import plotly.graph_objects as go
from utils.retrieval import get_table_data

def plot_radar_chart(df:pd.Series):
    r = df.values.tolist()
    r.append(r[0])
    theta = df.index.tolist()
    theta.append(theta[0])

    fig = go.Figure(
        data=go.Scatterpolar(
            r=r, 
            theta=theta,
            fill="toself",
            name="!"
        )
    )
    fig.update_traces(marker_color="#4CA083")
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
            ),
            bgcolor="#EFEFEB",
        ),
        showlegend=False,
        title=dict(text="Average audio features of my library")
    )
    return fig

def main():
    data = get_table_data("temp_audio_features", "SELECT * FROM temp_audio_features")
    df = pd.DataFrame.from_records(data)
    df = df[
        [
            # "track_name",
            # "main_artist",
            "danceability",
            "energy",
            "instrumentalness",
            "liveness",
            "speechiness",
            "valence",
        ]
    ]
    df_avg = df.mean(axis=0)

    fig = plot_radar_chart(df_avg)
    fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yearly distribution")
    args = parser.parse_args()
    main()
