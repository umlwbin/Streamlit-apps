import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
import re
import os
from datetime import datetime as dt

#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)
#st.session_state.update(st.session_state)

def main():
    # GEt CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.sidebar.image(logo, width=250)

    # Title and Description
    st.sidebar.title('Idronaut Data processor 🌊')
    st.sidebar.image("https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Idronaut/img/idronaut.jpg", width=150)
    st.sidebar.html('''
    <style>
    div.s {    
        font-size: 16px;
        ul,ol {font-size: 16px; color: #333333; margin-bottom: 24px;}
        }
    </style>

    <div class="s"">

        <b>The Idronaut</b> <br>

    IDRONAUT sensors and instrumentations measure the most important physical and chemical water parameters like, temperature,
     depth, salinity, pH, dissolved oxygen and much more.
        <br><br>

        <b>What This App Does</b> <br>
    <ul>
      <li>Reads idronaut text/csv files and allows a user to visually crop the downcast</li>
      <li>Allows the user to enter the Latitude, Longitude and Site ID which is added to the processed file</li>
      <li>Curates the file to CanWIN best practices</li>
    </ul>
                  
    </div>
    '''
    )

    #Download example files Widget
    main_path=os.path.abspath(os.curdir)

    _, _, files = next(os.walk(main_path))
    files=[f for f in files if 'example1' in f]
    filepath=os.path.join(main_path,files[0])

    file_df=pd.read_csv(filepath, sep='\s+')
    txt=file_df.to_csv(index=False).encode("utf-8")

    st.sidebar.download_button(
        label="Download Example TXT",
        data=txt,
        file_name="example.txt",
        mime="text/csv",
        icon=":material/download:",
        )
    

    # Clear output data
    for f in os.listdir(main_path):
        if 'output' in f or 'example.csv' in f:
            os.remove(os.path.join(main_path, f))

    file_upload()


def file_upload(): 

    st.markdown('#### Upload a CSV/TXT File here')
    datafile = st.file_uploader("Choose a CSV file", accept_multiple_files=False)
    
    #If there are files uplaoded call get header widget function
    if datafile:
        if '.csv' in datafile.name or '.txt' in datafile.name:
            read_files(datafile)

        else:
            left, right = st.columns(2)
            left.warning('Oops, please uplaod a CSV/TXT files', icon="⚠️")


