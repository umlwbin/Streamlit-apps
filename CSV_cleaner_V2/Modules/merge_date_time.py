import streamlit as st
import pandas as pd
import os
import sys

#Output Path
path=os.path.abspath(os.curdir)
sys.path.append(f'{path}/Modules')

#Module Imports for the different sections
import readFiles, save_files, download


def mergedate_time(datafiles, cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Merge a date column and a time column')
    st.markdown('##### Enter the date and time columns')

    # WIDGET INTERACTIONS----------------------------------------------------
    def click_button():
        st.session_state.mergeDateNext = True
        st.session_state.version=st.session_state.version+1 #update the version

    def change_vars():
        st.session_state.mergeDateNext = False

    # WIDGET CREATION ---------------------------------------------------------------       
    def_date=None
    def_time=None
    ind=-1
    for c in cols:
        ind=ind+1
        if 'Date' in c or 'date' in c:
            def_date=ind
        if 'Time' in c or 'time' in c:
            def_time=ind

    col1,col2=st.columns(2)
    date_col = col1.selectbox(label='Date column',options=list(cols),index=def_date,key='select3', on_change=change_vars)# name of the date column
    time_col = col2.selectbox(label='Time column',options=list(cols),index=def_time, key='select4', on_change=change_vars) # name of the time column
    col1.button("Next", type="primary", key='Next_Button5', on_click=click_button)

    if st.session_state.mergeDateNext == True:# Next button is clicked
        merge_func(date_col,time_col,datafiles)# Call conversion function

def merge_func(date_col,time_col, datafiles):

    # LOOP THROUGH FILES------------------------------------------------  
    df_list=[]
    for file in datafiles: 

        #PROCESSING************************************************************************ 
        # 1. READ FILE 
        df=readFiles.read_datafiles(file)

        try:
            # 2. PROCESS
            df[date_col] = pd.to_datetime(df[date_col],format="mixed").dt.date# Convert date column to datetime
            df[time_col] = df[time_col].replace('', pd.NA)# Replace empty strings with NaN so they parse cleanly

            # Parse times and let pandas infer format
            parsed_times = pd.to_datetime(df[time_col],format=None,errors='raise')

            # To get TIME OBJECTS (datetime.time):
            df[time_col] = parsed_times.dt.time

            # Fill missing time values with '00:00:00' (rows without time, will become NaT in the combined datetime column.)
            df[time_col] = df[time_col].fillna(pd.to_datetime('00:00:00').time())

            # Combine date and time
            df['Date_Time'] = pd.to_datetime(df[date_col].astype(str) + ' ' + df[time_col].astype(str), errors='coerce')

            # To get an ISO string:
            df['Date_Time']=df['Date_Time'].dt.strftime('%Y-%m-%dT%H:%M:%S')

            date_timecol=df.pop('Date_Time')       # pop the column from the data frame
            origDate_index=df.columns.get_loc(date_col) # get the index of the original date column
            df.insert(origDate_index,'Date_Time', date_timecol) # insert the merged data column before the original date column

            #Drop the old date and time cols
            df=df.drop(columns=[date_col,time_col])

        except ValueError: #Error in the date column
            st.error('Unknown datetime string format! Please check your Date or Time column.',icon="🚨" )

        # 3. CREATE CSV FILE
        df_list=save_files.create_csv_files(file, df, df_list)
    
    #SHOW SNAPSHOT OF PROCESSES FILES-----------------------------------------------------------------------------------------------------------
    save_files.show_snapshot(df_list)

    # CALL DOWNLOAD FUNCTION---------------------------------------------------------
    download.download_output(df_list)
