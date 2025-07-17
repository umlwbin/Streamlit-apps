import streamlit as st


#Setting States
if 'new_upload' not in st.session_state:
    st.session_state.new_upload=False
if 'toggleChange' not in st.session_state:
    st.session_state.toggleChange=False

if 'mergeRowsBegin' not in st.session_state:
    st.session_state.mergeRowsBegin = False
    
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