import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import re
import os
from datetime import datetime as dt
from streamlit_sortables import sort_items


#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)
#st.session_state.update(st.session_state)

def main():
    # GEt CanWIN Logo
    logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
    st.sidebar.image(logo, width=250)

    # Title and Description
    st.sidebar.title('CSV File Cleaning Tool 🧹')
    st.sidebar.html('''
    <style>
    div.s {    
        font-size: 16px;
        ul,ol {font-size: 16px; color: #333333; margin-bottom: 24px;}
        }
    </style>

    <div class="s"">
    This app allows you to perform basic cleaning tasks on multiple files:<br><br>
        <ul>
        <li>Rearrange columns</li>
        <li>Rename columns</li>
        <li>Add columns</li>
        <li>Remove columns</li>
        <li>Clean headers (remove special characters)</li>
        <li>Merge multiple files</li>
        <li>Convert date-time column to ISO format</li>
        <li>Merge a date column and a time column into one</li>
        </ul>
    </div> 
    '''
    )

    # Clear output data
    main_path=os.path.abspath(os.curdir)
    full_path=main_path+'/CSV_cleaner/'
    for f in os.listdir(full_path):
        if 'output' in f or 'cwout' in f:
            os.remove(os.path.join(full_path, f))

    what_to_do_widgets()


def fileuploadfunc(func): 
    st.markdown('')
    st.markdown('#### Upload a CSV/TXT File here')
    datafiles = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
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
                    #--------------------------------------------------------------------------------
                    else: # Columns are consistent!
                        #Create a data frame (table) with the data
                        df=pd.read_csv(file)
                        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    
                        #Get a list of the columns from this data excel sheet only once
                        cols=list(df.columns)
    
            # Call next function
            if exit!=True:
                func(datafiles, cols) #func is whatever dunction passed to file_uplaod
        else:
            left, right = st.columns([0.8,0.2])
            left.warning('Oops, please uplaod CSV files', icon="⚠️")

def what_to_do_widgets():
    st.markdown('#### What would you like to do?🤔')

    #Create Session states
    if 'rbclicked1' not in st.session_state:
        st.session_state.rbclicked1 = False

    # If the radiobutton is clicked, the session state is set to true (radiobutton is clicked)
    def click_Rbutton():
        st.session_state.rbclicked1 = True


    radiobutton=st.radio('Select an action',['Reorder columns','Add columns', 'Remove columns', 'Merge multiple files', 'Clean column headers',
                                             'Rename columns','Merge date and time columns', 'Convert DateTime column to ISO format'],
                                             captions=['','','','','Remove spaces and special characters', '','',''], index=None,on_change=click_Rbutton)

    st.warning('If uploading multiple files, ensure they all have the same column headers', icon="⚠️")

    #If a certain radio button is chosen
    if radiobutton=='Reorder columns':
        st.markdown('### Reorder Columns')
        fileuploadfunc(reorder)
        
    if radiobutton=='Add columns':
        st.markdown('### Add Columns')
        fileuploadfunc(how_many_vars_widget)
        
    if radiobutton=='Remove columns':
        st.markdown('### Remove Columns')
        fileuploadfunc(which_cols)

    if radiobutton=='Merge multiple files':
        st.markdown('### Merge multiple files')
        fileuploadfunc(merge)

    if radiobutton=='Clean column headers':
        st.markdown('### Clean column headers')
        fileuploadfunc(clean_headers)

    if radiobutton=='Rename columns':
        st.markdown('### Rename columns')
        fileuploadfunc(rename_headers)

    if radiobutton=='Merge date and time columns':
        st.markdown('### Merge date and time columns')
        fileuploadfunc(mergedate_time)
            
    if radiobutton=='Convert DateTime column to ISO format':
        st.markdown('### Convert DateTime column to ISO format')
        fileuploadfunc(convert_dateTime)

        # if radiobutton=='Add Result Value Qualifiers':
        #     fileuploadfunc(True,add_rvqs)

