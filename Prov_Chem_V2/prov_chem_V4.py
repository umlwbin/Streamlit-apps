import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import re
import os
import plotly.express as px
import sys

#Set page config
st.set_page_config(page_title="Provincial Chemistry App", page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

#PATHS----------------------------------------------------------------------------------------------------------------------------
#Input_path is where the script and any input files are found, output_path is where the output files are created -the current dir.
#input_path=os.path.abspath(os.curdir)+'/Prov_chem/' #For Streamlit Directory
input_path=os.path.abspath(os.curdir) #For desktop
output_path=os.path.abspath(os.curdir)
#----------------------------------------------------------------------------------------------------------------------------------

sys.path.append(f'{input_path}/Modules') #adding the Modules directory to Python's search path at runtime.

#Setting States
if 'new_upload' not in st.session_state:
    st.session_state.new_upload=False
if 'toggleChange' not in st.session_state:
    st.session_state.toggleChange=False

if 'begin1' not in st.session_state:
    st.session_state.begin1 = False
if 'begin2' not in st.session_state:
    st.session_state.begin2 = False
if 'begin3' not in st.session_state:
    st.session_state.begin3 = False
if 'begin4' not in st.session_state:
    st.session_state.begin4 = False
if 'begin5' not in st.session_state:
    st.session_state.begin5 = False

if 'begin6' not in st.session_state:
    st.session_state.begin6 = False

if 'next1' not in st.session_state:
    st.session_state.next1 = False
if 'next2' not in st.session_state:
    st.session_state.next2 = False
if 'next3' not in st.session_state:
    st.session_state.next3 = False
if 'radio2' not in st.session_state:
    st.session_state.radio2 = False
if 'next4' not in st.session_state:
    st.session_state.next4 = False
if 'next5' not in st.session_state:
    st.session_state.next5 = False
if 'next6' not in st.session_state:
    st.session_state.next6 = False
if 'next7' not in st.session_state:
    st.session_state.next7 = False

if 'ParseNextButton' not in st.session_state:
    st.session_state.ParseNextButton = False

if 'allDone' not in st.session_state:
    st.session_state.allDone = False


#Module Imports for the different sections
import  app_setup, file_uploads, file_structure, restructure_table, headers, iso_dates, parse_dates, rvq, save_and_download, units_vmv_merge

tab1, tabStructure, tab4, tab5, tab6, tab7, tabDownload= st.tabs(['File Upload','Restructure Files', 
                                                                'Clean Headers', 'Create ISO Date-Time', 'Parse Date','Manage RVQs',
                                                                'Download Data'])

#MESSAGES
def warnings(msg):
    left, right = st.columns([0.8, 0.2])
    left.warning(f'{msg}', icon="⚠️")

def errors(msg):
    left, right = st.columns([0.8, 0.2])
    left.error(f'{msg}', icon="🚨")  

def successes(msg):
    #left, right = st.columns([0.8, 0.2])
    st.success(f'Success! {msg}', icon="✅",)

#Global variables
inconsistent_cols_error=False
date_time_error=False
cleaned_df_list=[]
supplementary_df_list=[]
placeholder=st.empty()

#PAGE & SESSION STATES SETUP
app_setup.app_intro_sidebar()#Set up APP Page and session states


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

    if st.session_state.new_upload and not datafiles:   #If an upload was done but the files are now removed
        warnings('Please Upload CSV files')

    if datafiles: #If there are files
        datafiles_dfs,csvfileNames, inconsistent_cols_error=file_uploads.read_dfs(datafiles, inconsistent_cols_error) #Read the data files as dataframes

    if inconsistent_cols_error: #inconsistent columns
        errors('Ooops, I think your file might have inconsistent columns. Each line must have the same number of columns. Please reformat your files and re-upload.')


if datafiles and inconsistent_cols_error==False: #All is good to begin cleaning!
    cleaned_df_list=datafiles_dfs
    with tabStructure:
        structure_option=file_structure.choose_file_structure_widgets() or None

        if structure_option=="merge_vmv_units":
            # STEP--- Merge VMV and UNit Rows-------------------------------------------
            #Streamlit Widget Functions -- Start of section
            vmvCode_row,units_row=units_vmv_merge.merge_rows_widget() or (None, None)

            if st.session_state.next1: #next button from the above widget function is clicked

                #Processing Functions - Pure Python
                cleaned_df_list=units_vmv_merge.merge_rows(cleaned_df_list, vmvCode_row,units_row)

                if cleaned_df_list:
                    #Streamlit Widget Functions -- End of section
                    successes("Rows have been merged and headers cleaned!") #Streamlit success message

        if structure_option=="pivot":
            # STEP--- Restructure table and Extract Variables-------------------------------------------
            #Streamlit Widget Functions -- Start of section
            var_col,value_col, additional_params=restructure_table.restructure_widgets(cleaned_df_list) or (None,None, None)

            if st.session_state.radio2 and st.session_state.next2 and st.session_state.next3:
                #Processing Functions - Pure Python
                cleaned_df_list=restructure_table.filter_df_for_each_variable(cleaned_df_list,var_col,value_col, additional_params) or None #Extract variables as their own columns and add the VMV and Variable codes to the variable names (column headers)
                
                #Streamlit Widget Functions -- End of section
                if cleaned_df_list:
                    successes("File has been restructured!") #Streamlit success message

            
    with tab4:
        # STEP 2--- Clean Headers-------------------------------------------
        #Streamlit Widget Functions -- Start of section
        headers.clean_headers_widgets()

        if st.session_state.begin3:
            #Processing Functions - Pure Python
            cleaned_df_list=headers.clean_headers(cleaned_df_list) #Remove special characters from headers

            #Streamlit Widget Functions -- End of section
            successes("Headers have been cleaned!")

    with tab5:
        #STEP 4 Convert the one dt column, or separate d & t columns to ISO-------------------------------------------
        # Streamlit Widget Functions -- Start of section      
        date_structure_radioButton=iso_dates.Choose_One_Or_Two_DateTime_Columns_Widgets() #Separate date + time cols, or just one dateTime column? Create radio buttons to get user selection (date_structure)
        
        if st.session_state.begin4:
            if date_structure_radioButton: #Don't continue unless this widget has a value from user
                date_time_col=iso_dates.one_dateTime_col_Widgets(cleaned_df_list, date_structure_radioButton) or None #widgets for allowing user to select the date-time column
                date_col, time_col=iso_dates.separate_dateTime_cols_Widgets(cleaned_df_list, date_structure_radioButton) or (None, None)#widgets for allowing user to select both date and time column 

        #Processing Functions - Pure Python
        if st.session_state.next4 == True: #If button is clicked from one_dateTime_col_Widgets:
            cleaned_df_list, date_time_error=iso_dates.convert_one_dateTime_col_to_iso(cleaned_df_list,date_time_col)# Convert dt col to ISO   

        if st.session_state.next5 == True: #If button is clicked from separate_dateTime_cols_Widgets:
            cleaned_df_list, date_time_error=iso_dates.convert_date_and_time_cols_to_iso(date_col,time_col,cleaned_df_list) # Convert both cols to ISO  

        #Streamlit Widget Functions -- End of section
        if (st.session_state.next4 or st.session_state.next5) and date_time_error==False:
            successes('Created Date-Time column in ISO format!')

    with tab6:#STEP--- #Parse ISO Date-Time column into yr, month, day, time-------------------------------------------
        
        # Streamlit Widget Functions -- Start of section
        parse_dates.parse_date_time_Widgets()

        if st.session_state.begin5:
            dt_col=parse_dates.select_date_time_column(cleaned_df_list)
        
        #Processing Functions - Pure Python
        if st.session_state.ParseNextButton:
            cleaned_df_list=df_merged=parse_dates.extract_yr_mn_day_time(cleaned_df_list, dt_col) #extract the Year, motnh, day and time

            #Streamlit Widget Functions -- End of section
            successes('Parsed the Date time column!')

    with tab7:
    #STEP--- # Result Value Qualifier (RVQ) Management-------------------------------------------
    # Streamlit Widget Functions -- Start of section
        starting_rvq_var, exceptions=rvq.choose_RVQs_Widgets(cleaned_df_list) or (None,None) #Allow users to choose starting RVQs and exceptions

        if st.session_state.next6:# Next button from choose_RVQs_Widgets was been clicked
            if starting_rvq_var != None: # A starting RVQ was selected, thus there ARE RVQ cols
                usercodes,rvqcodes=rvq.match_rvq_to_user_codes_widgets() or (None,None) #Allow user to match the User codes to rvq codes

            if st.session_state.next7 and usercodes and rvqcodes:
                #Processing Functions - Pure Python
                supplementary_df_list=rvq.save_rvq_df_as_csv(supplementary_df_list, usercodes,rvqcodes) #Create an RVQ df and save as csv                
                cleaned_df_list=rvq.add_RVQs_to_files(cleaned_df_list, starting_rvq_var, exceptions, usercodes,rvqcodes) #Add RVQ columns and codes to appropriate variable columns

                #Streamlit Widget Functions -- End of section
                successes('Added RVQs!')

    with tabDownload:
        save_and_download.download_view_widgets(cleaned_df_list)

        if st.session_state.allDone:
            save_and_download.download_output(output_path, cleaned_df_list, csvfileNames, supplementary_df_list)






    #if st.session_state.nextTask and st.session_state.next1: #Go straight to managing the date and time columns

    # STEP--- Merge VMV and UNit Rows-------------------------------------------
    #Streamlit Widget Functions -- Start of section

        # count=0
        # final_df_list=[]
        # total_dfs=len(datafiles_dfs)

        # #Loop through all the dataframes created from the files
        # for df, csv in zip(datafiles_dfs, csvfileNames): 
        #     count=count+1

        #     if count==1:
        #         units_vmv_merge.merge_rows_intro_widget()
        #         if st.session_state.clicked4:
        #             vmvCode_row,units_row=units_vmv_merge.merge_rows_widget() or (None, None)
        #     if st.session_state.clicked5:
        #         df=units_vmv_merge.merge_rows(df, vmvCode_row,units_row)
        #         st.write(df.head())

        #     # STEP 1--- Restructure table and Extract Variables-------------------------------------------
        #     #Streamlit Widget Functions -- Start of section
        #     if count==1:
        #         restructure_table.restructure_widgets()

        #     #Processing Functions - Pure Python
        #     df_merged=restructure_table.filter_df_for_each_variable(df) #Extract variables as their own columns and add the VMV and Variable codes to the variable names (column headers)
            
        #     #Streamlit Widget Functions -- End of section
        #     if count==total_dfs:
        #         successes("File has been restructured!") #Streamlit success message
        #         st.write(df_merged.head())

        #     # STEP 2--- Clean Headers-------------------------------------------
        #     #Streamlit Widget Functions -- Start of section
        #     if count==1:
        #         headers.clean_headers_widgets()

        #     #Processing Functions - Pure Python
        #     df_merged=headers.clean_headers(df_merged) #Remove special characters from headers

        #     #Streamlit Widget Functions -- End of section
        #     if count==total_dfs:
        #         successes("Headers have been cleaned!")
        #         st.write(df_merged.head())

        #     # STEP 3--- Determine if there is one col for date and time or separate columns-------------------------------------------
        #     #Streamlit Widgets
        #     if count==1:       
        #         date_structure_radioButton=iso_dates.Choose_One_Or_Two_DateTime_Columns_Widgets() #Separate date + time cols, or just one dateTime column? Create radio buttons to get user selection (date_structure)
            
        #     #STEP 4 Convert the one dt column, or separate d & t columns to ISO-------------------------------------------
        #     # Streamlit Widget Functions -- Start of section
        #         if date_structure_radioButton: #Don't continue unless this widget has a value from user
        #             date_time_col=iso_dates.one_dateTime_col_Widgets(df_merged, date_structure_radioButton) #widgets for allowing user to select the date-time column
        #             date_col, time_col=iso_dates.separate_dateTime_cols_Widgets(df_merged, date_structure_radioButton) #widgets for allowing user to select both date and time column

        #     #Processing Functions - Pure Python
        #     if st.session_state.clicked0 == True: #If button is clicked from one_dateTime_col_Widgets:
        #         df_merged=iso_dates.convert_one_dateTime_col_to_iso(df_merged,date_time_col)# Convert dt col to ISO   

        #     if st.session_state.clicked01 == True: #If button is clicked from separate_dateTime_cols_Widgets:
        #         df_merged=iso_dates.convert_date_and_time_cols_to_iso(date_col,time_col,df_merged) # Convert both cols to ISO  

        #     #Streamlit Widget Functions -- End of section
        #     if st.session_state.clicked0 or st.session_state.clicked01:
        #         if count==total_dfs:
        #             successes('Created Date-Time column in ISO format!')
        #             st.write(df_merged.head())

        #     #STEP 5--- #Parse ISO Date-Time column into yr, month, day, time-------------------------------------------
        #     # Streamlit Widget Functions -- Start of section
        #     if count==1:
        #         if st.session_state.clicked0 or st.session_state.clicked01: # Either of the next buttons button
        #             ignore=parse_dates.parse_date_time_Widgets()

        #     #Processing Functions - Pure Python
        #     if st.session_state.clicked02 == True: ## Next button from parse_date_time_Widgets was been clicked
        #         df_merged=parse_dates.extract_yr_mn_day_time(df_merged) #extract the Year, motnh, day and time
        #         df_merged=parse_dates.move_cols_to_front_of_dataframe(df_merged) #Move these extracted cols to front of the dataframe

        #     #Streamlit Widget Functions -- End of section
        #         if count==total_dfs:
        #             successes('Parsed the Date time column!')
        #             st.write(df_merged.head(5))

        #     #STEP 6--- # Result Value Qualifier (RVQ) Management-------------------------------------------
        #     # Streamlit Widget Functions -- Start of section
        #         if count==1:
        #             starting_rvq_var, exceptions=rvq.choose_RVQs_Widgets(df_merged) or (None,None) #Allow users to choose starting RVQs and exceptions
                
        #         if st.session_state.clicked2:# Next button from choose_RVQs_Widgets was been clicked
        #             if starting_rvq_var != None: # A starting RVQ was selected, thus there ARE RVQ cols
        #                 usercodes,rvqcodes=rvq.match_rvq_to_user_codes_widgets() or (None,None) #Allow user to match the User codes to rvq codes
                    
        #     #Processing Functions - Pure Python
        #             if st.session_state.clicked3:
        #                 rvqdict=rvq.create_rvq_dictionary_from_user_input(usercodes,rvqcodes) #Create an RVQ dictionary
        #                 rvq.save_rvq_dict_tocsv(rvqdict) #Save this RVQ dictionary as a CSV file e.g, 999:NC, L:BDL
        #                 vars_with_rvqs=rvq.create_list_with_potential_rvq_variables(df_merged, starting_rvq_var, exceptions) #List of all variables that should be associated with RVQs as selected by the user

        #                 #Let us loop through this varibale list and check for actual instances of user codes and get the rows
        #                 rvq_dict_per_Variable_List = [] #This will contain a list of dictionaries for each variable that has user codes in their column. E.g,  {variable: Temp; usercodes:L0.5, L8; Rows: 0,3}
        #                 for variable in vars_with_rvqs:
        #                     rvq_dict_per_Variable_List, df_merged=rvq.checkFor_UserCodes_in_RVQVariable_Columns(df_merged,usercodes,rvqcodes, variable, rvq_dict_per_Variable_List)

        #                 final_RVQ_Variable_list=rvq.filter_actual_RVQ_variables(rvq_dict_per_Variable_List) #Get the variables that actually have usercodes, these are the only ones actually associated with RVQs

        #                 #Let us create the RVQ column only for those Variables that actually have usercodes:
        #                 df_merged=rvq.create_RVQ_columns_for_Variables(rvq_dict_per_Variable_List,df_merged)
                        
        #                 final_df_list=save_and_download.save_final_dataframe(df_merged, csv, total_dfs, count, final_df_list) #Create csv file for data frame without dl still present in file
                               
        #         if st.session_state.clicked2 and starting_rvq_var == None:
        #             save_and_download.save_raw_files_if_no_rvq(df_merged,csv)# Just save the raw files with RVQ empty cols

        # if st.session_state.AllFilesProcessed:
        #     save_and_download.download_output(output_path, final_df_list)


