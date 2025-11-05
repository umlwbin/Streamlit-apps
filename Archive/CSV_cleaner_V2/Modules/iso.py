import streamlit as st
import pandas as pd
import os
import sys

#Output Path
path=os.path.abspath(os.curdir)
sys.path.append(f'{path}/Modules')

#Module Imports for the different sections
import readFiles, save_files, download


def convert_dateTime(datafiles, cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Convert date-time column to ISO standard format')
    st.markdown('##### Choose the date-time column')


    # WIDGET INTERACTIONS----------------------------------------------------
    def click_button():
        st.session_state.convertISONext1 = True
        st.session_state.version=st.session_state.version+1 #update the version

    def change_vars():
        st.session_state.convertISONext1 = False

    # WIDGET CREATION ---------------------------------------------------------------       
    col1,col2=st.columns(2)
    date_time_col= col1.selectbox(label='Column',options=list(cols),index=None, key='select7', on_change=change_vars)# name of the date_time column
    col1.button("Next", type="primary", key='Next_Button7', on_click=click_button)

    if st.session_state.convertISONext1 == True: # Next button is clicked

        if date_time_col:
            convert_func(date_time_col,datafiles)# Call conversion function
        else:
            col1.error('Please select date-time column', icon="🚨")
        

def convert_func(date_time_col,datafiles):
    
    # LOOP THROUGH FILES------------------------------------------------ 
    df_list=[]
    for file in datafiles: # Loop through all the files
        
        #PROCESSING************************************************************************ 
        # 1. READ FILE 
        df=readFiles.read_datafiles(file)

        try: 
            # 2. PROCESS

            # Create a temp date column and convert to datetime
            df['temp_date'] = pd.to_datetime(df[date_time_col], format="mixed").dt.date

            # Create a temp time column and replace empty strings with NaN so they parse cleanly
            df['temp_time'] = df[date_time_col].replace('', pd.NA)

            if not df['temp_date'].empty and not df['temp_time'].empty:

                # Convert to datetime with pandas; Let pandas infer the format; Unparseable times → NaT
                parsed_times = pd.to_datetime(df['temp_time'], format=None, errors='coerce')

                # To get TIME OBJECTS (datetime.time):
                df['temp_time'] = parsed_times.dt.time

                # Fill missing time values with '00:00:00' (rows without time, will become NaT in the combined datetime column.)
                df['temp_time'] = df['temp_time'].fillna(pd.to_datetime('00:00:00').time())

                # Combine date and time
                if date_time_col=='Date_Time':
                    new_dt_colName='DateTime'
                else:
                    new_dt_colName='Date_Time'
                
                df[new_dt_colName] = pd.to_datetime(df['temp_date'].astype(str) + ' ' + df['temp_time'].astype(str), errors='coerce')

                # To get an ISO string:
                df[new_dt_colName]=df['Date_Time'].dt.strftime('%Y-%m-%dT%H:%M:%S')

                date_timecol=df.pop(new_dt_colName)       # pop the column from the data frame
                origDate_index=df.columns.get_loc(date_time_col) # get the index of the original date column
                df.insert(origDate_index,new_dt_colName, date_timecol) # insert the merged data column before the original date column

                #Drop the old date_time col
                df.drop(columns=[date_time_col, 'temp_time', 'temp_date'], axis=1, inplace=True)

        except ValueError: #Error in the date column
            st.error('Unknown datetime string format! Please check your Date-time column.',icon="🚨" )
 

        # 3. CREATE CSV FILE
        df_list=save_files.create_csv_files(file, df, df_list)

    #SHOW SNAPSHOT OF PROCESSES FILES-----------------------------------------------------------------------------------------------------------
    save_files.show_snapshot(df_list)

    # CALL DOWNLOAD FUNCTION---------------------------------------------------------
    download.download_output(df_list)
