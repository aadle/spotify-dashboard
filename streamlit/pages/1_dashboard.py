import streamlit as st
from plots.joy_divison import unknown_pleasures, data_setup

st.set_page_config(
    page_title="dog",
    page_icon="🐶",
    )

df = st.session_state["listening"]

with st.container():
    year = st.selectbox(
        "Choose year",
        options=[x for x in range(2021, 2025+1)][::-1],
        width=100,
        label_visibility="collapsed",

    )
    df_weekly_freq = data_setup(df, year)
    _, col11, col12, _ = st.columns([0.15, 0.3, 0.4, 0.15],
                                    vertical_alignment="center")
    with col11:
        fig = unknown_pleasures(df_weekly_freq)
        st.plotly_chart(fig, 
                        width=350, # width is editable here, height is editable in unknown_pleasures()
                        config = {'scrollZoom': False},)
        

    with col12:
        grouped_hour = df_weekly_freq.groupby("hour", as_index=False)["freq"].sum()
        peak_hour = grouped_hour.loc[grouped_hour["freq"].idxmax(), "hour"]
        peak_hour_formatted = f"{peak_hour:02d}:00+00"

        grouped_week = df_weekly_freq.groupby("week", as_index=False)["freq"].sum()
        peak_week = grouped_week.loc[grouped_week["freq"].idxmax(), "week"]
        n_scrobbles = grouped_week["freq"].max()
        
        # st.dataframe(grouped_week)
        st.subheader(
            f"Your peak listening time was {peak_hour_formatted}. Week {peak_week} is the most scrobbled week of {year}, with *{n_scrobbles}* scrobbles.",
            text_alignment="center",
        )
        st.markdown(":small[I've seen pattern on a t-shirt before...]",
                    text_alignment="center")

        if year==2021:
            st.markdown(
                ":small[ *I started scrobbling with in May of 2021 last.fm, explaining the lack of curved lines* ]",
                text_alignment="center")
        elif year==2025:
            st.markdown(
                ":small[*(The data cutoff is at 16.12.2025.)*]",
                text_alignment="center"
            )
