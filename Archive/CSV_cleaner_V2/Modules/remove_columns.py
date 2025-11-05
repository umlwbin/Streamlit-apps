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


def which_cols(datafiles, cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('##### Which columns would you like to remove?')

    # WIDGET INTERACTIONS----------------------------------------------------
    def click_button():# If the button is clicked
        st.session_state.removeColsNext = True
        st.session_state.version=st.session_state.version+1 #update the version

    def change_vars():
        st.session_state.removeColsNext = False

    # WIDGET CREATION -------------------------------------------- 
    left, right = st.columns([0.8,0.2])
    vars_to_rem = left.multiselect(label='Select columns',options=cols, on_change=change_vars, key='remove1')
    left.button("Next", type="primary", key='Next_Button4', on_click=click_button)

    
    if st.session_state.removeColsNext ==True:#If next button is clicked
        if vars_to_rem:
            # Call next function
            remove_cols(datafiles, cols, vars_to_rem)
        else:
            left.error('Please enter one or more columns!', icon="🚨")

def remove_cols(datafiles, cols, vars_to_rem):

# LOOP THROUGH FILES------------------------------------------------   
    df_list=[] # a list of all the dataframes created for each file   
    for file in datafiles:

        #PROCESSING************************************************************************ 
        # 1. READ FILE       
        # Read the data!
        df=readFiles.read_datafiles(file)

        # 2. PROCESS
        new_df=df.drop(columns=vars_to_rem) # Drop columns

        # 3. CREATE CSV FILE
        df_list=save_files.create_csv_files(file, new_df, df_list)    

    #SHOW SNAPSHOT OF PROCESSES FILES-----------------------------------------------------------------------------------------------------------
    save_files.show_snapshot(df_list)
        
    # CALL DOWNLOAD FUNCTION---------------------------------------------------------
    download.download_output(df_list )
