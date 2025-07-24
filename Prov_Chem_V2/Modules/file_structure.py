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
   
    structure_radio_button=st.radio("Select a format", options=['Your file has a **header row**, as well as a row with **either VMV codes** or **units** (**or two separate rows with VMV codes and Units**). You would like to restructure the file so that there is only one header row with the VMV codes and (or) units added to the column names.',
                                        'Your file has a **column** with the variables/parameters and another **column** with the values of the variables. You would like to pivot the table so that each variable is its own column header.'], 
                                        horizontal=True, index=None, label_visibility="hidden", on_change=onClick)
    

    if structure_radio_button:
        if structure_radio_button=='Your file has a **header row**, as well as a row with **either VMV codes** or **units** (**or two separate rows with VMV codes and Units**). You would like to restructure the file so that there is only one header row with the VMV codes and (or) units added to the column names.':
            return "merge_vmv_units"
        else:
            return "pivot"