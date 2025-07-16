import streamlit as st
import pandas as pd

def parse_date_time_Widgets():

    st.markdown('#### ⏰ Separate Year, Month, Day, Time into their own columns ')
    st.markdown('This step parses one date time ISO column into Day, year, month and time columns.')

    def click_Begin_button():
        st.session_state.begin5 = True
        st.session_state.allDone=False
    st.button("Let's Go!", type="primary", key='Begin_Button5', on_click=click_Begin_button)

def extract_yr_mn_day_time(cleaned_df_list): 
    temp_workin_list=[]
    for df in cleaned_df_list:   
        cleaned_dt_col='Date_Time' #Date_time_column that was inserted 
        #Ensure your datetime column is in datetime format using pd.to_datetime()
        df[cleaned_dt_col] = pd.to_datetime(df[cleaned_dt_col])

        #Use the .dt accessor to extract the year, month, day, and time components. Create new columns for each component.
        df['Year'] = df[cleaned_dt_col].dt.year
        df['Month'] = df[cleaned_dt_col].dt.month
        df['Day'] = df[cleaned_dt_col].dt.day
        df['Time'] = df[cleaned_dt_col].dt.time

        df=move_cols_to_front_of_dataframe(df)
        temp_workin_list.append(df) #update the list for this processing

    cleaned_df_list=temp_workin_list
    return cleaned_df_list


def move_cols_to_front_of_dataframe(df):
    cleaned_dt_col='Date_Time' #Date_time_column that was inserted
    year_col=df.pop('Year')     # pop the column from the data frame
    month_col=df.pop('Month')   # pop the column from the data frame
    day_col=df.pop('Day')       # pop the column from the data frame
    time_col=df.pop('Time')     # pop the column from the data frame

    origDate_index=df.columns.get_loc(cleaned_dt_col) # get the index of the original date column
    df.insert(origDate_index+1,'Year', year_col)      # insert the merged data column before the original date column
    df.insert(origDate_index+2,'Month', month_col)    # insert the merged data column before the original date column
    df.insert(origDate_index+3,'Day', day_col) # insert the merged data column before the original date column
    df.insert(origDate_index+4,'Time', time_col) # insert the merged data column before the original date column
    return df 