def reorder(datafiles, cols):
    #Create widgets for ordering the data variables
    st.markdown('#####')
    st.markdown('#### Reorder Columns')
    st.markdown('Organize column headers below in the order they should be in your file. Press **Next** to finish.')


    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked1' not in st.session_state:
        st.session_state.clicked1 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked1 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked1 = False

    #Sort the list using sort_items
    var_list=sort_items(cols)

    #Next button
    st.button("Next", type="primary", key='Next_Button1', on_click=click_button) #next button

    if st.session_state.clicked1==True: #If "next is clicked"
    
        df_list=[] # a list of all the dataframes created for each file
        filename_list=[]
        
        # Read all the data files
        for file in datafiles:
            
            file.seek(0) #Go back to beginning of file
            df=pd.read_csv(file)

            #Create a new dataframe
            new_df=pd.DataFrame()

            # Loop through the widget selections and update new dataframe 
            for v in var_list:
                new_df[v]=df[v]
            
            #Append csv file to list 
            filename_list.append(file.name)
    
            # Append new data frame to data frame list
            df_list.append(new_df)

        # Save all the data frames as csv files
        for f, d in zip(filename_list,df_list):
            csvname=f[:-4]+'_cwout.csv'
            d.to_csv(csvname, index=False)

        #Call download function
        main_path=os.path.abspath(os.curdir)
        path=main_path+'/CSV_cleaner/'

        download_output(path, df_list)

def how_many_vars_widget(datafiles, cols):
    # Ask how many variables to add?
    st.markdown('#####')
    st.markdown('#### Add new columns')
    left, right = st.columns([0.8, 0.2])
    left.info('The value will be the same throughout the column', icon="🚨")
    left.markdown('')
    left.markdown('##### How many fields would you like to add?')
    
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

    # int widget
    var_num=left.number_input(label="Number of fields to add", value=1, on_change=change_vars, key='addnum')
    st.button("Next", type="primary", key='Next_Button2', on_click=click_button) #next button

    if st.session_state.clicked2 ==True:
        # Call next function
        add_cols(datafiles, cols, var_num)

def add_cols(datafiles, cols, var_num):

    st.markdown('#####')
    st.markdown('##### Steps')
    st.markdown('1. Enter the name of the column to add')
    st.markdown('2. Enter the value for that column')
    st.markdown(f'3. Enter the column number where it should be added in your file (first column is 1, last column of this data is {len(list(cols))} )')
    st.markdown('If you change your mind, just leave fields empty and click next, or change the number above. 🙂')

    # l1=widgets.Label('Column variable name')
    # l3=widgets.Label('Variable value')
    # l4=widgets.Label('Column number')
    
    txt_list=[]
    txt_values_list=[]
    int_values_list=[]

    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked3' not in st.session_state:
        st.session_state.clicked3 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked3 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked3 = False

    col1,col2,col3=st.columns(3)
    for c in range(0, var_num):
        txt=col1.text_input(label='Column variable name',placeholder='E.g. project_name', value=None, on_change=change_vars, key='var')
        txt_list.append(txt)
        
        txt_val=col2.text_input(label='Variable value', placeholder="E.g. BaySys", value=None, on_change=change_vars, key='val')
        txt_values_list.append(txt_val)

        int_val=col3.number_input(label='Column number', value=(len(list(cols))+1)+c, on_change=change_vars,key='colnum')
        int_values_list.append(int_val)
    
    # Widget for next button
    st.button("Next", type="primary", key='Next_Button3', on_click=click_button) #next button

    if st.session_state.clicked3 == True:
        # Get the variable entries
        var_list=[]
        var_values_list=[]
        var_colNum_list=[]
        for t, tv, i in zip(txt_list, txt_values_list, int_values_list):
           #Get the dropdown field, value and col number
            if t!= None and tv!=None:
                var_list.append(t)
                var_values_list.append(tv)
                var_colNum_list.append(i)
        
            if (t!=None) and (tv==None):
                left, right = st.columns([0.8, 0.2])
                left.markdown('')
                left.warning(f'You have not entered a value for **{t}**. **{t}** wil be removed.', icon='⚠️')
  
        if all([t==None for t in txt_list]) and all([tv==None for t in txt_values_list]):
            left, right = st.columns([0.8, 0.2])
            left.markdown('')
            left.warning("You haven't entered any variables so we will just ignore it!")            
                
        df_list=[] # a list of all the dataframes created for each file
        filename_list=[]
        
        # Read all the data files
        for file in datafiles:
            file.seek(0) #Go back to beginning of file
            df=pd.read_csv(file)

            #Create a new dataframe
            new_df=df

            # Add the additional variables to new dataframe
            if var_list:
                for va, val, pos in zip(var_list, var_values_list, var_colNum_list,):
                    new_df.insert(pos-1, va, val)
                    
            #Append csv file to list 
            filename_list.append(file.name)
                       
            # Append new data frame to data frame list
            df_list.append(new_df)

        # Save all the data frames as csv files
        for f, d in zip(filename_list,df_list):
            csvname=f[:-4]+'_cwout.csv'
            d.to_csv(csvname, index=False)
 
        # Call download
        main_path=os.path.abspath(os.curdir)
        path=main_path+'/CSV_cleaner/'
        download_output(path, df_list)

