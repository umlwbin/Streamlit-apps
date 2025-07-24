import streamlit as st
import re

def clean_headers_widgets():
    st.markdown('#### 🧹 Cleaning Headers ')
    st.markdown('This step removes special characters and extra spaces from column headers, making them database-compatible.')

    def click_Begin_button():
        st.session_state.headersBegin = True

        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.mergeRowsNext1 = st.session_state.PivotNext1 = st.session_state.PivotNext2 = st.session_state.isoNext1 = st.session_state.isoNext2 = st.session_state.parseNext1 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone = False  


        st.session_state.allDone=False
    st.button("Let's Go!", type="primary", key='Begin_Button3', on_click=click_Begin_button)


def clean_headers(cleaned_df_list):
    temp_workin_list=[]
    for df in cleaned_df_list:
        # CLEAN the headers and update the merged data frame
        headers=df.columns         
        headers_list=[]
        pattern = r'[^A-Za-z0-9]'
        for header in list(headers): 
            header=header.strip() # Remove trailing white space
            header=re.sub(pattern, '_', header)

            # Collapse multiple underscores into one
            header = re.sub(r'_+', '_', header)

            if header.endswith('_'):
                header = header[:-1]

            headers_list.append(header) #append to final header list
        
        #Save updated column headers to data frame
        df.columns=headers_list
        temp_workin_list.append(df)

    cleaned_df_list=temp_workin_list
    return cleaned_df_list