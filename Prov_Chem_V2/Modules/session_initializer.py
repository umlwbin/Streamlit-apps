import streamlit as st


def init_session_state():
    #Setting States
    if 'cleaned_df_list' not in st.session_state:
        st.session_state.cleaned_df_list=[]

    if "df_history" not in st.session_state:
        st.session_state.df_history = []

    if "redo_stack" not in st.session_state:
        st.session_state.redo_stack = []


    if 'new_upload' not in st.session_state:
        st.session_state.new_upload=False
    if 'toggleChange' not in st.session_state:
        st.session_state.toggleChange=False

    if 'mergeRowsBegin' not in st.session_state:
        st.session_state.mergeRowsBegin = False
    if 'pivotBegin' not in st.session_state:
        st.session_state.pivotBegin = False
    if 'headersBegin' not in st.session_state:
        st.session_state.headersBegin = False
    if 'isoBegin' not in st.session_state:
        st.session_state.isoBegin = False
    if 'parseBegin' not in st.session_state:
        st.session_state.parseBegin = False
    if 'rvqBegin' not in st.session_state:
        st.session_state.rvqBegin = False

    if 'mergeRowsNext1' not in st.session_state:
        st.session_state.mergeRowsNext1 = False
    if 'PivotNext1' not in st.session_state:
        st.session_state.PivotNext1 = False
    if 'PivotNext2' not in st.session_state:
        st.session_state.PivotNext2 = False
    if 'pivotRadio1' not in st.session_state:
        st.session_state.pivotRadio1 = False

    if 'isoNext1' not in st.session_state:
        st.session_state.isoNext1 = False
    if 'isoNext2' not in st.session_state:
        st.session_state.isoNext2 = False

    if 'parseNext1' not in st.session_state:
        st.session_state.parseNext1 = False

    if 'rvqNext1' not in st.session_state:
        st.session_state.rvqNext1 = False
    if 'rvqNext2' not in st.session_state:
        st.session_state.rvqNext2 = False

    if 'allDone' not in st.session_state:
        st.session_state.allDone = False