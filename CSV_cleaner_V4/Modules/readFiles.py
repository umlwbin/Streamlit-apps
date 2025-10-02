import streamlit as st
import pandas as pd

def read_datafiles(file):
    #Reorder Next is a special case
    if st.session_state.reorderNext: 
        if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files if toggle is simply off, or its just the first run
            try: #Just because there is no on_change function for the sort_items customized streamlit widget, so we cant set st.session_state.reorderNext = False for a change
                file.seek(0) #Go back to beginning of file
            except AttributeError:
                st.session_state.version=st.session_state.version+1
                left, right = st.columns([0.8, 0.2])
                left.warning('Oops, you might have to make that switch again, sorry!', icon="⚠️")

    else:
        if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files if toggle is simply off, or its just the first run
            file.seek(0) #Go back to beginning of file
    
    df=pd.read_csv(file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns
    return df