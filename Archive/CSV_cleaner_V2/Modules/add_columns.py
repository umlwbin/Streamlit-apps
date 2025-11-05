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

def how_many_vars_widget(datafiles, cols):
    
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### How many fields would you like to add?')

    # WIDGET INTERACTIONS----------------------------------------------------
    def click_button():
        st.session_state.addColsNext1 = True
        #st.session_state.processedFiles=True # Set the processed files session state to true, so now the toggle button will show up (if it didn't before)

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.addColsNext1 = False

    # WIDGET CREATION --------------------------------------------
    left2, right2 = st.columns(2)
    var_num=left2.number_input(label="Number of fields to add", value=1, on_change=change_vars, key='addnum')
    st.button("Next", type="primary", key='Next_Button2', on_click=click_button) #next button

    if st.session_state.addColsNext1 ==True: #If next button is clicked
        if var_num:
            # Call next function
            add_cols(datafiles, cols, var_num)
        else:
            left2.error('Please enter a number!', icon="🚨")
            

def add_cols(datafiles, cols, var_num):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('')
    st.markdown('##### Steps')
    st.markdown('1. Enter the name of the column to add')
    st.markdown('2. Enter the value for that column. **ℹ️ Note: The value will be the same throughout the column**')
    st.markdown(f'3. Enter the column number where it should be added in your file (first column is 1, last column of this data is {len(list(cols))} )')
    left, right = st.columns([0.6, 0.4])
    left.info('If you change your mind, just leave fields empty and click next, or change the number above. 🙂', icon="ℹ️")

    # WIDGET INTERACTIONS----------------------------------------------------
    def click_button():
        st.session_state.addColsNext2 = True
        st.session_state.version=st.session_state.version+1 #update the version

    def change_vars():
        st.session_state.addColsNext2 = False

    # WIDGET CREATION ---------------------------------------------------------------       
    txt_list=[]
    txt_values_list=[]
    int_values_list=[]

    # Create widgets to enter col, value and col position
    col1,col2,col3=st.columns(3)
    for c in range(0, var_num):
        txt=col1.text_input(label='Column variable name',placeholder='E.g. project_name', value=None, on_change=change_vars, key='var')
        txt_list.append(txt)
        
        txt_val=col2.text_input(label='Variable value', placeholder="E.g. BaySys", value=None, on_change=change_vars, key='val')
        txt_values_list.append(txt_val)

        int_val=col3.number_input(label='Column number', value=(len(list(cols))+1)+c, on_change=change_vars,key='colnum')
        int_values_list.append(int_val)
    
    # Widget for next button
    st.button("Next", type="primary", key='Next_Button3', on_click=click_button) #next button

    if st.session_state.addColsNext2 == True: #If next button is clicked
        var_list=[]
        var_values_list=[]
        var_colNum_list=[]
        exit=False

        for t, tv, i in zip(txt_list, txt_values_list, int_values_list):
           #Get the dropdown field, value and col number
            if t!= None and tv!=None:
                var_list.append(t)
                var_values_list.append(tv)
                var_colNum_list.append(i)
        
            if (t!=None) and (tv==None):
                left, right = st.columns([0.8, 0.2])
                left.markdown('')
                left.warning(f'You have not entered a value for **{t}**. **{t}** wil be removed.', icon='⚠️')
  
        if all([t==None for t in txt_list]) and all([tv==None for t in txt_values_list]):
            left, right = st.columns([0.8, 0.2])
            left.markdown('')
            left.warning("You haven't entered any variables so we will just ignore it!")
        #--------------------------------------------------------------------------------------------  

        # LOOP THROUGH FILES------------------------------------------------               
        df_list=[] # a list of all the dataframes created for each file
        for file in datafiles:

            #PROCESSING************************************************************************ 
            # 1. READ FILE 
            df=readFiles.read_datafiles(file)

            # 2. PROCESS 
            new_df=df #Create a new dataframe
            
            # Add the additional variables to new dataframe
            try:
                if var_list:
                    for va, val, pos in zip(var_list, var_values_list, var_colNum_list):
                        new_df.insert(pos-1, va, val)
            except ValueError as e:
                left, right = st.columns([0.8, 0.2])
                left.markdown('')
                left.error("You already have that column name!",icon="🚨",)
                exit=True

            if exit==False:
                # 3. CREATE CSV FILE
                df_list=save_files.create_csv_files(file, new_df, df_list)
                #************************************************************************************

        if exit==False:
            #SHOW SNAPSHOT OF PROCESSES FILES-----------------------------------------------------------------------------------------------------------
            save_files.show_snapshot(df_list)

            # CALL DOWNLOAD FUNCTION---------------------------------------------------------
            download.download_output(df_list)
