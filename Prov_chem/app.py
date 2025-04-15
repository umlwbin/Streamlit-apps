import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import re
import os
import plotly.express as px

#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)
#st.session_state.update(st.session_state)
tab1, tab2 = st.tabs(["Data Cleaning", "Data Dashboard"])

def main():
    # GEt CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.sidebar.image(logo, width=250)

    # Title and Description
    st.sidebar.title('Provincial Chemistry File Editor 🧑🏽‍🔬')
    st.sidebar.html('''
    <style>
    div.s {    
        font-size: 16px;
        ul,ol {font-size: 16px; color: #333333; margin-bottom: 24px;}
        }
    </style>

    <div class="s"">
    This editor merges one row of units and one row of VMV codes to column headers, producing a file with one cleaned header row without spaces or special characters.<br>
    
    <br>

    You can also plot data by date and station.     
    </div> 
    '''
    )

    # Clear output data
    main_path=os.path.abspath(os.curdir)
    full_path=main_path+'/Prov_chem/'
    for f in os.listdir(full_path):
        if 'output' in f or 'cwout' in f:
            os.remove(os.path.join(full_path, f))

    fileupload()


def fileupload(): 
    with tab1:
        st.markdown('')
        st.markdown('#### Upload CSV files here')
        datafiles = st.file_uploader("Choos CSV files", accept_multiple_files=True)
        #If there are files uplaoded call get header widget function
        if datafiles:
            the_filenames=[d.name for d in datafiles if '.csv' in d.name] #check for csv files
            if the_filenames: #if there are CSV filesd
                #Get the column names
                c=0
                for file in datafiles:
                    c=c+1
                    if c==1:      
                        #Do a check to see if the columns are consistent
                        #--------------------------------------------------------------------------------
                        exit=False #Check to see if program should continue processing if the file looks good
                        
                        # To convert to a string based IO:
                        stringio = StringIO(file.getvalue().decode("utf-8"))
                        str_data = stringio.read()# To read file as string:

                        # get individual lines from string output
                        lines=[]
                        for l in str_data.split('\n'):
                            if l:
                                lines.append(l)
                        last_line=lines[-1] #will be the last line with data
                
                        #Delimiter
                        data_file_delimiter = ','
                
                        #The max num of columns come from the last line
                        max_col_num = len(last_line.split(data_file_delimiter)) + 1

                        #Num of columns from line 1
                        first_line_col_num = len(lines[0].split(data_file_delimiter)) + 1

                        #If they are different:
                        if first_line_col_num<max_col_num:
                            left, right = st.columns([0.8, 0.2])
                            left.error('Ooops, I think your file might have inconsistent columns. Each line must have the same number of columns. Please reformat your files and re-upload.', icon="🚨")
                            exit=True
                            break
                        #-------------------------------------------------------------------------------  
                # Call next function
                if exit!=True:
                    merge_rows_widget(datafiles) #func is whatever dunction passed to file_uplaod
            else:
                left, right = st.columns([0.8,0.2])
                left.warning('Oops, please uplaod CSV files', icon="⚠️")


def merge_rows_widget(datafiles):

    # This function creates widgets allowing the user to chose the rows that contain the units and VMV codes
    st.markdown('#####')
    st.markdown('#### Choose the rows that contains the Valid Method Variable (VMV) code and the variable units')
    
    #Setting States
    #clicked1 is for 1st button. It is set to false at first (not clicked yet)
    if 'clicked1' not in st.session_state:
        st.session_state.clicked1 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked1 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked1 = False

    col1,col2, col3=st.columns(3)
    vmvCode_row = col1.selectbox(label='Select the VMV code row',options=['0', '1'],index=0, key='select1', on_change=change_vars)
    units_row = col2.selectbox(label='Select the Units row',options=['0', '1'],index=1,key='select2', on_change=change_vars)
    #Next button
    st.button("Next", type="primary", key='Next_Button1', on_click=click_button)

    if st.session_state.clicked1==True:
        # Call next function
        merge_rows(datafiles, vmvCode_row,units_row)


