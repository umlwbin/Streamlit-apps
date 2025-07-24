import streamlit as st
import pandas as pd
import re


def merge_rows_widget():
    st.markdown('#####')
    st.markdown('##### 🗒️ Merging Units and VMV codes to headers')
    st.markdown(' This step cleans  provincial file that contains one row of units and one row of VMV codes. ' \
    'It merges the codes and units to the column headers and also cleans the headers '
    '(removes special characters and spaces).' )

    def click_Begin_button():
        st.session_state.mergeRowsBegin = True
    st.button("Let's Go!", type="primary", key='Begin_Button1', on_click=click_Begin_button)

    if st.session_state.mergeRowsBegin:
        #Setting States
        if 'mergeRowsNext1' not in st.session_state:
            st.session_state.mergeRowsNext1 = False

        # If the button is clicked, the session state is set to true (button is clicked)
        def click_button():
            st.session_state.mergeRowsNext1 = True

        # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
        def change_vars():
            st.session_state.mergeRowsNext1 = False
            st.session_state.allDone=False

        st.markdown('#####')
        st.markdown('##### Choose the rows that contains the Valid Method Variable (VMV) code and the variable units')
        col1,col2, col3=st.columns(3, vertical_alignment='bottom')
        vmvCode_row = col1.selectbox(label='Select the VMV code row',options=['0', '1'],index=0, key='select1', on_change=change_vars)
        units_row = col2.selectbox(label='Select the Units row',options=['0', '1'],index=1,key='select2', on_change=change_vars)
      
        #Next button
        col3.button("Next", type="primary", key='Next_Button5', on_click=click_button)

        if st.session_state.mergeRowsNext1:
            return vmvCode_row,units_row
       

def merge_rows(cleaned_df_list, vmvCode_row,units_row):
    temp_workin_list=[]
    for df in cleaned_df_list:
        # This function merges the user defined rows containing units and VMV codes
        headers=list(df.columns) #get the headers
        units=list(df.iloc[int(units_row)]) #Get the units row
        codes=list(df.iloc[int(vmvCode_row)]) #Get the units row

        # Ensure there are no spaces or brackets in header name
        headers_list=[]
        pattern = r'[^A-Za-z0-9]'
        for header, code, unit in zip(headers, codes, units):
            
            # Merging the nvm code and units
            if pd.isna(code)==False:
                header=header+'_'+str(code)+'_'+str(unit)
            
            #Clean current headers
            header=header.strip() # Remove trailing white space
            header=re.sub(pattern, '_', header)

            # Collapse multiple underscores into one
            header = re.sub(r'_+', '_', header)
            
            # Remove trailing underscore if any
            if header.endswith('_'):
                header = header[:-1]           

            headers_list.append(header) #append to final header list

        #Save updated column headers to data frame
        df.columns=headers_list
        df=df.tail(-2)

        temp_workin_list.append(df) #update the list for this processing
    
    cleaned_df_list=temp_workin_list

    return cleaned_df_list
    