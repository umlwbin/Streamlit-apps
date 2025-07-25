import streamlit as st

def choose_file_structure_widgets():

    st.markdown("""
        <style>
        [role=radiogroup]{gap: 1.5rem;}
        </style>
        """,unsafe_allow_html=True)
    
    def onClick():
        st.session_state.mergeRowsBegin = False
        st.session_state.pivotBegin = False
        st.session_state.headersBegin = False
        st.session_state.isoBegin = False
        st.session_state.parseBegin = False
        st.session_state.rvqBegin = False

    st.markdown('#### 📑 Restructure Files')
    st.markdown('Provincial chemistry files can come in several formats. Choose from an option below.')
    st.info('If your files are already structured properly, and you would like to apply other cleaning steps, feel free to move on to the other tabs!', icon="ℹ️")

    st.markdown("#####")
    st.markdown('##### File Structure Options')
    st.markdown('###### Option 1 - Merge header rows')
    with st.expander("Expand for more details"):
        st.markdown('Your file has a header row, where **each variable/parameter is its own column**. The file also has one of the three:' \
        '\n - A row with **VMV codes** '
        '\n - A row with **units** '
        '\n - Two separate rows with VMV codes and Units.' \
        '\n\n You would like to restructure the file so that there is **only one header row with the VMV codes and (or) units added to the column (variable) names**.')

    st.markdown('###### Option 2 - Pivot Table')
    with st.expander("Expand for more details"):
        st.markdown('Your file has **one column with the variables/parameters** and another **column with the values** of the variables. ' \
        '\n\n You would like to pivot the table so that **each variable is its own column header**.')
   
    st.markdown('')
    structure_radio_button=st.radio("Select a format based on the descriptions above", options=['Option 1','Option 2'], captions=['Merge header rows','Pivot table'], 
                                        horizontal=True, index=None, on_change=onClick)
    

    if structure_radio_button:
        if structure_radio_button=='Option 1':
            return "merge_vmv_units"
        else:
            return "pivot"