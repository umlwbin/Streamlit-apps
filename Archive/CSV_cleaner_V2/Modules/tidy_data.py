import streamlit as st
import pandas as pd
import os
import sys
import numpy as np
import re

#Output Path
path=os.path.abspath(os.curdir)
sys.path.append(f'{path}/Modules')

#Module Imports for the different sections
import readFiles, save_files, download


def file_cleanup(datafiles,cols):
    
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### File Cleanup 🗒️ ')

    with st.container(border=True):
        st.markdown('##### Nan Check')
        st.markdown('')
        st.markdown('Are there any Nan representations in your file(s) that are not in the following list?')
        st.markdown('**NA**, **?**, **N/A**, **" "**, **np.nan**, **None**, **Nan**, **NaN**')
        st.markdown('If yes, enter the Nan representation(s) below. **Click Add** after each entry.')
        st.markdown('When you are finished, or **if you have nothing to enter**, click **Continue**.')
        
    # WIDGET INTERACTIONS----------------------------------------------------
        def changeEntry():
            st.session_state.cleanupContinue=False

        def click_button():
            st.session_state.cleanupContinue=True
            st.session_state.version=st.session_state.version+1 #update the version

    # WIDGET CREATION ---------------------------------------------------------------       
        # Widget for user to enter NAN
        nans=[]
        left, middle1,right = st.columns([2,2,6],vertical_alignment='bottom')
        user_nan=left.text_input('Enter',label_visibility='hidden', on_change=changeEntry)
        
        #ADD Button
        if middle1.button("Add Entry"):#If Add button is pressed, add the Nan entered by user
            nans.append(user_nan) #Add user nan to list
            st.markdown(f'{user_nan} was added to list')
        
        #CONTINUE Button
        continue_button=right.button("Continue",on_click=click_button,type='primary')

    if st.session_state.cleanupContinue:
        # LOOP THROUGH FILES------------------------------------------------  
        df_list=[]
        emptyCols=0 #Keeping track of the files with empty cols
        emptyRows=0 #Keeping track of the files with empty rows
        
        for file in datafiles:
            #PROCESSING************************************************************************ 
            # 1. READ FILE 
            df=readFiles.read_datafiles(file)

            # 2. PROCESS
            # 2.1 Empty Columns======
            empty_cols = [col for col in df.columns if df[col].isnull().all()]

            if len(empty_cols)>0:
                df.drop(empty_cols, axis=1, inplace=True)#remove empty cols
                cols=list(df.columns) #update the cols
                emptyCols=emptyCols+1

            # 2.2 Empty Rows======
            empty_rows= df[df.isna().all(axis=1)]
            if not empty_rows.empty:
                emptyRows=emptyRows+1
            # Remove empty rows
            df = df.dropna(how='all')

            # 2.3 Checking Nans======
            # Identify different NaN representations
            na_values = ['NA', '?', 'N/A', '', np.nan, None, 'Nan', 'NaN']
            if nans:
                na_values.extend(nans) #Add the user provided nans
            
            # Replace all identified NaN values with empty strings
            df = df.replace(na_values, '')
        
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

            if cleaned_headers==cols:
                headers_already_clean=True
            else:
                headers_already_clean=False
                headers_list.append(headers_already_clean)
                
            # 3. CREATE CSV FILE
            df_list=save_files.create_csv_files(file, df, df_list)

        #Display chamges made -------------------------------------------- 
        st.markdown('######')
        if emptyCols>0:
            st. markdown(f'✅ There were empty columns found in one or more files that were removed')
        else:
            st. markdown(f'✅ There were no empty columns found 🥳')


        if emptyRows>0:
            st. markdown(f'✅ There were empty rows found in one or more files that were removed')
        else:
            st. markdown(f'✅ There were no empty rows found 🥳')

        st.markdown(f'✅ All NaNs were converted to blank spaces 🥳')

        if headers_list:
            st.markdown('✅ Column headers with special characters or extra spaces were found and corrected')
        else:
            st.markdown('✅ Your column headers were pretty clean 🥳')
    

        #SHOW SNAPSHOT OF PROCESSES FILES-----------------------------------------------------------------------------------------------------------
        save_files.show_snapshot(df_list)

        # CALL DOWNLOAD FUNCTION---------------------------------------------------------
        download.download_output(df_list)   

