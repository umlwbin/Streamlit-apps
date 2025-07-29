import streamlit as st
import pandas as pd
import os
import sys

#Output Path
path=os.path.abspath(os.curdir)

def fileuploadfunc(func): 
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('')
    st.markdown('#### Upload a CSV/TXT File here')
    st.markdown(' ')

    # WIDGET INTERACTIONS----------------------------------------------------
    def newUpload():
        st.session_state.new_upload=True

        # Clear output data
        for f in os.listdir(path):
            if 'output' in f or 'cwout' in f:
                os.remove(os.path.join(path, f))

    # WIDGET CREATION --------------------------------------------
    datafiles = st.file_uploader("Choose a CSV file", accept_multiple_files=True, on_change=newUpload, type="csv")
    
    #PROCESSING----------------------------------------------------
    if st.session_state.new_upload and datafiles:#If there are files uplaoded
        
        # 1. GET COLUMNS
        file=datafiles[0]#Grab just one file

        try: #Do a check to see if the columns are consistent
            df = pd.read_csv(file)
        except pd.errors.ParserError as e:
            left, right = st.columns([0.8, 0.2])
            left.error('Ooops, I think your file might have inconsistent columns. Each line must have the same number of columns. Please reformat your files and re-upload.', icon="🚨")
                    
        else: # Columns are consistent!
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            cols=list(df.columns)

            return datafiles, cols, func
    else:
        return [],[], func
