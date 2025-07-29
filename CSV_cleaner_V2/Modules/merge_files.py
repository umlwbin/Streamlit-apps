import streamlit as st
import pandas as pd
import os
from streamlit_sortables import sort_items
import sys

#Output Path
path=os.path.abspath(os.curdir)
sys.path.append(f'{path}/Modules')

#Module Imports for the different sections
import readFiles, save_files, download

def merge(datafiles, cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Merging all your files')

    if len(datafiles)==1:
        left, right = st.columns([0.8,0.2])
        left.info('There is only one file uploaded so no work for us! 😌', icon='ℹ️')

    df_list=[] # a list of all the dataframes created for each file
    merged_df_list=[] #We're going to add the one merged df to this list (just for sending to download function which takes a list)
    # LOOP THROUGH FILES------------------------------------------------
    for file in datafiles:

    #PROCESSING************************************************************************ 
        # 1. READ FILE 
        df=readFiles.read_datafiles(file)

        # 2. PROCESS
        # Append each data frame data frame list
        df_list.append(df)
        
    # Concatenate the list of data frames
    final_df=pd.concat(df_list,ignore_index=True)

    # Check if the columns in all files were the same
    if all([set(df_list[0].columns) == set(df.columns) for df in df_list]):
        if len(datafiles)>1:
            left, right = st.columns([0.8,0.2])
            left.success('Column headers in all files are the same! Merging...',icon='✅')

        # 3. CREATE CSV FILE
        csv_name='merged_cwout.csv'
        final_df.to_csv(csv_name, index=False)

        #SHOW SNAPSHOT OF PROCESSES FILES------------------------------------------------
        st.markdown('###### Here is a snapshot of your file!')
        st.write(df_list[0].head(10))

        # CALL DOWNLOAD FUNCTION---------------------------------------------------------
        merged_df_list.append(final_df)#Add to list (even though its just one file)
        st.session_state.version=st.session_state.version+1 #Update version here since not next button
        download.download_output(merged_df_list)
    
    else:
        left, right = st.columns([0.8,0.2])
        left.error('Column headers are not the same in all files 👎🏼. Please uplaod files with the same headers.',icon='🚨')
