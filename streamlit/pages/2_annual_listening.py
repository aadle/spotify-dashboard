import streamlit as st 
import plots.top_artists as ta
import plots.top_songs_played as tsp
import plots.listening_dist_yearly as ldy

df_listening = st.session_state["listening"]


with st.container(horizontal=True):
    year = st.selectbox(
        "Choose year",
        options=[x for x in range(2021, 2025+1)][::-1],
        width=100,
        label_visibility="collapsed",
    ) 
    top_n = 25
    df_ta = ta.data_setup(df_listening, year, top_n)
    df_tsp = tsp.data_setup(df_listening, year, top_n)
    df_ldy = ldy.data_setup(df_listening, year)

with st.container():

    col00, col11, col12 = st.columns([0.2, 0.4, 0.4])
    with col00:
            st.space("large")
            st.image(f"imgs/wrapped_{year}.jpeg")
    
    with col11:
        genre_fig = ta.plot_top_artists(df_ta, year, top_n)
        st.plotly_chart(genre_fig, height=700)

    with col12:
        artist_fig = tsp.plot_top_artists_and_songs(df_tsp, year, top_n)
        st.plotly_chart(artist_fig, height=700)

    st.subheader(f"{df_ldy.shape[0]} total tracks played in {year}",
                text_alignment="center")
    # st.markdown(":small[*Possibility to get favorite genre based on artists*]",
    #             text_alignment="center")

    st.markdown("",text_alignment="center")


    fig = ldy.yearly_distribution_fig(df_ldy, year, 10)
    st.plotly_chart(fig, height=600)
    st.markdown(":small[ *Hover over the bars to get the top 10 played songs of that month* ]")
    

    if year==2025:
        st.markdown(
            """
            What could be the cause of drop in consumption from June and
            onwards? Well for one, I have stopped listening to music while
            reading or working. If I was to work while listening to something, I
            now would listen to white noise as I don't find it as distracting as music
            (even for genres such as classical and ambient).

            The drop in music consumption can also be explained by an increase of
            podcast listening which is not accounted for in the Last.fm data. 
            """
        )