def which_cols(datafiles, cols):
    st.markdown('#####')
    st.markdown('#### Remove columns')
    st.markdown('##### Which columns would you like to remove?')

    left, right = st.columns([0.8,0.2])

    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked4' not in st.session_state:
        st.session_state.clicked4 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked4 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked4 = False

    vars_to_rem = left.multiselect(label='Select columns',options=cols, on_change=change_vars, key='remove1')
    left.button("Next", type="primary", key='Next_Button4', on_click=click_button)

    if st.session_state.clicked4 ==True:
        # Call next function
        remove_cols(datafiles, cols, vars_to_rem)

def remove_cols(datafiles, cols, vars_to_rem):
    
    df_list=[] # a list of all the dataframes created for each file
    filename_list=[]    
    
    # Read all the data files
    for file in datafiles:
        # Read the data!
        file.seek(0) #Go back to beginning of file
        df=pd.read_csv(file)
          
        #Drop columns
        new_df=df.drop(columns=vars_to_rem)

        #Append csv file to list 
        filename_list.append(file.name)

        # Append new data frame to data frame list
        df_list.append(new_df)

    # Save all the data frames as csv files
    for f, d in zip(filename_list,df_list):
        csvname=f[:-4]+'_cwout.csv'
        d.to_csv(csvname, index=False)
        
    # Call download
    main_path=os.path.abspath(os.curdir)
    path=main_path+'/CSV_cleaner/'
    download_output(path,df_list )

def merge(datafiles, cols):
    st.markdown('#####')
    st.markdown('#### Merge files')

    df_list=[] # a list of all the dataframes created for each file
    filename_list=[]

    if len(datafiles)==1:
        left, right = st.columns([0.8,0.2])
        left.info('There is only one file uploaded so no work for us! 😌', icon='ℹ️')

    # Read all the data files
    for file in datafiles:

        file.seek(0) #Go back to beginning of file
        df=pd.read_csv(file)
        filename_list.append(file.name) #append to filename list
       
        # Append each data frame data frame list
        df_list.append(df)
        
        # Concatenate the list of data frames
        final_df=pd.concat(df_list)


    if all([set(df_list[0].columns) == set(df.columns) for df in df_list]):
        if len(datafiles)>1:
            left, right = st.columns([0.8,0.2])
            left.success('Column headers in all files are the same! Merging...',icon='✅')
        
        # save merged data frame as csv 
        csv_name='merged_cwout.csv'
        final_df.to_csv(csv_name, index=False)

        #add to df_list to pass to downlaod function (even though its just one file)
        df_list=[]
        df_list.append(final_df)

        main_path=os.path.abspath(os.curdir)
        path=main_path+'/CSV_cleaner/'
        download_output(path,df_list)
    
    else:
        left, right = st.columns([0.8,0.2])
        left.error('Column headers are not the same in all files 👎🏼. Please uplaod files with the same headers.',icon='🚨')

