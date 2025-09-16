import streamlit as st
import pandas as pd


def merge_widgets():

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### You have multiple files, let\'s merge them!')

    if len(st.session_state.current_data.keys())==1:
        left, right = st.columns([0.8,0.2])
        left.info('There is only one file uploaded so no work for us! 😌', icon='ℹ️')

    else:
        
        # WIDGET CREATION --------------------------------------------   
        #Next Button
        st.button("Let's Go", type="primary", key='mergeContinue') 

        #IF NEXT BUTTON IS CLICKED
        if st.session_state.get("mergeContinue"): 
            task_inputs = {}              
            return task_inputs  


def merge(dfs_dict):
    
    #PROCESSING************************************************************************
    # Concatenate all DataFrames vertically
    merged_df = pd.concat(dfs_dict.values(), ignore_index=True)
    return merged_df
