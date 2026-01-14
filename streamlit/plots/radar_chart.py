import argparse
import pandas as pd
import plotly.graph_objects as go
from utils.retrieval import get_table_data

def audio_feature_info():
    info = {
        "danceability": """
            Danceability describes how suitable a track is for dancing based on a<br>
            combination of musical elements including tempo, rhythm stability, beat<br>
            strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is<br> 
            most danceable."
            """,
        "energy": """
            Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of<br> 
            intensity and activity. Typically, energetic tracks feel fast, loud, and noisy.<br> 
            For example, death metal has high energy, while a Bach prelude scores low on the<br> 
            scale. Perceptual features contributing to this attribute include dynamic range,<br> 
            perceived loudness, timbre, onset rate, and general entropy.<br> 
            """,
        "instrumentalness": """
            Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated<br> 
            as instrumental in this context. Rap or spoken word tracks are clearly "vocal".<br> 
            The closer the instrumentalness value is to 1.0, the greater likelihood the<br> 
            track contains no vocal content. Values above 0.5 are intended to represent<br> 
            instrumental tracks, but confidence is higher as the value approaches 1.0.
            """,
        "liveness": """
            Detects the presence of an audience in the recording. Higher liveness values<br>  
            represent an increased probability that the track was performed live. A value<br> 
            above 0.8 provides strong likelihood that the track is live.
            """,
        "speechiness": """
            Speechiness detects the presence of spoken words in a track. The more<br> 
            exclusively speech-like the recording (e.g. talk show, audio book, poetry), the<br> 
            closer to 1.0 the attribute value. Values above 0.66 describe tracks that are<br> 
            probably made entirely of spoken words. Values between 0.33 and 0.66 describe<br> 
            tracks that may contain both music and speech, either in sections or layered,<br> 
            including such cases as rap music. Values below 0.33 most likely represent music<br> 
            and other non-speech-like tracks.
            """,
        "valence": """
            A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a<br> 
            track. Tracks with high valence sound more positive (e.g. happy, cheerful,<br>
            euphoric), while tracks with low valence sound more negative (e.g. sad,<br> 
            depressed, angry).
            """,
    }
    return info

def plot_radar_chart(df:pd.Series):

    af_info = audio_feature_info()
    r = df.values.tolist()
    r.append(r[0])
    theta = df.index.tolist()
    theta.append(theta[0])

    hover_text = [af_info[feature].strip() for feature in df.index.tolist()]
    hover_text.append(hover_text[0])

    fig = go.Figure(
        data=go.Scatterpolar(
            r=r, 
            theta=theta,
            fill="toself",
            name="!",
            hovertext=hover_text,
            hoverinfo="r+text"
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
        title=dict(text="Average audio features")
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
