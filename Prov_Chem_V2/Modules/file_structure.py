import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import re
import os
import plotly.express as px


def choose_file_structure_widgets():

    st.markdown("""
        <style>
        [role=radiogroup]{gap: 1.5rem;}
        </style>
        """,unsafe_allow_html=True)

    st.markdown('#### 📑 Restructure Files')
    st.markdown('Provincial chemistry files can come in several formats. Choose from an option below.')
    st.info('If your files are already structured properly, and you would like to apply other cleaning steps, feel free to move on to the other tabs!', icon="ℹ️")
   
    structure=st.radio("Select a format", options=['Your file has one row of **headers**, **VMV codes** and **units**, and you would like to restructure the file so that there is only one header row with the VMV codes and units added ot the column names.',
                                        'Your file has a **column** with the variables/parameters and another **column** with the values of the variables. You would like to pivot the table so that each variable is its own column header.'], 
                                        horizontal=True, index=None, label_visibility="hidden")
    

    if structure:
        if structure=='Your file has one row of **headers**, **VMV codes** and **units**, and you would like to restructure the file so that there is only one header row with the VMV codes and units added ot the column names.':
            return "merge_vmv_units"
        
        else:
            return "pivot"