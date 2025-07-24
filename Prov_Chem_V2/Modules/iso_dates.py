import streamlit as st
import pandas as pd


def Choose_One_Or_Two_DateTime_Columns_Widgets():

    st.markdown('#### ⏰ Convert date-time column to ISO standard format')
    st.markdown('This step converts either one datetime column or two Date and Time columns to ISO format.')

    # If the selections are changed, the session state is set to False (button is unclicked, so user has to click NExt again)
    def change_vars():
        st.session_state.isoNext1 = False
        st.session_state.isoNext2 = False
        st.session_state.allDone=False

    def click_Begin_button():
        st.session_state.isoBegin = True
        st.session_state.isoNext1 = False
        st.session_state.isoNext2 = False

        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.parseBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.mergeRowsNext1 = st.session_state.PivotNext1 = st.session_state.PivotNext2 = st.session_state.parseNext1 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone = False 



    st.button("Let's Go!", type="primary", key='Begin_Button4', on_click=click_Begin_button)

    if st.session_state.isoBegin: 
        #Create the radio buttons to choose
        st.markdown('#####')
        st.markdown('##### Is there one date-time column, or separate date and time columns?')
        date_structure=st.radio("Choose one",options=["Just one Date-time column", "Separate Date and Time columns"], index=None, on_change=change_vars) #radio buttons to choose
        return date_structure

def one_dateTime_col_Widgets(cleaned_df_list, date_structure_radioButton):
    if date_structure_radioButton!="Just one Date-time column":
        return
    
    st.markdown('######')
    st.markdown('##### Select the date-time column')

    #Setting States
    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.isoNext1 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.isoNext1 = False

    col1,col2=st.columns(2, vertical_alignment="center", gap="large")
    cols=list(cleaned_df_list[0].columns) #Updated columns

    potential_date_col = [string for string in cols if ('DATE' in string) or ('date' in string)]#get potential date column
    try:
        potential_date_col_inex=cols.index(potential_date_col[0])#get index of first date element, ideally its just one
    except IndexError:
        potential_date_col_inex=None
    
    #Select Widget and Next Button
    date_time_col= col1.selectbox(label='Column',options=cols,index=potential_date_col_inex, key='select0', on_change=change_vars)# get name of the date_time column
    col1.button("Next", type="primary", key='Next_Button4', on_click=click_button) #Next Button     
    return date_time_col  

def convert_one_dateTime_col_to_iso(cleaned_df_list,date_time_col):
    temp_workin_list=[]
    date_time_error=False
    for df in cleaned_df_list:    
        #Test first to see if it is actually a datetime value (maybe user selected the wrong column)
        try:
            # Create a temp date column and convert to datetime
            df['temp_date'] = pd.to_datetime(df[date_time_col], format="mixed").dt.date

            # Create a temp time column and replace empty strings with NaN so they parse cleanly
            df['temp_time'] = df[date_time_col].replace('', pd.NA)

            if not df['temp_date'].empty and not df['temp_time'].empty:

                # Convert to datetime with pandas
                parsed_times = pd.to_datetime(
                    df['temp_time'],
                    format=None,           # Let pandas infer the format
                    errors='coerce'        # Unparseable times → NaT
                )

                # To get TIME OBJECTS (datetime.time):
                df['temp_time'] = parsed_times.dt.time

                # Fill missing time values with '00:00:00' (rows without time, will become NaT in the combined datetime column.)
                df['temp_time'] = df['temp_time'].fillna(pd.to_datetime('00:00:00').time())

                # Combine date and time
                df['Date_Time'] = pd.to_datetime(df['temp_date'].astype(str) + ' ' + df['temp_time'].astype(str), errors='coerce')

                # To get an ISO string:
                df['Date_Time']=df['Date_Time'].dt.strftime('%Y-%m-%dT%H:%M:%S')

                date_timecol=df.pop('Date_Time')       # pop the column from the data frame
                origDate_index=df.columns.get_loc(date_time_col) # get the index of the original date column
                df.insert(origDate_index,'Date_Time', date_timecol) # insert the merged data column before the original date column

                #Drop the old date and time cols
                df=df.drop(columns=[date_time_col])

        except ValueError: #Error in the date column
            st.error('Unknown datetime string format! Please check your Date-time column.',icon="🚨" )
            date_time_error=True

        temp_workin_list.append(df) #update the list for this processing. If there is a datetime error, the original df would be added

    cleaned_df_list=temp_workin_list
    return cleaned_df_list, date_time_error

def separate_dateTime_cols_Widgets(cleaned_df_list, date_structure_radioButton):

    if date_structure_radioButton!="Separate Date and Time columns":
        return
    
    st.markdown('######')
    st.markdown('##### Select the Date column and the Time column')
    cols=list(cleaned_df_list[0].columns) #Updated columns
  
    #Setting States
    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.isoNext2 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.isoNext2 = False

    col1,col2=st.columns(2, vertical_alignment="center", gap="large")
    
    potential_date_col = [string for string in cols if ('DATE' in string) or ('date' in string)]#get potential date column
    try:
        potential_date_col_index=cols.index(potential_date_col[0])#get index of first date element, ideally its just one
    except IndexError:
        potential_date_col_index=None

    potential_time_col = [string for string in cols if ('TIME' in string) or ('Time' in string)]#get potential date column
    try:
        potential_time_col_index=cols.index(potential_time_col[0])#get index of first date element, ideally its just one
    except IndexError:
        potential_time_col_index=None
    
    date_col= col1.selectbox(label='Date Column',options=cols,index=potential_date_col_index, key='select01', on_change=change_vars)# name of the date column
    time_col= col1.selectbox(label='Time Column',options=cols,index=potential_time_col_index, key='select02', on_change=change_vars)# name of the time column
    col1.button("Next", type="primary", key='Next_Button5', on_click=click_button)
    
    return date_col, time_col

def convert_date_and_time_cols_to_iso(date_col,time_col,cleaned_df_list):  

    temp_workin_list=[]
    date_time_error=False

    for df in cleaned_df_list:           
        try:
            # Convert date column to datetime
            df[date_col] = pd.to_datetime(df[date_col],format="mixed").dt.date

            # Replace empty strings with NaN so they parse cleanly
            df[time_col] = df[time_col].replace('', pd.NA)

            # Parse with pandas
            parsed_times = pd.to_datetime(
                df[time_col],
                format=None,           # Let pandas infer the format
                errors='raise'
            )


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
            date_time_error=True

        temp_workin_list.append(df) #update the list for this processing
    
    cleaned_df_list=temp_workin_list        
    return cleaned_df_list, date_time_error
