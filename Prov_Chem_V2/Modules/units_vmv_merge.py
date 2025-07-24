import streamlit as st
import pandas as pd
import re


def merge_rows_widget(cleaned_df_list):
    st.markdown('#####')
    st.markdown('##### 🗒️ Merging Units and VMV codes to headers')
    st.markdown(' This step cleans  provincial file that contains one row of units and (or) one row of VMV codes. ' \
    'It merges the codes and units to the column headers and also cleans the headers '
    '(removes special characters and spaces).' )

    def click_Begin_button():
        st.session_state.mergeRowsBegin = True
        st.session_state.mergeRowsNext1 = False

        # Turn off all other Begin button sessions states
        st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.PivotNext1 = st.session_state.PivotNext2 = st.session_state.isoNext1 = st.session_state.isoNext2 = st.session_state.parseNext1 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone =False


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
        vmvCode_row = col1.selectbox(label='Select the VMV code row',options=['0', '1','2', 'No VMV row'],index=3, key='select1', on_change=change_vars)
        units_row = col2.selectbox(label='Select the Units row',options=['0', '1','2', 'No Units row'],index=3,key='select2', on_change=change_vars)

        if vmvCode_row !="No VMV row":
            st.markdown(' ')
            st.markdown(f'**This is the VMV row you have chosen (row {vmvCode_row}). Click Next to continue.**')
            st.dataframe(cleaned_df_list[0].iloc[[int(vmvCode_row)]])
        else:
            vmvCode_row=None #Set to None if there is no row


        if units_row !="No Units row":
            st.markdown(' ')
            st.markdown(f'**This is the Units row you have chosen (row {units_row}). Click Next to continue.**')
            st.dataframe(cleaned_df_list[0].iloc[[int(units_row)]])
        else:
            units_row=None

        #Next button
        col3.button("Next", type="primary", key='Next_Button5', on_click=click_button)

        if st.session_state.mergeRowsNext1:
            return vmvCode_row,units_row
       

def merge_rows(cleaned_df_list, vmvCode_row,units_row, just_cleaned_headers_flag):
    temp_workin_list=[]
    just_cleaned_headers_flag=False
    headers_are_the_same=False
    for df in cleaned_df_list:
        # This function merges the user defined rows containing units and VMV codes
        headers=list(df.columns) #get the original headers
        headers_with_vmvCodes=[]
        headers_with_units=[]
        headers_list_final=[]

        # Merging the nvm code and units------------------------------
        if vmvCode_row!=None: #If there was a vmv code row
            codes=list(df.iloc[int(vmvCode_row)]) #Get the row of data

            for header, code in zip(headers, codes):                   
                if pd.isna(code)==False:# Merging if not NAN
                    if ("VMV" not in str(code)) and ('vmv' not in str(code)):# Merging if VMV is not in the string in a cell in that row
                        header=header+'_'+str(code)
                headers_with_vmvCodes.append(header)

        if units_row!=None: #If there was a unit row
            units=list(df.iloc[int(units_row)]) #Get the row of data

            #if the headers with vmv codes is empty, then just add to original headers, otherwise, add to the headers with vmv codes
            if headers_with_vmvCodes==[]:
                headers2=headers
            else:
                headers2=headers_with_vmvCodes

            for header, unit in zip(headers2, units):                   
                if pd.isna(unit)==False: # Merging if not NAN
                    if "Unit" not in str(unit) and 'unit' not in str(unit) and 'UNIT' not in str(unit):# Merging if 'Unit' is not in the string in a cell in that row
                        header=header+'_'+str(unit)
                headers_with_units.append(header)

        if vmvCode_row==None and units_row==None:
            st.warning('No VMV code or Units row selected! BUT we cleaned your headers anyway! ☺️', icon="⚠️" )
            just_cleaned_headers_flag=True
        
     
        #Now that they have been added, clean up headers
        #Depending on what has been added to the headers:
        if vmvCode_row !=None and units_row==None:
            headers_before_cleaning=headers_with_vmvCodes
        elif vmvCode_row ==None and units_row!=None:
            headers_before_cleaning=headers_with_units
        elif vmvCode_row !=None and units_row!=None:
            headers_before_cleaning=headers_with_units
        elif vmvCode_row ==None and units_row==None:
            headers_before_cleaning=headers #original list


        pattern = r'[^A-Za-z0-9]'
        for header in headers_before_cleaning:

            header=header.strip() # Remove trailing white space
            header=re.sub(pattern, '_', header) # Remove special characters
            header = re.sub(r'_+', '_', header) # Collapse multiple underscores into one
            
            # Remove trailing underscore if any
            if header.endswith('_'):
                header = header[:-1]           

            headers_list_final.append(header) #append to final header list

        #Save updated column headers to data frame
        df.columns=headers_list_final
        df=df.tail(-2)

        #Reset Index
        df.reset_index(drop=True, inplace=True)

        #update the processed temp list
        temp_workin_list.append(df) 
    
    #Headers are the same (no cleanign needed)
    if list(cleaned_df_list[0].columns)==list(temp_workin_list[0].columns):
        headers_are_the_same=True
        
    #Update the cleaned list
    cleaned_df_list=temp_workin_list

    return cleaned_df_list, just_cleaned_headers_flag, headers_are_the_same
    