def read_files(datafile):
    
    #Do a check to see if the columns are consistent
    #--------------------------------------------------------------------------------
    # To convert to a string based IO:
    stringio = StringIO(datafile.getvalue().decode("utf-8"))

    # To read file as string:
    str_data = stringio.read()

    # get individual lines from string output
    lines=[]
    for l in str_data.split('\n'):
        if l:
            lines.append(l)
    last_line=lines[-1] #will be the last line with data
    data_file_delimiter = ','  #Delimiter

    #The max num of columns come from the last line
    max_col_num = len(last_line.split(data_file_delimiter)) + 1

    #Num of columns from line 1
    first_line_col_num = len(lines[0].split(data_file_delimiter)) + 1

    #If they are different:
    if first_line_col_num<max_col_num:
        left, right = st.columns([0.8, 0.2])
        left.error('Ooops, I think your file might have inconsistent columns. Each line must have the same number of columns. Please reformat your files and re-upload.', icon="🚨")
    else:
               
        #Create a data frame (table) with the data
        df=pd.read_csv(datafile, sep='\s+')
        cols=list(df.columns)

        correct_headers=['Date', 'Time','Pres','Temp','Cond','Sal','Turb','SigmaT','Cond25']

        wrong_file=False
        for ch in correct_headers:
            if ch not in cols:
                wrong_file=True
                left, right = st.columns([0.8, 0.2])
                left.error('Ooops, not finding some key variables. The MBGL Idronaut files contain: Date, Time, Pres, Temp, Cond, Sal, Turb, SigmaT, Cond25. Please try again.', icon="🚨")
                break
        if wrong_file==False:         
            # Display now reading file message
            filename=datafile.name
            st.success(f" Now reading file {filename}")
            
            #Ensure date column is this format: '%Y-%m-%d'
            df['Date'] = pd.to_datetime(df.Date, format='%d-%m-%Y')
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
            #Ensure TIME column is in this format '%H:%M:%S'
            df['Time'] = pd.to_datetime(df.Time, format='%H:%M:%S.%f')
            df['Time'] = df['Time'].dt.strftime('%H:%M:%S')
    
            #Add the Specific Conductance as a column in data frame-------------------------
            r=0.02 # Temperature correction coefficient for the sample - this value can change 
            Cond_std25=[round(c/(1+r*(t-25)),4) for c,t in zip(list(df['Cond']), list(df['Temp']))] #Create a list of the cond_std25 values
            df['Cond_std25_calculated']=Cond_std25 # Adding column of calculated specific conductance         

            # This section will plot a graph to find the downcast rows----------------------
            st.markdown('#####')
            st.markdown('### Downcast Processing')
            st.markdown('##### 1. Find the downcast from the plot below 📉')

            # loader=v.ProgressCircular(indeterminate=True,size="50",color="primary", class_='my-7') #This is just a progress loader
            # display(loader)

            # Plot graph
            fig = px.scatter(df, x=df.index, y='Pres')
            fig.update_layout(yaxis_title='Pressure', height=500, xaxis_title='Row',legend=dict(itemsizing='constant'),plot_bgcolor='#e5ecf6',
                                yaxis = dict(autorange="reversed",tickfont =dict(size=14)),xaxis = dict(tickfont =dict(size=14)))
            fig.update_traces(marker={'size': 4})
            
            # Plot!
            st.plotly_chart(fig)

            #Create Session states
            #Clicked1 is for first button. It is set to false at first (not clicked yet)
            if 'clicked1' not in st.session_state:
                st.session_state.clicked1 = False

            # If the button is clicked, the session state is set to true (button is clicked)
            def click_button():
                st.session_state.clicked1 = True

            # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
            def change_num():
                st.session_state.clicked1 = False

            #Create widgets for grabbing the start row and end row----------------------
            st.markdown('##### 2. Add the starting and ending row for first downcast (**Index** from the plot above represents the rows.)')
            left, right = st.columns(2)
            start_row=left.number_input("Start",value=0, on_change=change_num)# Get the start and end row values from the widgets
            end_row=left.number_input("End",value=0, on_change=change_num)# Get the start and end row values from the widgets
            left.button("Next", type="primary", on_click=click_button)

            if st.session_state.clicked1: #button is clicked
                #Call cleaning function and pass the start row, end row, file, and dataframe to it - Go to next cell!
                clean(datafile, df, start_row, end_row)


            #Because the server can be slow to load plots, let rest of code wait a few secs for plot to load.
            # from time import sleep
            # sleep(3) 
            # #close the spinning loader
            # loader.class_ = 'd-none' # disapear
            
