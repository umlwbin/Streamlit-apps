import streamlit as st
import pandas as pd
import re


def clean_headers(df,):

    cols=list(df.columns)

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Cleaning headers...')
    st.markdown('')

    #PROCESSING************************************************************************ 
    cleaned_headers=[]
    chars_to_keep = "µ" # Characters to explicitly keep
    # Escape characters in chars_to_keep for safe use in regex
    escaped_chars_to_keep = re.escape(chars_to_keep)
    pattern = rf"[^A-Za-z0-9\s{escaped_chars_to_keep}]"        

    # 1. GET A LIST OF CLEANED HEADERS
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


    # 2. PROCESS 
    df = df.dropna(axis=1, how='all')# Remove columns where all values are NaN
    df.columns=list(cleaned_headers) #add new headers


    if cleaned_headers==cols:
        st.success('These column headers already look pretty clean to me!',icon='✅')

    return df