def merge_rows(datafiles, vmvCode_row,units_row):
    # This function merges the user defined rows containing units and VMV codes
    
    #Get the last data file
    num_of_files=len(datafiles)
    last_file=[datafiles[num_of_files-1]]
    lastfile, = last_file

    # if len(datafiles)>0:
    #     #progress loader
    #     loader=v.ProgressCircular(indeterminate=True,size="50",color="primary", class_='my-9', style_='padding-top:60px; padding-bottom: 20px')
    
    count=0
    df_list=[] # create a list of datafiles
    filename_list=[] #create a list of filenames
    for file in datafiles: # Loop through all the files

        #Display loader
        if len(datafiles)>0:
            count=count+1
            if count==1:
                left, right = st.columns(2)
                left.markdown('')
                left.info("Cleaning headers and saving files...A few seconds please 🙂",icon='ℹ️')

            
        # Read the data!
        file.seek(0) #Go back to beginning of file
        rawdata_df=pd.read_csv(file, low_memory=False)
        
        headers=list(rawdata_df.columns) #get the headers
        units=list(rawdata_df.iloc[int(units_row)]) #Get the units row
        codes=list(rawdata_df.iloc[int(vmvCode_row)]) #Get the units row

        # Ensure there are no spaces or brackets in header name
        headers_list=[]
        for header, code, unit in zip(headers, codes, units):

            # Cleaning up the headers
            header=re.sub(r'\([^)]*\)', '', header) #Remove brackets and contents
            header=header.rstrip() # Remove trailing white space
            header = re.sub(r"[^\w\s]", '', header)# Remove all non-word characters (everything except numbers and letters)
            header = re.sub(r"\s+", '_', header) # Replace all remaining whitespace with _
            #header=header.replace('_1','')  # Remove the _1 for duplicated variables

            # Merging the nvm code and units
            if pd.isna(code)==False:
                header=header+'_'+str(code)+'_'+str(unit)
                header = re.sub(r"[^\w\s]", '_', header)# Remove all non-word characters
                header = re.sub(r"\s+", '_', header) # Replace all remaining whitespace with _

            headers_list.append(header) #append to final header list

        #Save updated column headers to data frame
        rawdata_df.columns=headers_list
        rawdata_df=rawdata_df.tail(-2)
        
        #Save as csv file
        output_filename=file.name[:-4]+'_cwout.csv'
        rawdata_df.to_csv(output_filename, float_format="%.4f", index=False)
        df_list.append(rawdata_df)
        filename_list.append(file.name[:-4])

    # ------------------------------- Download Files ----------------------------------------------- 
    path=os.path.abspath(os.curdir)
    download_output(path,df_list,filename_list)


def download_output(path,df_list,filename_list):
    from zipfile import ZipFile
    st.markdown('#####')
    st.markdown('#### Data Download')
    left, right = st.columns(2)
    left.success('All Done! 🎉', icon="✅")

    _, _, files = next(os.walk(path))
    files=[f for f in files if '_cwout' in f]
    file_count = len(files)

    if file_count==1:
        filename=files.pop()
        fp=df_list[0].to_csv().encode("utf-8")
        left.download_button(
        label="Download CSV",
        data=fp,
        file_name=filename,
        mime="text/csv",
        icon=":material/download:",
        )


    if file_count>1:
        filename='output_data.zip'
        from os.path import basename
        with ZipFile(filename, 'w') as zipObj:
           # Iterate over all the files in directory
            for file in files:
                filePath = os.path.join(path, file)
                # Add file to zip
                zipObj.write(filePath, basename(filePath))
        
        with open(filename, "rb") as fp:
            left.download_button(
            label="Download ZIP",
            data=fp,
            file_name=filename,
            mime="application/zip",
            icon=":material/download:",
            )
    left.markdown('######')
    left.info('Click on the **Data Dashboard** tab above to make some plots!', icon="ℹ️")
    choose_file(df_list, filename_list)


def choose_file(df_list,filename_list):
    with tab2:

        st.markdown('#####')
        st.markdown('#### Let\'s plot some data! 🕺')
        st.markdown('##### Choose the data file')

        col1,col2=st.columns(2)
        select_file = col1.selectbox(label='Select file',options=filename_list, index=None)

        if select_file: #if they have chosen a file
            for f, df in zip(filename_list, df_list): #Grab the data frame that corresponds with the filename
                if f==select_file:
                    sel_file=f
                    sel_df=df
                    choose_cols(sel_file, sel_df)


def choose_cols(sel_file, sel_df):
    cols=list(sel_df.columns) # Get the cols of the daatframe

    col1,col2=st.columns(2)
    col1.markdown('#####')
    col2.markdown('#####')
    col1.markdown('##### Select DateTime column')
    col2.markdown('##### Select Station column')

    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked2' not in st.session_state:
        st.session_state.clicked2 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked2 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked2 = False

    #Find date time
    datetime=[d for d in cols if 'Date' in d or 'date' in d or 'DATE' in d]
    datetime_idx=[ind for (ind,d) in enumerate(cols) if 'Date' in d or 'date' in d or 'DATE' in d] #get indices

    #Date widget
    if datetime:
        date_col = col1.selectbox(label='DateTime',options=cols,index=datetime_idx[0], key='select3')#selected date column
    else:
        date_col = col1.selectbox(label='DateTime',options=cols,index=None, key='select3')

    
    #Find station
    station_var=[s for s in cols if 'Station' in s or 'station' in s or 'STATION' in s]
    station_var_idx=[idx for idx,s in enumerate(cols) if 'Station' in s or 'station' in s or 'STATION' in s] #get index

    st_name=[s for s in station_var if 'NAME' in s or 'name' in s or 'Name' in s] #Check if there is a station_name, and chose this rather than station number
    st_name_idx=[idx for idx,s in enumerate(station_var) if 'NAME' in s or 'name' in s or 'Name' in s] #get index


    #station name widget - 
    if station_var:
        if st_name:
            station = col2.selectbox(label='Station Column',options=cols,index=st_name_idx[0],on_change=change_vars)#selected station column
        else:
            station = col2.selectbox(label='Station Column',options=cols,index=station_var_idx[0],on_change=change_vars)
    else:
        station = col2.selectbox(label='Station Column',options=cols,index=None,on_change=change_vars)

    st.button("Next", type="primary", key='Next_Button2', on_click=click_button) #next button

    if st.session_state.clicked2 == True:
        get_vars(sel_file, cols, sel_df, date_col,station)


