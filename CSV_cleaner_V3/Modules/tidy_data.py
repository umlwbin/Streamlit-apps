import streamlit as st

import numpy as np
import re

def file_cleanup_widgets(cols):
    
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### File Cleanup 🗒️ ')

    with st.container(border=True):
        st.markdown('##### Nan Check')
        st.markdown('')
        st.markdown('Are there any Nan representations in your file(s) that are not in the following list?')
        st.markdown('**NA**, **?**, **N/A**, **" "**, **np.nan**, **None**, **Nan**, **NaN**')
        st.markdown('If yes, enter the Nan representation(s) below. **Click Add** after each entry.')
        st.markdown('When you are finished, or **if you have nothing to enter**, click **Continue**.')
        
    # # WIDGET INTERACTIONS----------------------------------------------------
    #     def changeEntry():
    #         st.session_state.cleanupContinue=False

    #     def click_button():
    #         st.session_state.cleanupContinue=True

    # WIDGET CREATION ---------------------------------------------------------------       
        # Widget for user to enter NAN
        nans=[]
        left, middle1,right = st.columns([2,2,6],vertical_alignment='bottom')
        user_nans=left.text_input('Enter',label_visibility='hidden')
        
        #ADD Button
        if middle1.button("Add Entry"):#If Add button is pressed, add the Nan entered by user
            nans.append(user_nans) #Add user nan to list
            st.markdown(f'{user_nans} was added to list')
        
        #CONTINUE Button
        right.button("Continue", type='primary', key="cleanupContinue")

    if st.session_state.get("cleanupContinue"):
        task_inputs = {"nans": nans}                  
        return task_inputs


def basic_cleaning(df,nans):
    cols=list(df.columns)
    summary = {}

    #PROCESSING************************************************************************ 

    # 1 Empty Columns Check======
    empty_cols = [col for col in df.columns if df[col].isnull().all()]

    if len(empty_cols)>0:
        df.drop(empty_cols, axis=1, inplace=True) # remove empty cols
        cols=list(df.columns)                    # update the cols
        
        summary["empty_columns_removed"] = empty_cols # Update Summary


    # 2 Empty Rows Check======
    empty_rows= df[df.isna().all(axis=1)]
    if not empty_rows.empty:
        emptyRows=emptyRows+1
   
    df = df.dropna(how='all')  # Remove empty rows
    summary["empty_rows_removed"] = len(empty_rows) # Update Summary

    # 2.3 Checking Nans======
    # Identify different NaN representations
    na_values = ['NA', '?', 'N/A', '', np.nan, None, 'Nan', 'NaN']
    if nans:
        na_values.extend(nans) #Add the user provided nans

    #Before replacements
    df_original = df.copy()
    
    # Replace all identified NaN values with empty strings
    df = df.replace(na_values, '')
    nan_count=(df_original != df).sum().sum()
    summary["nans_replaced"] = nan_count

    # 2.4 Cleaning headers======
    headers_list=[]
    cleaned_headers=[]

    chars_to_keep = "µ" # Characters to explicitly keep
    # Escape characters in chars_to_keep for safe use in regex
    escaped_chars_to_keep = re.escape(chars_to_keep)
    pattern = rf"[^A-Za-z0-9\s{escaped_chars_to_keep}]"        

    for header in cols: 
        header=header.strip() # Remove trailing white space
        header=re.sub(pattern, '_', header)

        # Collapse multiple underscores into one
        header = re.sub(r'_+', '_', header)
        
        #if header has extra _ at end
        if header.endswith('_'):
            header = header[:-1]

        #Append to final header list
        cleaned_headers.append(header)

    # Add new headers to DF
    df.columns=list(cleaned_headers)
    summary["columns_cleaned"] = cols != df.columns.tolist()

    return df, summary
