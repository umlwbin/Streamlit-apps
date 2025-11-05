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


def reorder(datafiles, cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown(" ")
    st.markdown('##### Organize column headers below')
    st.markdown(" ")

    # WIDGET INTERACTIONS----------------------------------------------------
    def click_button(): #If button is clicked
        st.session_state.reorderNext = True
        st.session_state.version=st.session_state.version+1

    # WIDGET CREATION --------------------------------------------      
    var_list=sort_items(cols) #Sort Items widget 
    sort_button=st.button("Next", type="primary", key='Next_Button1', on_click=click_button) #Next button

    if sort_button and st.session_state.reorderNext==True: #If next button is clicked
        if var_list:
            key_error=False
            df_list=[] # a list of all the final dataframes created for each file
            for file in datafiles:

                #PROCESSING************************************************************************
                # 1. READ FILE 
                df=readFiles.read_datafiles(file)

                # 2. PROCESS 
                new_df=pd.DataFrame() #Create a new dataframe

                try:
                    for v in var_list:  # Loop through the widget selections and update new dataframe 
                        new_df[v]=df[v]
                except KeyError as e:
                    key_error=True
                    st.error('There is an error with a column header, perhaps a special character. Please use the **Clean column headers** function and try again.', icon="🚨")

                if key_error==False:
                    # 3. CREATE CSV FILE
                    df_list=save_files.create_csv_files(file, new_df, df_list)
                    #************************************************************************************

            if key_error==False:
                #SHOW SNAPSHOT OF PROCESSED FILES--------------------------------------------
                save_files.show_snapshot(df_list)

                #Call download function
                download.download_output(df_list)
        else:
            st.error('You did not reorder 🙃', icon="🚨")