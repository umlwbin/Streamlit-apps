import streamlit as st
import pandas as pd
import os
import sys

#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

#Output Path
path=os.path.abspath(os.curdir)

#Add Modules
sys.path.append(f'{path}/Modules') #adding the Modules directory to Python's search path at runtime.

#Module Imports for the different sections
import  session_initializer, sidebar_intro, toggle

# Initialize Session States
session_initializer.init_session_state()

#Set Up the Sidebar
sidebar_intro.sidebar()

#=========================================BEGIN WORKFLOW====================================================

# INTRO WIDGETS---------------------------------------------
st.markdown('#### What would you like to do? 🤔')

# WIDGET INTERACTIONS----------------------------------------------------
def click_Rbutton():
    # Set all next buttons to false when the radio btton selection changes
    st.session_state.reorderNext = False
    st.session_state.addColsNext1 = False
    st.session_state.addColsNext2 = False 
    st.session_state.removeColsNext = False
    st.session_state.renameNext = False
    st.session_state.mergeDateNext = False
    st.session_state.convertISONext1 = False

def onToggle():
    if tog: # if it is ON, and then you switch it off, 'if tog' will be true
        st.session_state.toggle = False # If it is switched off On-->Off
    else:
        st.session_state.toggle = True #if it is switched on
    st.session_state.reorderNext = False
    st.session_state.addColsNext1 = False
    st.session_state.addColsNext2 = False #This ensures they have to press that last next button again, otherwise it would go straight to downloads. 
    st.session_state.removeColsNext = False
    st.session_state.renameNext = False
    st.session_state.mergeDateNext = False
    st.session_state.convertISONext1 = False

# WIDGET CREATION --------------------------------------------
radiobutton=st.radio('Select an action',['Tidy Data Checker','Reorder columns','Add columns', 'Remove columns', 'Merge multiple files', 'Clean column headers',
                                            'Rename columns','Merge date and time columns', 'Convert DateTime column to ISO format'],
                                            captions=['Please use this checker for key cleaning steps. It removes empty rows and cols, standardizes NaNs, and cleans column headers.','','','','','Remove spaces and special characters', '','',''], 
                                            index=None,on_change=click_Rbutton, key='RadioKey')

#Toggle button - Keep curating same files. Default - ON
st. markdown('')
tog=st.toggle("**Activate switch to use the same dataset**",on_change=onToggle,key='toggleSwitch', value=True)


# CALL FUNCTIONS DEPENDING ON TOGGLE AND RADIO BUTTONS ---------------------------------------------

# Toggle is turned on ---------------------------------------------
if tog:
    left, right = st.columns([0.6, 0.4])
    left.info('Working on the same file! Select an action above.', icon="ℹ️",)

    # *****Files have already been processed at least once*****
    if st.session_state.version>=1 and st.session_state.firstRun==False: #The version gets updated after each Next button. The first run will be false after the first download fucntion
        
        # Grab the already curated files
        _, _, files = next(os.walk(path))
        tempfiles=[f for f in files if '_cwout' in f]

        if tempfiles:
            # Get the cols again since we wont do the upload func, and the cols may have changed
            tempfile=tempfiles[0]
            df=pd.read_csv(tempfile, nrows=1) # just get a row
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            tempcols= list(df.columns)

            # Go to that processing function directly
            toggle.call_processing_function_old_data(radiobutton, tempfiles, tempcols)

    #****Toggle is on, but we havent processed any files yet, we still need to use the uplaoder.*****
    else:
        toggle.call_processing_function_new_data(radiobutton)


# Toggle is turned off - NEW DATA---------------------------------------------
else: 
    left, right = st.columns([0.6, 0.4])
    left.info('To continue processing the same files, activate the switch above!', icon="ℹ️",)
    toggle.call_processing_function_new_data(radiobutton)
