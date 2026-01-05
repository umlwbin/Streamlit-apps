import streamlit as st

def sidebar():
    # Get CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/images/apps_images/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.image(logo, width=250)

    # Title and Description
    st.title('CSV File Cleaning Tool 🧹')
    intro="""
        This app allows you to perform basic cleaning tasks on multiple CSV files. This allows for proper ingestion into a database.
        
        - Choose an cleaning/editing option from the list on the right.
        
       -  When you are ready to download, click the **Download button** below.

        - To reset to the original data, click **Reset All Files** at the top of the page.

        """
    st.markdown(intro)
    st.markdown("")

