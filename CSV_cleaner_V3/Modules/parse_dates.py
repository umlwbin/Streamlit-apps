import streamlit as st
import pandas as pd
import numpy as np

def parse_dateTime_widgets(cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Parse a date-time ISO column into Year, Month, Day and Time (optional)')
    st.markdown('##### Choose the date-time column')

    # WIDGET CREATION ------------------------------------------------------      
    col1,col2=st.columns(2)
    date_time_col= col1.selectbox(label='Column',options=list(cols),index=None, key='parse_select')# name of the date_time column
    col1.button("Next", type="primary", key='ParseNext_WidgetKey')

    if st.session_state.get("ParseNext_WidgetKey"): # Next button is clicked

        if date_time_col:
            task_inputs = {"date_time_col": date_time_col}                  
            return task_inputs
        else:
            col1.error('Please select date-time column', icon="🚨")
        

def parse_func(df, date_time_col):
     
    #PROCESSING************************************************************************ 
    try: 
        theres_time=False
        #Ensure your datetime column is in datetime format using pd.to_datetime()
        df[date_time_col] = pd.to_datetime(df[date_time_col], errors='coerce')

        #Use the .dt accessor to extract the year, month, day, and time components. Create new columns for each component.
        df['Year'] = df[date_time_col].dt.year.astype('Int64')
        df['Month'] = df[date_time_col].dt.month.astype('Int64')
        df['Day'] = df[date_time_col].dt.day.astype('Int64')

        # Create a 'time' column only when the time part is not 00:00:00
        df['Time'] = df[date_time_col].apply(lambda x: x.time() if pd.notnull(x) and (x.time() != pd.Timestamp.min.time()) else np.nan)

        year_col=df.pop('Year')     # pop the column from the data frame
        month_col=df.pop('Month')   # pop the column from the data frame
        day_col=df.pop('Day')       # pop the column from the data frame

        if 'Time' in df:
            time_col=df.pop('Time')     # pop the column from the data frame
            theres_time=True

        origDate_index=df.columns.get_loc(date_time_col) # get the index of the original date column
        df.insert(origDate_index+1,'Year', year_col)      # insert the merged data column before the original date column
        df.insert(origDate_index+2,'Month', month_col)    # insert the merged data column before the original date column
        df.insert(origDate_index+3,'Day', day_col) # insert the merged data column before the original date column
        
        if theres_time:
            df.insert(origDate_index+4,'Time', time_col) # insert the merged data column before the original date column

        return df

    except ValueError: #Error in the date column
        st.error('Unknown datetime string format! Please check your Date-time column.',icon="🚨" )