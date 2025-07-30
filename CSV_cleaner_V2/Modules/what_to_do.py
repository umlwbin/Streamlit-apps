import streamlit as st
import os

#Output Path
path=os.path.abspath(os.curdir)

def what_to_do_widgets():
    
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


    return radiobutton, tog