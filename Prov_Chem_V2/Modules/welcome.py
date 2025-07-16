import streamlit as st

def welcome_widgets():

    st.markdown('## Welcome!')
    st.markdown('This app allows for the applicaiton of several cleaning steps for Provincial chemistry files.')
    st.markdown('Click on the **File Structure** tab to first restructure file according to the type of chemistry file. Then click on any other tab to apply that cleaning functioion.')
    st.markdown('Click on the **Download** tab whenever you are ready to download the processed file(s). If you need to upload another file, simply remove the currrent file and re-uplaod a new file under the **File Upload** tab. ')