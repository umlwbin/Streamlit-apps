import streamlit as st
import os
import sys

#Output Path
path=os.path.abspath(os.curdir)
#Add Modules
sys.path.append(f'{path}/Modules')
#Module Imports for the different sections
import  session_initializer, add_columns,reorder_variables,remove_columns, merge_files, headers, rename,merge_date_time, iso, parse_dates, tidy_data, pivot_data, assign_dataType 


def define_task_functions():
    TASKS = {
        "Tidy Data Checker": {"type": "single", "func": tidy_data.basic_cleaning},
        "Add columns": {"type": "single", "func": add_columns.add_cols},
        "Reorder columns": {"type": "single", "func": reorder_variables.reorder},
        "Remove columns": {"type": "single", "func": remove_columns.remove_cols},
        "Merge All Files": {"type": "multi", "func": merge_files.merge},
        "Clean column headers": {"type": "single", "func": headers.clean_headers},
        "Rename columns": {"type": "single", "func": rename.rename_cols},
        "Merge date and time columns": {"type": "single", "func": merge_date_time.merge},
        "Convert DateTime column to ISO format": {"type": "single", "func": iso.convert_func},
        "Parse Date": {"type": "single", "func": parse_dates.parse_func},
        "Transpose Data": {"type": "single", "func": pivot_data.pivot},
        "Assign Data Type": {"type": "single", "func": assign_dataType.assign},
        
    }

    return TASKS



def what_to_do_widgets():
    
    # INTRO WIDGETS---------------------------------------------
    st.markdown('#### What would you like to do? 🤔')

    # WIDGET INTERACTIONS----------------------------------------------------
    def click_Rbutton():

        st.session_state.selected_task = task
        session_initializer.reset_widget_flags() #Reset all the next buttons that are not directly widgetkeys. 

    # WIDGET CREATION --------------------------------------------
    task=st.radio('Select an action',['Tidy Data Checker','Reorder columns','Add columns', 'Remove columns', 'Merge multiple files', 'Clean column headers',
                                                'Rename columns','Merge date and time columns', 'Convert DateTime column to ISO format', 'Parse Date', 'Transpose Data', 'Assign Data Type'],
                                                captions=['Please use this checker for key cleaning steps. It removes empty rows and cols, standardizes NaNs, and cleans column headers.',
                                                          '','','','','Remove spaces and special characters',' Standardize those column names!','','YYYY-MM-DDTHH:MM:SS', 'Parse one ISO date-time column into Y-m-d and Time','Flip your data!', 'Assign data types to **columns**'], 
                                                index=None,on_change=click_Rbutton, key='RadioKey')
    
    return task


