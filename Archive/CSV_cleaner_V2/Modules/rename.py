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


def rename_headers(datafiles, cols):

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Enter the variable names that should be used in your processed output file(s)')
    left, right = st.columns([0.8,0.2])

    # WIDGET INTERACTIONS---------------------------------------------------
    def click_button():
        st.session_state.renameNext = True
        st.session_state.version=st.session_state.version+1 #update the version

    def change_vars():
        st.session_state.renameNext = False

    # WIDGET CREATION ---------------------------------------------------------------       
    #Dropdown lists for variable names
    stNames=list()
    col1, col2=st.columns(2)
    for c in range(0,len(cols)):
        stan=col1.text_input(label=f' Variable in file: {cols[c]}', value=cols[c], on_change=change_vars) #user text input
        stNames.append(stan) # append to the standardized names list

    # Widget for next button
    col1.button("Next", type="primary", key='Next_Button5', on_click=click_button)
    #--------------------------------------------------------------------------------------------  

    if st.session_state.renameNext == True:#if button is clicked
        if stNames:
            #Get the user inputted standardized names
            st_names=[]
            for c in range(0,len(cols)): 
                st_names.append(stNames[c])             

            # LOOP THROUGH FILES------------------------------------------------               
            df_list=[]
            inconsistent_cols=False
            c=0
            for file in datafiles:
                #PROCESSING************************************************************************ 
                c=c+1            
                # 1. READ FILE 
                df=readFiles.read_datafiles(file)

                # 2. PROCESS
                # Check if the number of columns in the DataFrame matches the length of the list
                if len(df.columns) == len(st_names):            
                    #Replace column names
                    df.columns=st_names

                    # 3. CREATE CSV FILE
                    df_list=save_files.create_csv_files(file, df, df_list)
                #************************************************************************************
                else:
                    inconsistent_cols=True

            if inconsistent_cols==True:
                left.warning('Some files had different column lengths, those files were not changed. Please uplaod files with the same headers.', icon="⚠️")

            else:
                #SHOW SNAPSHOT OF PROCESSES FILES-----------------------------------------------------------------------------------------------------------
                save_files.show_snapshot(df_list)

                # CALL DOWNLOAD FUNCTION---------------------------------------------------------
                download.download_output(df_list)

        else:
            st.error('Nothing was entered!', icon="🚨")
