import streamlit as st


def init_session_state():
    if 'new_upload' not in st.session_state:
        st.session_state.new_upload=False
        
    if 'toggle' not in st.session_state:
        st.session_state.toggle=True
        st.session_state.version=0 #This is updated after each next button is pressed for each function
        st.session_state.firstRun=True #This is turned on when the download function is called.

    if 'processedFiles' not in st.session_state:
        st.session_state.processedFiles=False

    if 'reorderNext' not in st.session_state:
        st.session_state.reorderNext = False

    if 'addColsNext1' not in st.session_state:
        st.session_state.addColsNext1 = False

    if 'addColsNext2' not in st.session_state:
        st.session_state.addColsNext2 = False

    if 'removeColsNext' not in st.session_state:
        st.session_state.removeColsNext = False

    if 'renameNext' not in st.session_state:
        st.session_state.renameNext = False

    if 'mergeDateNext' not in st.session_state:
        st.session_state.mergeDateNext = False

    if 'convertISONext1' not in st.session_state:
        st.session_state.convertISONext1 = False

    if 'cleanupContinue' not in st.session_state:
        st.session_state.cleanupContinue = False