def clean_headers(datafiles, cols):
    st.markdown('#####')
    st.markdown('#### Clean headers')

    cleaned_headers=[]
    for header in cols:
        # Cleaning up the headers
        header=header.rstrip() # Remove trailing white space
        header = re.sub(r"[^\w\s\/]", '', header)# Remove all non-word characters (everything except numbers and letters)
        header = re.sub(r"\s+", '_', header) # Replace all remaining whitespace with _
        header=header.replace('/','_')  # Replace all / with _
        cleaned_headers.append(header)

    f=0
    df_list=[]
    for file in datafiles:
        f=f+1
        file.seek(0) #Go back to beginning of file
        df=pd.read_csv(file)

        if f==1:
            st.markdown('##### Your input column headers are: 👇🏼')
            st.write(df.head(1))
            st.markdown('')

        df.columns=list(cleaned_headers) #add new headers
        #create output CSV file with clean headers
        csv_name=file.name[:-4]+'_cwout.csv' 
        df.to_csv(csv_name, index=False)
        df_list.append(df) #add to df_list to pass to downlaod function

    if cleaned_headers==cols:
        left, right = st.columns([0.8,0.2])
        left.success('These column headers look pretty clean to me!',icon='✅')
    else:
        st.markdown('##### Your input column headers are: 👇🏼')
        st.dataframe(df.head(1))
        
        left, right = st.columns([0.8,0.2])
        left.markdown('<br>')
        left.success('Column headers are cleaned!',icon='✅')    
    
    main_path=os.path.abspath(os.curdir)
    path=main_path+'/CSV_cleaner/'
    download_output(path,df_list)

def rename_headers(datafiles, cols):
    st.markdown('#####')
    st.markdown('#### Rename headers')

    #Create widgets for matching the raw data
    st.markdown('##### Enter the variable names that should be used in your processed output file(s)')

    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked5' not in st.session_state:
        st.session_state.clicked5 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked5 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked5 = False

    #Dropdown lists for variable names
    stNames=list()
    col1, col2=st.columns(2)
    for c in range(0,len(cols)):
        stan=col1.text_input(label=f' Variable in file: {cols[c]}', value=cols[c], on_change=change_vars) #user text input
        stNames.append(stan) # append to the standardized names list

    # Widget for next button
    col1.button("Next", type="primary", key='Next_Button5', on_click=click_button)
    
    if st.session_state.clicked5 == True:#if button is clicked
        st_names=[]
        for c in range(0,len(cols)): 
            st_names.append(stNames[c]) #Get the user inputted standardized names            

        #replace the names in each dataframe
        df_list=[]
        filenames_list=[]
        
        c=0
        for file in datafiles:
            c=c+1
                        
            # Read the data!
            file.seek(0) #Go back to beginning of file
            df=pd.read_csv(file)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df_list.append(df)
            filenames_list.append(file)
            
        if all([set(df_list[0].columns) == set(df.columns) for df in df_list]): #Ensure all the columns are the same
            left, right = st.columns([0.8,0.2])
            left.success('Column headers in all files are the same! Renaming columns...',icon='✅')
        else:
            left, right = st.columns([0.8,0.2])
            left.error('Column headers are not the same in all files 👎🏼. Please uplaod files with the same headers.',icon='🚨')
   
        for file,df in zip(filenames_list, df_list):
            #Replace column names
            df.columns=st_names

            #save to output files    
            csv_name=file.name[:-4]+'_cwout.csv'
            df.to_csv(csv_name, index=False)

        if all([set(df_list[0].columns) == set(df.columns) for df in df_list]):
            #Call download function
            main_path=os.path.abspath(os.curdir)
            path=main_path+'/CSV_cleaner/'
            download_output(path,df_list)

def mergedate_time(datafiles, cols):

    st.markdown('#####')
    st.markdown('#### Merge a date column and a time column')
    st.markdown('##### Enter the date and time columns')

    def_date=None
    def_time=None
    ind=-1
    for c in cols:
        ind=ind+1
        if 'Date' in c or 'date' in c:
            def_date=ind

        if 'Time' in c or 'time' in c:
            def_time=ind

    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked6' not in st.session_state:
        st.session_state.clicked6 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked6 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked6 = False

    col1,col2=st.columns(2)
    date_col = col1.selectbox(label='Date column',options=list(cols),index=def_date,key='select3', on_change=change_vars)# name of the date column
    time_col = col2.selectbox(label='Time column',options=list(cols),index=def_time, key='select4', on_change=change_vars) # name of the time column
    col1.button("Next", type="primary", key='Next_Button5', on_click=click_button)

    if st.session_state.clicked6 == True:
        # Call conversion function
        merge_func(date_col,time_col,datafiles, cols)

