import argparse
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
from utils.retrieval import get_listening_data

def unknown_pleasures(df:pd.DataFrame):
    weeks = df.week.unique().tolist()
    fig = go.Figure()
    fig.update_layout(template="plotly_dark")
    
    for week in weeks:
        temp_df = df.query(f"week == {week}")
        fig.add_trace(
            go.Scatter(
                x=temp_df["hour"],
                y=temp_df["norm_freq"]-week/1.5,
                mode="lines",
                name=f"Week {week}",
                marker=dict(
                    color="#272727"
                    # color="#EFEFEB" #reversed colorscheme
                ),
                line=dict(width=1.35),
                customdata=temp_df[["week", "hour_formatted", "freq"]],
                hovertemplate="<b>Week %{customdata[0]}, %{customdata[1]} </b><br>" +
                "<b>%{customdata[2]} scrobbles</b><br>"
            )
        )

    fig.update_layout(
        autosize=False,
        width=200,
        height=800,
        showlegend=False,
    )

    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_xaxes(showgrid=False, zeroline=False)

    return fig

def data_setup(df:pd.DataFrame, year:int):
    # Filtering by year
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    mask = (df.listened_at >= start) & (df.listened_at < end)
    df = df.loc[mask]

    # Counting the number of tracks scrobbled during each hour of the week, by
    # groupby
    df_weekly_freq = (
        df.groupby([df["listened_at"].dt.isocalendar().week, df["listened_at"].dt.hour])
        .size()
        .reset_index(name="freq")
    )
    all_weeks = range(1, 52)
    all_hours = range(0, 24)
    index = pd.MultiIndex.from_product([all_weeks, all_hours], names=["week", "hour"])
    df_weekly_freq = (
        df_weekly_freq.set_index(["week", "listened_at"])
        .reindex(index, fill_value=0)
        .reset_index()
    )

    # Normalize frequency of tracks played each hour of the week. This is the
    # data which we plot
    df_weekly_freq["norm_freq"] = df_weekly_freq.groupby("week")["freq"].transform(
        lambda x: (x - x.min()) / (x.max() - x.min() + 1e-10)
        if x.max() > x.min()
        else x
    )
    # Format the hour stamps.
    df_weekly_freq["hour_formatted"] = df_weekly_freq["hour"].apply(
        lambda x: f"{x:02d}:00"
    )

    

    return df_weekly_freq

def main(args):
    df = get_listening_data()

    # filter data to "year" only
    start = datetime(args.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(args.year + 1, 1, 1, tzinfo=timezone.utc)
    mask = (df.listened_at >= start) & (df.listened_at < end)
    df = df.loc[mask]
    df_weekly_freq = (
        df.groupby([df["listened_at"].dt.isocalendar().week, df["listened_at"].dt.hour])
        .size()
        .reset_index(name="freq")
    )
    all_weeks = range(1, 52)
    all_hours = range(0, 24)
    index = pd.MultiIndex.from_product([all_weeks, all_hours], names=["week", "hour"])
    df_weekly_freq = (
        df_weekly_freq.set_index(["week", "listened_at"])
        .reindex(index, fill_value=0)
        .reset_index()
    )

    df_weekly_freq["norm_freq"] = df_weekly_freq.groupby("week")["freq"].transform(
        lambda x: (x - x.min()) / (x.max() - x.min() + 1e-10)
        if x.max() > x.min()
        else x
    )
    df_weekly_freq["hour_formatted"] = df_weekly_freq["hour"].apply(
        lambda x: f"{x:02d}:00"
    )

    fig = unknown_pleasures(df_weekly_freq)
    fig.show()

    # group by hour
    print(df_weekly_freq[["hour", "freq"]].groupby("hour").sum("freq"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yearly distribution")
    parser.add_argument("--year", nargs="?", default=2025, type=int)
    parser.add_argument("--top_n", nargs="?", default=25, type=int)
    args = parser.parse_args()
    main(args)