def get_vars(sel_file, cols, sel_df, date_col,station):
    col1,col2=st.columns(2)
    col1.markdown('#####')
    col2.markdown('#####')
    col1.markdown('##### Select variable to plot')
    col2.markdown('##### Select Station for plot')

    #Setting States
    #clicked3 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked3' not in st.session_state:
        st.session_state.clicked3 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked3 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked3 = False

    # Get the var to plot - widget
    var = col1.selectbox(label='Variable',options=cols,index=None,on_change=change_vars)
    
    #get the station names
    station_data=list(sel_df[station])
    station_data = list(dict.fromkeys(station_data)) #Get unique vales in order
    station_data.insert(0,"None")

    # get the exact station name - widget
    station_var=col2.selectbox(label='Station Name',options=station_data,index=0, on_change=change_vars)
    left,right=st.columns([0.9,0.1])
    left.info("You can select **None** under **Station Name** to plot all stations", icon="ℹ️")

    #Plot btton
    left.button('Plot', type='primary',on_click=click_button)

    if st.session_state.clicked3 == True:

        import dateutil.parser
        dates=list(sel_df[date_col])
        converted_dates=[]
        for date in dates:
            converted_dates.append(dateutil.parser.parse(date).strftime("%Y-%m-%d %H:%M:%S"))
            
        sel_df[date_col]= converted_dates

        if var == None:
            left,right=st.columns(2)
            left.warning("You did not choose a variable to plot",icon="⚠️")
        else:
            plot(date_col, var, station, station_var, sel_df)



def plot(date_col, var, station, station_var, sel_df):
    #Check the var type
    from pandas.api.types import is_string_dtype
    from pandas.api.types import is_numeric_dtype

    # if is_string_dtype(sel_df[var])==True or is_numeric_dtype(sel_df[var])==False:
    #     left,right=st.columns([0.9,0.1])
    #     left.warning("This does not seem to be numeric data",icon="⚠️")

    #Get the data for the chosen varibale if the station is equal to the chosen station
    var_data=list(sel_df.loc[sel_df[station]==station_var, var])
    var_dates=list(sel_df.loc[sel_df[station]==station_var, date_col])
    
    good_dates=[]
    good_data=[]

    for data, date in zip(var_data, var_dates):
        if data is not np.nan and data!='' and data!=None:
            good_dates.append(date)
            good_data.append(data)


    var_data=good_data
    var_dates=good_dates


    if not var_data and station_var!='None':
        left,right=st.columns([0.9,0.1])
        left.error("Sorry, there is no data for the selected Station",icon="🚨",)      
    else:

        st.markdown('')
        def fig_update():
            fig.update_layout( yaxis_title=var, height=500, xaxis_title='DateTime',
                                yaxis = dict(tickfont =dict(size=14)),xaxis = dict(tickfont =dict(size=14)),font=dict(size=14), plot_bgcolor='ghostwhite', 
                                legend= {'itemsizing': 'constant'})
            fig.update_traces(marker={'size': 7})
            fig.update_xaxes(showline=True, linewidth=0.7, linecolor='LightGrey', mirror=True, showgrid=True, gridwidth=0.7, gridcolor='LightGrey')
            fig.update_yaxes(showline=True, linewidth=0.7, linecolor='LightGrey', mirror=True, showgrid=True, gridwidth=0.7, gridcolor='LightGrey')
            
            # Plot!
            st.plotly_chart(fig)


        if station_var=='None':
            dates=list(sel_df[date_col])
            values=list(sel_df[var])
            colors=list(sel_df[station])

            good_dates=[]
            good_data=[]
            good_colors=[]
            for data, date, colour in zip(values, dates, colors):
                if data is not np.nan and data!='' and data!=None:
                    good_dates.append(date)
                    good_data.append(data)
                    good_colors.append(colour)
        
            fig = px.scatter(x=good_dates, y=good_data, color=good_colors)
            fig.update_layout(legend_title='Stations')
            fig_update()

        else:
            if var_data:
                fig = px.scatter(x=var_dates, y=var_data)
                fig['data'][0]['showlegend']=True
                fig.update_layout(legend_title=station_var)
                fig_update()   
 
        

main()