import streamlit as st
import pandas as pd
import os
import sys

#Output Path
path=os.path.abspath(os.curdir)

#Add Modules
sys.path.append(f'{path}/Modules')

import  session_initializer

def fileuploadfunc():
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('')
    st.markdown('#### Upload a CSV/TXT File here')
    st.markdown(' ') 

    # WIDGET INTERACTIONS----------------------------------------------------
    def newUpload():
        #st.session_state.new_upload=True
        session_initializer.reset_widget_flags() #Reset all the next buttons that are not directly widgetkeys. 
  
        # Clear output data
        for f in os.listdir(path):
            if 'output' in f or 'cleaned' in f:
                os.remove(os.path.join(path, f))

    # WIDGET CREATION --------------------------------------------
    uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True,type="csv", on_change=newUpload, key="new_upload")
    st.markdown("")

    #PROCESSING----------------------------------------------------
    if uploaded_files and st.session_state.new_upload: #If there are files uplaoded
        st.session_state.uploaded_files = uploaded_files
        return uploaded_files
    
    else:
        return []