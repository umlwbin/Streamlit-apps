import streamlit as st
import pandas as pd
import copy

def parse_date_time_Widgets():

    st.markdown('#### ⏰ Separate Year, Month, Day, Time into their own columns ')
    st.markdown('This step parses one date time ISO column into Day, year, month and time columns.')

    def click_Begin_button():
        st.session_state.parseBegin = True
        st.session_state.parseNext1 = False

        # Turn off all other Begin button sessions states
        st.session_state.mergeRowsBegin = st.session_state.pivotBegin = st.session_state.headersBegin = st.session_state.isoBegin = st.session_state.rvqBegin = False
        # Turn off all other Next button sessions states
        st.session_state.mergeRowsNext1 = st.session_state.PivotNext1 = st.session_state.PivotNext2 = st.session_state.isoNext1 = st.session_state.isoNext2 = st.session_state.rvqNext1=st.session_state.rvqNext2 = False
        # Turn off all other sessions states
        st.session_state.pivotRadio1 = st.session_state.allDone = False 

    st.button("Let's Go!", type="primary", key='Begin_Button5', on_click=click_Begin_button)


def select_date_time_column_Widgets(cleaned_df_list):
    st.markdown('##### ')
    st.markdown('##### Select your ISO date-time column')

    def change_vars():
        st.session_state.parseNext1 = False
        st.session_state.allDone=False

    def click_Next_button():
        st.session_state.parseNext1 = True

    cols=list(cleaned_df_list[0].columns)
    col1, col2=st.columns(2)

    potential_date_col = [string for string in cols if ('DATE' in string) or ('date' in string)]#get potential date column
    try:
        potential_date_col_inex=cols.index(potential_date_col[0])#get index of first date element, ideally its just one
    except IndexError:
        potential_date_col_inex=None

    #Select widget
    dt_col=col1.selectbox('Date-Time column', options=cols, index=potential_date_col_inex,on_change=change_vars)

    #Next button
    st.button("Next", type="primary", key='NextButton_Parse', on_click=click_Next_button)

    if st.session_state.parseNext1:
        return dt_col
    

def extract_yr_mn_day_time(cleaned_df_list, dt_col): 

    # Create a deep copy of the current list in session state. We will work on this copy
    cleaned_df_list=copy.deepcopy(st.session_state.cleaned_df_list)

    # Push current version to history before makign any changes
    st.session_state.df_history.append(copy.deepcopy(st.session_state.cleaned_df_list))

    # Clear redo stack since we are making a new change
    st.session_state.redo_stack.clear()

    date_time_error=False
    for df in cleaned_df_list:   
        cleaned_dt_col=dt_col #Date_time_column that was inserted 
        #Test first to see if it is actually a datetime value (maybe user selected the wrong column)
        try:
            #Ensure your datetime column is in datetime format using pd.to_datetime()
            df[cleaned_dt_col] = pd.to_datetime(df[cleaned_dt_col])

            #Use the .dt accessor to extract the year, month, day, and time components. Create new columns for each component.
            df['Year'] = df[cleaned_dt_col].dt.year.astype('Int64')
            df['Month'] = df[cleaned_dt_col].dt.month.astype('Int64')
            df['Day'] = df[cleaned_dt_col].dt.day.astype('Int64')

            # Create 'time' column if there's a time component
            df['Time'] = df[cleaned_dt_col].apply(lambda dt: dt.time() if dt.time() != pd.Timestamp(0).time() else pd.NaT)

            # Drop 'time' column if it's all NaT or NaN
            if df['Time'].isna().all():
                df.drop(columns=['Time'], inplace=True)

            #df['Time'] = df[cleaned_dt_col].dt.time

            df=move_cols_to_front_of_dataframe(df, dt_col)

        except ValueError: #Error in the date column
            st.error('Unknown datetime string format! Please check your Date-time column, or restructure first',icon="🚨")
            date_time_error=True

    #Update the cleaned list in session state
    st.session_state.cleaned_df_list=cleaned_df_list
    return date_time_error


def move_cols_to_front_of_dataframe(df, dt_col):
    cleaned_dt_col=dt_col #Date_time_column that was inserted
    year_col=df.pop('Year')     # pop the column from the data frame
    month_col=df.pop('Month')   # pop the column from the data frame
    day_col=df.pop('Day')       # pop the column from the data frame

    if 'Time' in df:
        time_col=df.pop('Time')     # pop the column from the data frame

    origDate_index=df.columns.get_loc(cleaned_dt_col) # get the index of the original date column
    df.insert(origDate_index+1,'Year', year_col)      # insert the merged data column before the original date column
    df.insert(origDate_index+2,'Month', month_col)    # insert the merged data column before the original date column
    df.insert(origDate_index+3,'Day', day_col) # insert the merged data column before the original date column
    if 'Time' in df:
        df.insert(origDate_index+4,'Time', time_col) # insert the merged data column before the original date column
    return df 

