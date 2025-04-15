import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
import re
import os
from datetime import datetime as dt

#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

def main():
    # GEt CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.sidebar.image(logo, width=250)

    # Title and Description
    st.sidebar.title('Idronaut Data processor 🌊')
    st.sidebar.image("https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Idronaut/img/idronaut.jpg", width=150)
    st.sidebar.html('''
    <style>
    div.s {    
        font-size: 16px;
        ul,ol {font-size: 16px; color: #333333; margin-bottom: 24px;}
        }
    </style>

    <div class="s"">

        <b>The Idronaut</b> <br>

    IDRONAUT sensors and instrumentations measure the most important physical and chemical water parameters like, temperature,
     depth, salinity, pH, dissolved oxygen and much more.
        <br><br>

        <b>What This App Does</b> <br>
    <ul>
      <li>Reads idronaut text/csv files and allows a user to visually crop the downcast</li>
      <li>Allows the user to enter the Latitude, Longitude and Site ID which is added to the processed file</li>
      <li>Curates the file to CanWIN best practices</li>
    </ul>
                  
    </div>
    '''
    )

    #Download example files Widget
    main_path=os.path.abspath(os.curdir)
    _, _, files = next(os.walk(main_path))
    files=[f for f in files if 'example' in f]
    st.sidebar.download_button(
        label="Download Example CSV",
        data=files[0],
        file_name="example.csv",
        mime="text/csv",
        icon=":material/download:",
        )
    
    # Clear output data
    for f in os.listdir(main_path):
        if 'output' in f or 'example.csv' in f:
            os.remove(os.path.join(main_path, f))

    #file_upload()


def file_upload(): 
    st.markdown('#### Upload a CSV/TXT File here')

    datafile = st.file_uploader("Choose a CSV file", accept_multiple_files=False)
    
    #If there are files uplaoded call get header widget function
    if datafile:
        if '.csv' in datafile.name or .'txt' in datafile.name:
            get_header_widget(datafiles)

        else:
            left, right = st.columns(2)
            left.warning('Oops, please uplaod a CSV/TXT files', icon="⚠️")



def download_output(final_df, final_plot_df):
    left, right = st.columns([0.8, 0.2])
    left.success('All Done! 🎉', icon="✅")

    csv=final_df.to_csv().encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="output.csv",
        mime="text/csv",
        icon=":material/download:",
        )


main()


