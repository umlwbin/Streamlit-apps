import streamlit as st
import pandas as pd


def merge(dfs_dict):

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Merging all your files')

    if len(dfs_dict)==1:
        left, right = st.columns([0.8,0.2])
        left.info('There is only one file uploaded so no work for us! 😌', icon='ℹ️')

    #PROCESSING************************************************************************
    # Concatenate all DataFrames vertically
    merged_df = pd.concat(dfs_dict.values(), ignore_index=True)
    return merged_df
