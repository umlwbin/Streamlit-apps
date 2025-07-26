import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import re
import os
import plotly.express as px
import sys
import copy

#Set page config
st.set_page_config(page_title="Provincial Chemistry App", page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

#PATHS----------------------------------------------------------------------------------------------------------------------------
#Input_path is where the script and any input files are found, output_path is where the output files are created -the current dir.
#input_path=os.path.abspath(os.curdir)+'/Prov_chem/' #For Streamlit Directory
input_path=os.path.abspath(os.curdir) #For desktop
output_path=os.path.abspath(os.curdir)
#----------------------------------------------------------------------------------------------------------------------------------

sys.path.append(f'{input_path}/Modules') #adding the Modules directory to Python's search path at runtime.

#Module Imports for the different sections
import  session_initializer, undo_redo_restart, app_setup, messages, file_uploads, file_structure, pivot_table, headers, iso_dates, parse_dates, rvq, save_and_download, units_vmv_merge

#Initialize Sessions
session_initializer.init_session_state()

#Undo, Redo, Restart Buttons
undo_redo_restart.undo_redo_restart_widgets()

#Tabs
tab1, structureTab, headersTab, isoTab, parseTab, rvqTab, downloadTab= st.tabs(['File Upload','Restructure Files', 
                                                                'Clean Headers', 'Create ISO Date-Time', 'Parse Date','Manage RVQs',
                                                                'Download Data'])

#PAGE SETUP
app_setup.app_intro_sidebar()


#Global Variables-----------------------------------------
inconsistent_cols_error=False
date_time_error=False
no_user_codes_in_files=False
just_cleaned_headers_flag=False
headers_are_the_same=False

supplementary_df_list=[]
placeholder=st.empty()


#WORKFLOW
with tab1: #File Upload Tab
    datafiles=file_uploads.fileupload_Widget() #Get all the files
    example_file=file_uploads.example_file_widget() #Use exmaple file instead

    if st.session_state.new_upload or example_file: # Clear output data whenever new files are uploaded
        for f in os.listdir(output_path):
            if 'output' in f or '_curated' in f:
                os.remove(os.path.join(output_path, f))

    #If they chose to use an example file
    if example_file:
        datafiles=[example_file]

    #If an upload was done but the files are now removed
    if st.session_state.new_upload and not datafiles:   
        messages.warnings('Please Upload CSV files')

    #If there are files, uploaded or example
    if datafiles: 
        datafiles_dfs,csvfileNames, inconsistent_cols_error=file_uploads.read_dfs(datafiles, inconsistent_cols_error) #Read the data files as dataframes

    #inconsistent columns
    if inconsistent_cols_error: 
        messages.errors('Ooops, I think your file might have inconsistent columns. Each line must have the same number of columns. Please reformat your files and re-upload.')

#All is good to begin cleaning!!!!!🙌🏽-------------------------------------
if (datafiles) and (inconsistent_cols_error==False): 
    
    if st.session_state.cleaned_df_list==[]: #Initialize st.session_state.cleaned_df_list with the original uploaded files on first run (its empty). This will keep changing after each step.
        st.session_state.cleaned_df_list=datafiles_dfs

    with structureTab: #Tab for choosing the structure of files-------------------------------------------
        #Get the option for the file structure from radio buttons
        structure_option=file_structure.choose_file_structure_widgets() or None 
 
        if structure_option=="merge_vmv_units":# STEP--- Merge VMV and UNit Rows-------------------------------------------

            #Streamlit Widget Functions -- Start of section
            vmvCode_row,units_row=units_vmv_merge.merge_rows_widget() or (None, None)

            if st.session_state.mergeRowsBegin and st.session_state.mergeRowsNext1: #next button from the above widget function is clicked

                #Processing Functions - Pure Python
                just_cleaned_headers_flag, headers_are_the_same=units_vmv_merge.merge_rows(vmvCode_row,units_row, just_cleaned_headers_flag)

                if st.session_state.cleaned_df_list:
                    #Streamlit Widget Functions -- End of section
                    if just_cleaned_headers_flag==True:
                        if headers_are_the_same:
                            messages.successes("Headers look great and did not need cleaning!") #Streamlit success message
                        else:
                            messages.successes("Headers cleaned!") #Streamlit success message
                    else:
                        messages.successes("Rows have been merged and headers cleaned!") #Streamlit success message

        if structure_option=="pivot":# STEP--- Restructure table and Extract Variables-------------------------------------------
            #Streamlit Widget Functions -- Start of section
            var_col,value_col, additional_params=pivot_table.restructure_widgets(st.session_state.cleaned_df_list) or (None,None, None)

            if var_col !=None and value_col !=None:
                if st.session_state.pivotBegin and st.session_state.pivotRadio1 and st.session_state.PivotNext1 and st.session_state.PivotNext2:
                    #Processing Functions - Pure Python
                    pivot_table.filter_df_for_each_variable(var_col,value_col, additional_params) #Extract variables as their own columns and add the VMV and Variable codes to the variable names (column headers)
                    
                    #Streamlit Widget Functions -- End of section
                    if st.session_state.cleaned_df_list:
                        messages.successes("File has been restructured!") #Streamlit success message

            
    with headersTab:# STEP--- Clean Headers-------------------------------------------       
        #Streamlit Widget Functions -- Start of section
        headers.clean_headers_widgets()

        if st.session_state.headersBegin:
            #Processing Functions - Pure Python
            headers.clean_headers(st.session_state.cleaned_df_list) #Remove special characters from headers

            #Streamlit Widget Functions -- End of section
            messages.successes("Headers have been cleaned!")

    with isoTab:#STEP 4 Convert the one dt column, or separate D & T columns to ISO------------------------------
        # Streamlit Widget Functions -- Start of section      
        date_structure_radioButton=iso_dates.Choose_One_Or_Two_DateTime_Columns_Widgets() #Separate date + time cols, or just one dateTime column? Create radio buttons to get user selection (date_structure)
        
        if st.session_state.isoBegin:
            if date_structure_radioButton: #Don't continue unless this widget has a value from user
                date_time_col=iso_dates.one_dateTime_col_Widgets(st.session_state.cleaned_df_list, date_structure_radioButton) or None #widgets for allowing user to select the date-time column
                date_col, time_col=iso_dates.separate_dateTime_cols_Widgets(st.session_state.cleaned_df_list, date_structure_radioButton) or (None, None)#widgets for allowing user to select both date and time column 

                #Processing Functions - Pure Python
                if date_time_col and st.session_state.isoNext1 == True: #If button is clicked from one_dateTime_col_Widgets:
                    date_time_error=iso_dates.convert_one_dateTime_col_to_iso(st.session_state.cleaned_df_list,date_time_col)# Convert dt col to ISO   

                if st.session_state.isoNext2 == True and date_col and time_col: #If button is clicked from separate_dateTime_cols_Widgets:
                    date_time_error=iso_dates.convert_date_and_time_cols_to_iso(date_col,time_col,st.session_state.cleaned_df_list) # Convert both cols to ISO  

                #Streamlit Widget Functions -- End of section
                if (st.session_state.isoNext1 or st.session_state.isoNext2) and date_time_error==False:
                    messages.successes('Created Date-Time column in ISO format!')

    with parseTab:#STEP--- #Parse ISO Date-Time column into yr, month, day, time-------------------------------------------     
        # Streamlit Widget Functions -- Start of section
        parse_dates.parse_date_time_Widgets()

        if st.session_state.parseBegin:
            dt_col=parse_dates.select_date_time_column_Widgets(st.session_state.cleaned_df_list) or None
        
            if dt_col:
                #Processing Functions - Pure Python
                if st.session_state.parseNext1==True:
                    date_time_error=parse_dates.extract_yr_mn_day_time(st.session_state.cleaned_df_list, dt_col) #extract the Year, motnh, day and time

                    if date_time_error==False:
                        #Streamlit Widget Functions -- End of section
                        messages.successes('Parsed the Date time column!')

    with rvqTab:#STEP--- # Result Value Qualifier (RVQ) Management-------------------------------------------
    # Streamlit Widget Functions -- Start of section
        starting_rvq_var, exceptions=rvq.choose_RVQs_Widgets(st.session_state.cleaned_df_list) or (None,None) #Allow users to choose starting RVQs and exceptions

        if st.session_state.rvqBegin:
            if st.session_state.rvqNext1 and starting_rvq_var != None: # Next button from choose_RVQs_Widgets was been clicked and a starting RVQ was selected, thus there ARE RVQ cols
                usercodes,rvqcodes=rvq.match_rvq_to_user_codes_widgets() or (None,None) #Allow user to match the User codes to rvq codes

                if st.session_state.rvqNext2 and usercodes and rvqcodes:
                    #Processing Functions - Pure Python
                    supplementary_df_list=rvq.save_rvq_df_as_csv(supplementary_df_list, usercodes,rvqcodes) #Create an RVQ df and save as csv                
                    no_user_codes_in_files=rvq.add_RVQs_to_files(st.session_state.cleaned_df_list, starting_rvq_var, exceptions, usercodes,rvqcodes) #Add RVQ columns and codes to appropriate variable columns

                    if no_user_codes_in_files==False:
                        #Streamlit Widget Functions -- End of section
                        messages.successes('Added RVQs!')

    with downloadTab:
        save_and_download.download_view_widgets(st.session_state.cleaned_df_list)

        if st.session_state.allDone:
            save_and_download.download_output(output_path, st.session_state.cleaned_df_list, csvfileNames, supplementary_df_list)
