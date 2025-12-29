import argparse
import pandas as pd
import plotly.express as px
from utils.retrieval import get_table_data

def plot_genre_distribution(df:pd.DataFrame):
    fig = px.bar(df, 
                 x="genres", 
                 y="freq", 
                 hover_data="popular_artists_in_library",
                 title="Genre distribution in my library",
                 )
    fig.update_traces(marker_color="#4CA083")
    return fig

def data_setup(df:pd.DataFrame, top_n:int=20):
    # data = get_table_data("artists", "SELECT * FROM artists;")
    # df = pd.DataFrame.from_records(data)

    df = df.dropna(subset=["genres"])
    # df[["genres"]] = df[["genres"]].fillna(value="Unknown")
    df = df.explode("genres").reset_index(drop=True)

    df_grouped = df.groupby(by="genres").size().reset_index(name="freq")
    df_grouped = df_grouped.sort_values("freq", ascending=False)
    df_grouped = df_grouped.iloc[: top_n]

    top_genres = df_grouped.genres.tolist()
    df_top_genres = df.query(f"genres == {top_genres}").sort_values(
        "popularity", ascending=False
    )

    # Extract top 10 artists from each top genre
    top_artists_by_genre = (
        df_top_genres.groupby("genres")
        .apply(lambda group: group["name"].head(5).tolist(), include_groups=False)
        .reset_index(name="popular_artists_in_library")
    )
    df_grouped = df_grouped.merge(top_artists_by_genre, on="genres", how="left")

    return df_grouped

def main(args):
    data = get_table_data("artists", "SELECT * FROM artists;")
    df = pd.DataFrame.from_records(data)
    df = df.dropna(subset=["genres"])
    df = df.explode("genres").reset_index(drop=True)

    df_grouped = df.groupby(by="genres").size().reset_index(name="freq")
    df_grouped = df_grouped.sort_values("freq", ascending=False)
    df_grouped = df_grouped.iloc[: args.top_n]

    top_genres = df_grouped.genres.tolist()
    df_top_genres = df.query(f"genres == {top_genres}").sort_values(
        "popularity", ascending=False
    )

    # Extract top 10 artists from each top genre
    top_artists_by_genre = (
        df_top_genres.groupby("genres")
        .apply(lambda group: group["name"].head(5).tolist(), include_groups=False)
        .reset_index(name="popular_artists_in_library")
    )
    df_grouped = df_grouped.merge(top_artists_by_genre, on="genres", how="left")


    # # Alternative way
    # str_to_lower = lambda x: x.lower()
    #
    # # Get listening data from a set year
    # df_listening = get_listening_data()
    # start = datetime(args.year, 1, 1, tzinfo=timezone.utc)
    # end = datetime(args.year+1, 1, 1, tzinfo=timezone.utc)
    # mask = (df_listening.listened_at >= start) & (df_listening.listened_at < end)
    # df_listening = df_listening.loc[mask]
    #
    # # Get artist frequency from that year
    # df_202x_freq = df_listening.groupby(by="artist_name").size().reset_index(name='freq')
    # df_202x_freq.artist_name = df_202x_freq.artist_name.apply(str_to_lower)
    # artists_202x = df_202x_freq.artist_name.tolist()
    #
    # # Reference these artists in the 'artist'-table
    # df_artists_202x = df.query(f"name == {artists_202x}")
    # df_artists_202x.name = df_artists_202x.name.apply(str_to_lower)
    # df_merged = df_202x_freq.merge(right=df_artists_202x, how="right",
    #                                left_on="artist_name", right_on="name")
    # df_merged = df_merged.drop(["name"], axis=1)
    # print(df_merged)
    #
    # # Get genre frequency from df_merged
    # df_genres_freq = df_merged.groupby(by="genres").size().reset_index(name='freq')
    # df_genres_freq = df_genres_freq.sort_values(by='freq', ascending=False)
    # df_genres_freq = df_genres_freq.iloc[:args.top_n]
    #
    # # Get top 10 artists within each genres and add them as a list column
    # def get_top_10_artists(genres):
    #     df_genres = df_merged[df_merged['genres'] == genres]
    #     top_10 = df_genres.nlargest(10, 'freq')['artist_name'].tolist()
    #     return top_10
    #
    # df_genres_freq['top_10_artists'] = df_genres_freq['genres'].apply(get_top_10_artists)
    #
    # print(df_genres_freq)
    
    fig = plot_genre_distribution(df_grouped)
    fig.show()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yearly distribution")
    parser.add_argument("--top_n", nargs="?", default=20, type=int)
    parser.add_argument("--year", nargs="?", default=2025, type=int)
    args = parser.parse_args()
    main(args)
