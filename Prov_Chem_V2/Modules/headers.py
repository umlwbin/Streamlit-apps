import streamlit as st
import re
import copy

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
    # Create a deep copy of the current list in session state. We will work on this copy
    cleaned_df_list=copy.deepcopy(st.session_state.cleaned_df_list)

    # Push current version to history before makign any changes
    st.session_state.df_history.append(copy.deepcopy(st.session_state.cleaned_df_list))

    # Clear redo stack since we are making a new change
    st.session_state.redo_stack.clear()

    for df in cleaned_df_list:
        # CLEAN the headers and update the merged data frame
        headers=df.columns         
        headers_list=[]
        
        chars_to_keep = "µ" # Characters to explicitly keep
        # Escape characters in chars_to_keep for safe use in regex
        escaped_chars_to_keep = re.escape(chars_to_keep)
        pattern = rf"[^A-Za-z0-9\s{escaped_chars_to_keep}]"        

        for header in list(headers): 
            header=header.strip() # Remove trailing white space
            header=re.sub(pattern, '_', header)

            # Collapse multiple underscores into one
            header = re.sub(r'_+', '_', header)
            
            #if header has extra _ at end
            if header.endswith('_'):
                header = header[:-1]

            #Append to final header list
            headers_list.append(header) 
        
        #Save updated column headers to data frame
        df.columns=headers_list
        
    #Update the cleaned list in session state
    st.session_state.cleaned_df_list=cleaned_df_list
