import streamlit as st
import sys
import os

#Output Path
path=os.path.abspath(os.curdir)

#Add Modules
sys.path.append(f'{path}/Modules') #adding the Modules directory to Python's search path at runtime.

#Module Imports for the different sections
import  file_uploads, reorder_variables, add_columns, remove_columns, merge_files, headers, rename, merge_date_time, iso, tidy_data


def call_processing_function_old_data(radiobutton, tempfiles, tempcols):

    if radiobutton is not None:
        st.markdown('-------------')
        st.markdown(f'### {radiobutton}')
        st.markdown(' ')

    if radiobutton=='Reorder columns':
        reorder_variables.reorder(tempfiles,tempcols)
        
    if radiobutton=='Add columns':
        add_columns.how_many_vars_widget(tempfiles, tempcols)
        
    if radiobutton=='Remove columns':
        remove_columns.which_cols(tempfiles, tempcols)

    if radiobutton=='Merge multiple files':
        merge_files.merge(tempfiles, tempcols)

    if radiobutton=='Clean column headers':
        headers.clean_headers(tempfiles, tempcols)

    if radiobutton=='Rename columns':
        rename.rename_headers(tempfiles, tempcols)

    if radiobutton=='Merge date and time columns':
        merge_date_time.mergedate_time(tempfiles, tempcols)
            
    if radiobutton=='Convert DateTime column to ISO format':
        iso.convert_dateTime(tempfiles, tempcols)

    if radiobutton=='Tidy Data Checker':
        tidy_data.file_cleanup(tempfiles,tempcols)

def call_processing_function_new_data(radiobutton):
    if radiobutton is not None:
        st.markdown('-------------')
        st.markdown(f'### {radiobutton}')
        st.markdown(' ')

    if radiobutton=='Reorder columns':
        datafiles, cols, func=datafiles, cols, func=file_uploads.fileuploadfunc(reorder_variables.reorder) 
        
    if radiobutton=='Add columns':
        datafiles, cols, func=file_uploads.fileuploadfunc(add_columns.how_many_vars_widget)
        
    if radiobutton=='Remove columns':
        datafiles, cols, func=file_uploads.fileuploadfunc(remove_columns.which_cols)

    if radiobutton=='Merge multiple files':
        datafiles, cols, func=file_uploads.fileuploadfunc(merge_files.merge)

    if radiobutton=='Clean column headers':
        datafiles, cols, func=file_uploads.fileuploadfunc(headers.clean_headers)

    if radiobutton=='Rename columns':
        datafiles, cols, func=file_uploads.fileuploadfunc(rename.rename_headers)

    if radiobutton=='Merge date and time columns':
        datafiles, cols, func=file_uploads.fileuploadfunc(merge_date_time.mergedate_time)
            
    if radiobutton=='Convert DateTime column to ISO format':
        datafiles, cols, func=file_uploads.fileuploadfunc(iso.convert_dateTime)

    if radiobutton=='Tidy Data Checker':
        datafiles, cols, func=file_uploads.fileuploadfunc(tidy_data.file_cleanup)

    if radiobutton and datafiles:
        #CALL CORE PROCESSING FUNCTION-----------------------
        func(datafiles, cols)

