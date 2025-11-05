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
import  session_initializer, sidebar_intro, toggle, what_to_do

# Initialize Session States
session_initializer.init_session_state()

#Set Up the Sidebar
sidebar_intro.sidebar()

#=========================================BEGIN WORKFLOW==========================================
# 1. WHAT DOES THE USER NEED TO DO? --------------------------------------------------------------
# Get the radio button option from user that asks them what task they would like ot perform, reorder, rename, merge etc
# The toggle when activated keeps processing the same files. 
radiobutton, tog = what_to_do.what_to_do_widgets()

# 2. CALL APPROPRIATE FUNCTIONS DEPENDING ON TOGGLE AND RADIO BUTTONS ------------------------------
# 2.1 Toggle is turned on --------------------------------------------------------------------------
if tog:
    left, right = st.columns([0.6, 0.4])
    left.info('Working on the same file! Select an action above.', icon="ℹ️",)

    # 2.11 Toggle is on and files have already been processed at least once -----------
    if st.session_state.version>=1 and st.session_state.firstRun==False: #The version gets updated after each Next button. The first run will be false after the first download fucntion
        
        #Get the files that have been processed already (temp files) and the associated columns (temp cols). These will now be the input files.
        tempfiles, tempcols=toggle.grab_already_curated_files()
        if tempfiles:
            # Go to the processing function directly
            toggle.call_processing_function_old_data(radiobutton, tempfiles, tempcols)

    # 2. 12 Toggle is on, but we havent processed any files yet, we still need to use the uploader. -------
    else:
        toggle.call_processing_function_new_data(radiobutton)

# 2.2 Toggle is turned off - NEW DATA so we need to use uploader------------------------------------------
else: 
    left, right = st.columns([0.6, 0.4])
    left.info('To continue processing the same files, activate the switch above!', icon="ℹ️",)
    toggle.call_processing_function_new_data(radiobutton)
