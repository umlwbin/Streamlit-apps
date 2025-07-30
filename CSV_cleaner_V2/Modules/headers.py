import streamlit as st
import pandas as pd
import os
from streamlit_sortables import sort_items
import sys
import re

#Output Path
path=os.path.abspath(os.curdir)
sys.path.append(f'{path}/Modules')

#Module Imports for the different sections
import readFiles, save_files, download

def clean_headers(datafiles, cols):
    # Update version state here since there is no next button
    st.session_state.version=st.session_state.version+1

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Cleaning headers!')
    st.markdown('###### Your original column headers are: 👇🏼')
    st.write(pd.DataFrame(cols).T)
    st.markdown('')
    left, right = st.columns([0.6, 0.4])

    #PROCESSING************************************************************************ 
    cleaned_headers=[]
    chars_to_keep = "µ" # Characters to explicitly keep
    # Escape characters in chars_to_keep for safe use in regex
    escaped_chars_to_keep = re.escape(chars_to_keep)
    pattern = rf"[^A-Za-z0-9\s{escaped_chars_to_keep}]"        

    # 1. GET A LIST OF CLEANED HEADERS
    for header in cols: 
        header=header.strip() # Remove trailing white space
        header=re.sub(pattern, '_', header)

        # Collapse multiple underscores into one
        header = re.sub(r'_+', '_', header)
        
        #if header has extra _ at end
        if header.endswith('_'):
            header = header[:-1]

        #Append to final header list
        cleaned_headers.append(header)         

    # LOOP THROUGH FILES------------------------------------------------
    df_list=[]
    for file in datafiles:
        # 1. READ FILE 
        df=readFiles.read_datafiles(file)

        # 2. PROCESS 
        df = df.dropna(axis=1, how='all')# Remove columns where all values are NaN
        df.columns=list(cleaned_headers) #add new headers

        # 3. CREATE CSV FILE
        df_list=save_files.create_csv_files(file, df, df_list)      

    if cleaned_headers==cols:
        left.success('These column headers already look pretty clean to me!',icon='✅')
    else:       
        left.markdown(' ')
        left.success('Column headers are cleaned!',icon='✅')    
        
        #SHOW SNAPSHOT OF PROCESSES FILES--------------------------------------------
        save_files.show_snapshot(df_list)

    # CALL DOWNLOAD FUNCTION---------------------------------------------------------
    download.download_output(df_list)