def clean(datafile, df, start_row, end_row):

    #CLEANING!
    # 1. Subset the data frame for only the downcast
    downcast_df=df.loc[start_row:end_row]

    # 2. Plot new data frame
    # Plot graph to find the downcast rows
    st.success("Success!", icon="✅")
    st.markdown('#####')
    st.markdown('##### 3.Plotting Downcast with Temperature')

    # #Progress loader - because the server can be slow to create plots
    # loader=v.ProgressCircular(indeterminate=True,size="50",color="primary", class_='my-7')
    # display(loader)
    
    fig = px.scatter(downcast_df, x='Temp', y='Pres')
    fig.update_layout(yaxis_title='Pressure (dbar; represented as depth in m)', height=500, xaxis_title='Temperature (°C)',legend=dict(itemsizing='constant'),plot_bgcolor='#e5ecf6',
                      yaxis = dict(autorange="reversed",tickfont =dict(size=14)),xaxis = dict(tickfont =dict(size=14)))
    fig.update_traces(marker={'size': 4})
    st.plotly_chart(fig)

    # #close the spinning loader
    # loader.class_ = 'd-none' # disapear

    # 3. Final Curation
    # 3.1 Merge date and time
    downcast_df['Datetime'] = pd.to_datetime(downcast_df['Date'] + " " + downcast_df['Time']) #Merge Date and Time to Datetime
    
    #Remove date and time columns
    downcast_df = downcast_df.drop('Date', axis=1)
    downcast_df = downcast_df.drop('Time', axis=1)
    
    #Add Datetime column to front
    column_to_move = downcast_df.pop('Datetime')
    downcast_df.insert(0, "Datetime", column_to_move)

    # Create widgets for Lat, long and site ID
    st.markdown('### Data Curation')
    st.markdown('##### 1. Add the Latitude (Decimal Degrees), Longitude (Decimal Degrees) and Site ID')

    #Create Session states
    #Clicked2 is for first button. It is set to false at first (not clicked yet)
    if 'clicked2' not in st.session_state:
        st.session_state.clicked2 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked2 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_num():
        st.session_state.clicked2 = False

    #Create widgets for grabbing the lat, lon, site----------------------

    left, right = st.columns(2)
    lat=left.number_input("Lat",value=None, key="lattitude",on_change=change_num)# Get the start and end row values from the widgets
    long=left.number_input("Long",value=None, key="longitude", on_change=change_num)# Get the start and end row values from the widgets
    siteid=left.text_input("Site ID",value=None, key="site", on_change=change_num)# Get the start and end row values from the widgets
    left.button(label="Next", type="primary", key='nextbutton2', on_click=click_button)

    if st.session_state.clicked2==True: #button is clicked
        #Call the next function after clicking Next to continue the cleaning (See next Cell)
        clean2(lat,long,siteid,downcast_df,datafile)

def clean2(lat,long,siteid,downcast_df,datafile):
    if lat==None or long==None or siteid==None: #If nothing was entered
        st.error('Please enter all the above variables!', icon="🚨")

    else: #If the user entered the Lat, Long and site ID

        # 3.3 Create lat, long, and siteID columns and add the values
        downcast_df.insert(0, 'Site ID', siteid)
        downcast_df.insert(2, 'Latitude', lat)
        downcast_df.insert(3, 'Longitude', long)

        # 3.4 Add metadata and rename column names
        cols=list(downcast_df.columns)
        cuarated_cols=[] #Build this list with the curated column headers
        for col in cols:
            if col=='Datetime' or col=='Latitude' or col=='Longitude' or col=='Site ID':
                cuarated_cols.append(col)
            else:
                if 'Pres' in col:
                    newcol='Pres_Z'
                    cuarated_cols.append(newcol)
                elif 'Temp' in col:
                    newcol='CTDTmp90'
                    cuarated_cols.append(newcol)
                elif col=='Cond':
                    newcol='CTDCond'
                    cuarated_cols.append(newcol)
                elif 'Sal' in col:
                    newcol='CTDSal'
                    cuarated_cols.append(newcol)
                elif 'Turb' in col:
                    newcol='Turbidity'
                    cuarated_cols.append(newcol)
                elif 'SigmaT' in col:
                    newcol='SigTheta'
                    cuarated_cols.append(newcol)
                elif 'Cond25' in col:
                    newcol='CTDCond25_raw'
                    cuarated_cols.append(newcol)
                elif 'Cond_std25_calculated' in col:
                    newcol='CTDCond25_calc'
                    cuarated_cols.append(newcol)

                RVQ_name=newcol+'_Result_Value_Qualifier'
                idx=downcast_df.columns.get_loc(col)    #get index for column
                downcast_df.insert(idx+1,RVQ_name, '')  #insert RVQ column
                cuarated_cols.append(RVQ_name)

        downcast_df.columns=cuarated_cols #renaming column headers

        download_output(downcast_df)

def download_output(downcast_df):
    st.markdown('#####')
    st.markdown('### Data Download')

    st.success('All Done! 🎉', icon="✅")

    csv=downcast_df.to_csv().encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="output.csv",
        mime="text/csv",
        icon=":material/download:",
        )

main()


