import streamlit as st

def sidebar():
    # Get CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.sidebar.image(logo, width=250)

    # Title and Description
    st.sidebar.title('CSV File Cleaning Tool 🧹')
    st.sidebar.html('''
    <style>
    div.s {    
        font-size: 16px;
        ul,ol {font-size: 16px; color: #333333; margin-bottom: 24px;}
        }
    </style>

    <div class="s"">
    This app allows you to perform basic cleaning tasks on multiple files:<br><br>
        <ul>
        <li>Rearrange columns</li>
        <li>Rename columns</li>
        <li>Add columns</li>
        <li>Remove columns</li>
        <li>Clean headers (remove special characters)</li>
        <li>Merge multiple files</li>
        <li>Convert date-time column to ISO format</li>
        <li>Merge a date column and a time column into one</li>
        </ul>
    </div> 
    '''
    )