def merge_func(date_col,time_col,datafiles, cols):
    # This function merges the date and time columns

    df_list=[]
    for file in datafiles: # Loop through all the files

        # Read the data!
        file.seek(0) #Go back to beginning of file
        rawdata_df=pd.read_csv(file)
        rawdata_df = rawdata_df.loc[:, ~rawdata_df.columns.str.contains('^Unnamed')]

        #First find any sample times that are empty and set to 00:00:00
        empty_times=np.where(pd.isnull(rawdata_df[time_col])) #all the rows where the sample time is empty
        empty_times=empty_times[0] 

        if empty_times.size:
            time_list=list(rawdata_df[time_col])
            idx=-1
            for t in time_list:
                idx=idx+1
                if idx in empty_times:
                    rawdata_df.at[idx, time_col] = '00:00:00'

        rawdata_df['date_time']=pd.to_datetime(rawdata_df[date_col] + ' ' + rawdata_df[time_col])# Convert columns to datetime and merge

        iso_date_list=[d.isoformat() for d in rawdata_df['date_time']] # Create a list of iso date_times
        rawdata_df['date_time']=iso_date_list  # Save to data frame column

        date_timecol=rawdata_df.pop('date_time')       # pop the column from the data frame
        origDate_index=rawdata_df.columns.get_loc(date_col) # get the index of the original date column
        rawdata_df.insert(origDate_index,'date_time', date_timecol) # insert the merged data column before the original date column 

        #Save to output files    
        output_filename=file.name[:-4]+'_cwout.csv'
        rawdata_df.to_csv(output_filename, float_format="%.2f", index=False) # Save as csv
        df_list.append(rawdata_df)

    # Call download
    main_path=os.path.abspath(os.curdir)
    path=main_path+'/CSV_cleaner/'
    download_output(path,df_list)

def convert_dateTime(datafiles, cols):

    st.markdown('#####')
    st.markdown('#### Convert date-time column to ISO standard format')
    st.markdown('##### Enter date/time column and desired output format')


    st.markdown('')
    st.info('Datetime formats require only one letter indicating a date or time element, with a "%" before it. For example, 2009-01-01 00:00:00  = %Y-%m-%d %H:%M:%S"', icon='ℹ️',)

    #Setting States
    if 'clicked7' not in st.session_state:
        st.session_state.clicked7 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked7 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked7 = False

    col1,col2=st.columns(2)
    out_format=col1.text_input(label="Format", value='%Y-%m-%dT%H:%M:%SZ', key='text7', on_change=change_vars)# format date_times should be converted to
    date_time_col= col2.selectbox(label='Column',options=list(cols),index=None, key='select7', on_change=change_vars)# name of the date_time column
    col1.button("Next", type="primary", key='Next_Button7', on_click=click_button)

    if st.session_state.clicked7 == True:   
        # Call conversion function
        convert_func(date_time_col,out_format,datafiles)

def convert_func(date_time_col,out_format,datafiles):
    df_list=[]
    for file in datafiles: # Loop through all the files
        # Read the data!
        file.seek(0) #Go back to beginning of file
        rawdata_df=pd.read_csv(file)

        cols=rawdata_df.columns
        if date_time_col in cols: 
            rawdata_df[date_time_col] = pd.to_datetime(rawdata_df[date_time_col])         # Parse the date time
            rawdata_df[date_time_col] = rawdata_df[date_time_col].dt.strftime(out_format) # Convert dates to given output format   

        output_filename=file.name[:-4]+'_cwout.csv'
        rawdata_df.to_csv(output_filename, index=False) # Save as csv
        df_list.append(rawdata_df)

    # Call download
    main_path=os.path.abspath(os.curdir)
    path=main_path+'/CSV_cleaner/'
    download_output(path,df_list)

def download_output(path,df_list):
    from zipfile import ZipFile
    st.markdown('#####')
    st.markdown('#### Data Download')
    left, right = st.columns([0.8, 0.2])
    left.success('All Done! 🎉', icon="✅")

    _, _, files = next(os.walk(path))
    files=[f for f in files if '_cwout' in f]
    file_count = len(files)

    if file_count==1:
        filename=files.pop()
        fp=df_list[0].to_csv().encode("utf-8")
        st.download_button(
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
            st.download_button(
            label="Download ZIP",
            data=fp,
            file_name=filename,
            mime="application/zip",
            icon=":material/download:",
            )

main()