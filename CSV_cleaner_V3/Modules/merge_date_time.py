import streamlit as st
import pandas as pd

def merge_dt_widgets(cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Enter the date and time columns')

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
    date_column = col1.selectbox(label='Date column',options=list(cols),index=def_date,key='select3')# name of the date column
    time_column = col2.selectbox(label='Time column',options=list(cols),index=def_time, key='select4') # name of the time column
    col1.button("Next", type="primary", key='mergeDateNext_WidgetKey')

    if st.session_state.get("mergeDateNext_WidgetKey"):# Next button is clicked
        if date_column and time_column:
            task_inputs = {"date_column": date_column,
                           "time_column": time_column}                  
            return task_inputs
        
        else:
            st.error('Please select date and time columns!',icon="🚨" )


def merge(df, date_column,time_column):
    
    #PROCESSING************************************************************************ 
    try:
        df[date_column] = pd.to_datetime(df[date_column],format="mixed").dt.date# Convert date column to datetime
        df[time_column] = df[time_column].replace('', pd.NA)# Replace empty strings with NaN so they parse cleanly

        # Parse times and let pandas infer format
        parsed_times = pd.to_datetime(df[time_column],format=None,errors='raise')

        # To get TIME OBJECTS (datetime.time):
        df[time_column] = parsed_times.dt.time

        # Fill missing time values with '00:00:00' (rows without time, will become NaT in the combined datetime column.)
        df[time_column] = df[time_column].fillna(pd.to_datetime('00:00:00').time())

        # Combine date and time
        df['Date_Time'] = pd.to_datetime(df[date_column].astype(str) + ' ' + df[time_column].astype(str), errors='coerce')

        # To get an ISO string:
        df['Date_Time']=df['Date_Time'].dt.strftime('%Y-%m-%dT%H:%M:%S')

        date_timecol=df.pop('Date_Time')       # pop the column from the data frame
        origDate_index=df.columns.get_loc(date_column) # get the index of the original date column
        df.insert(origDate_index,'Date_Time', date_timecol) # insert the merged data column before the original date column

        #Drop the old date and time cols
        df=df.drop(columns=[date_column,time_column])

        return df

    except ValueError: #Error in the date column
        st.error('Unknown datetime string format! Please check your Date or Time column.',icon="🚨" )