import streamlit as st


def init_session_state():

    default_values={
        "original_data": {}, # filename → original df
        "current_data": {},  # key: filename, value: cleaned DataFrame
        "task_history":{},
        "history_stack":{}, # history_stack: stores previous versions (for undo)
        "redo_stack":{}, # redo_stack: stores undone versions (for redo)
        'uploaded_files':[],
        'selected_types' : {},
        #"selected_task":None,

        #'new_upload': False,
        'files_processed':False,
        #'reorderNext':False,
        'addColsNext1':False,
        #'addColsNext2':False,
        'removeColsNext':False,        
        'renameNext':False,
        'mergeDateNext':False,
        'convertISONext1':False,
        'cleanupContinue':False,
        'ParseNext1':False 
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_widget_flags():
    for key in st.session_state.keys():
        if "Next" in key and "WidgetKey" not in key:
            st.session_state[key] = False
