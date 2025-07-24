import streamlit as st

def app_intro_sidebar():
    # GEt CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.sidebar.image(logo, width=250)

    # Title and Description
    st.sidebar.title('Provincial Chemistry File Editor 🧑🏽‍🔬')
    st.sidebar.markdown('## Welcome!')
    st.sidebar.markdown('This app allows for the applicaiton of several cleaning steps for Provincial chemistry files.')
    st.sidebar.markdown('- Click on the **Restructure Files** tab to first restructure the file(s) according to the type of chemistry file.')
    st.sidebar.markdown('- Click on any other tab to apply that cleaning function.')
    st.sidebar.markdown('- Click on the **Download Data** tab whenever you are ready to download the processed file(s). ')


