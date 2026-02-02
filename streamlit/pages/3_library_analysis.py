import streamlit as st
from plots.genre_distribution import data_setup, plot_genre_distribution
from plots.radar_chart import plot_radar_chart

df_artists = st.session_state["artists"]
df_genres = data_setup(df_artists)

df_af = st.session_state["audio_features"]
df_avg = df_af.mean(axis=0)

st.title("Library analysis")

st.markdown(
    """
    
    """
)
with st.container():
    col_1, col_2 = st.columns([0.4, 0.6])

    with col_1:
        fig_radar = plot_radar_chart(df_avg)
        st.plotly_chart(fig_radar)

    with col_2:
        fig_genre_dist = plot_genre_distribution(df_genres)
        st.plotly_chart(fig_genre_dist)

st.divider()

st.subheader("Artist relations in my library")
with st.container():
    htmlfile = open("html/artist_network.html", 'r', encoding='utf-8')
    st.components.v1.html(htmlfile.read(), height=700)

