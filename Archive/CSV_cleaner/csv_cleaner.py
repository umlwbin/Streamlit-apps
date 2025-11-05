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

#Output Path
path=os.path.abspath(os.curdir)

#Sett toggle session state  to False at first (switch is off to use the same dataset)
if 'toggle' not in st.session_state:
    st.session_state.toggle=False
    st.session_state.version=0 #This is updated after each next button is pressed for each function
    st.session_state.firstRun=True #This is turned on when the download function is called.

if 'processedFiles' not in st.session_state:
    st.session_state.processedFiles=False

# if st.session_state.version==0 and st.session_state.toggle==False: #Clear on first run 
#     # Clear output data
#     for f in os.listdir(path):
#         if 'output' in f or 'cwout' in f:
#             os.remove(os.path.join(path, f))

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

    what_to_do_widgets()

def fileuploadfunc(func): 
    st.markdown('')
    st.markdown('#### Upload a CSV/TXT File here')

    if 'new_upload' not in st.session_state:
        st.session_state.new_upload=False

    def newUpload():
        st.session_state.new_upload=True

        # Clear output data
        for f in os.listdir(path):
            if 'output' in f or 'cwout' in f:
                os.remove(os.path.join(path, f))

    datafiles = st.file_uploader("Choose a CSV file", accept_multiple_files=True, on_change=newUpload)
    

    #If there are files uplaoded call get header widget function
    if st.session_state.new_upload:
        the_filenames=[d.name for d in datafiles if '.csv' in d.name] #check for csv files
        if the_filenames: #if there are CSV files
            #Get the column names
            c=0
            for file in datafiles:
                c=c+1
                if c==1:

                    #Do a check to see if the columns are consistent or there are empty columns-------------------------------------
                    #When reading a file with inconsistent columns using Python's pandas library, the error raised is 
                    #pandas.errors.ParserError: Expected ... fields in line ..., saw .... 
                    #This error indicates that the number of columns in a particular row does not match the expected 
                    #number of columns based on the file's structure or the specified parameter
                    
                    try:
                        df = pd.read_csv(file)
                    except pd.errors.ParserError as e:
                        left, right = st.columns([0.8, 0.2])
                        left.error('Ooops, I think your file might have inconsistent columns. Each line must have the same number of columns. Please reformat your files and re-upload.', icon="🚨")
                    else:
                        #Ok, so there are no inconcistent columns BUT, there could be empty, unnamed columns
                        #lets check for empty, unnnamed columns.
                        unnamed_cols = [col for col in df.columns if 'Unnamed' in col]

                        if unnamed_cols:
                            unnamed_cols_num=len(unnamed_cols)
                            emptyCols=0
                            for col in unnamed_cols:
                                if df[col].isnull().all(): #checking if the cols are all empty 
                                    emptyCols=emptyCols+1 #counting the empty cols

                            if unnamed_cols_num==emptyCols: #There are empty cols
                                if not func.__name__=='file_cleanup': #for every func except file_cleanup, encourage them to run the file cleanup 
                                    left, right = st.columns([0.6, 0.4])
                                    st.toast('Perhaps select the "Tidy File Checker" function first from the menu.', icon='⚠️')
                                    st.toast(f'This file(s) has {emptyCols} empty columns that will be removed.',icon='⚠️')                                   
                                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns
   
                                #Get a list of the columns from this data excel sheet only once
                                cols=list(df.columns)
                                func(datafiles, cols) #func is whatever dunction passed to file_uplaod
                                
                        else: # Columns are consistent!
                            cols=list(df.columns)
                            st.markdown(' ')
                            func(datafiles, cols) #func is whatever dunction passed to file_uplaod

        # else:
        #     left, right = st.columns([0.8,0.2])
        #     left.warning('Oops, please uplaod CSV files', icon="⚠️")

def what_to_do_widgets():
    st.markdown('#### What would you like to do? 🤔')

    #Create Session states

    # If the radiobutton is clicked, the session state is set to true (radiobutton is clicked)
    def click_Rbutton():
        #clicked1-7 are the next buttons for each function (after the user manipulates the widgets). 
        # This ensures they have to press that last next button again if the radio button is changed
        st.session_state.clicked1 = False
        st.session_state.clicked2 = False
        st.session_state.clicked3 = False 
        st.session_state.clicked4 = False
        st.session_state.clicked5 = False
        st.session_state.clicked6 = False
        st.session_state.clicked7 = False


    radiobutton=st.radio('Select an action',['Tidy Data Checker','Reorder columns','Add columns', 'Remove columns', 'Merge multiple files', 'Clean column headers',
                                             'Rename columns','Merge date and time columns', 'Convert DateTime column to ISO format'],
                                             captions=['Please use this checker for key cleaning steps. It removes empty rows and cols, standardizes NaNs, and cleans column headers.','','','','','Remove spaces and special characters', '','',''], 
                                             index=None,on_change=click_Rbutton)

    
    #Set up the Toggle button-------------------------------------------------------------------------------------------------------------
    def onToggle():
        
        if tog: # if it is ON, and then you switch it off, 'if tog' will be true
            st.session_state.toggle = False # If it is switched off On-->Off
        else:
            st.session_state.toggle = True #if it is switched on

        st.session_state.clicked1 = False
        st.session_state.clicked2 = False
        st.session_state.clicked3 = False #This ensures they have to press that last next button again, otherwise it would go straight to downloads. 
        st.session_state.clicked4 = False
        st.session_state.clicked5 = False
        st.session_state.clicked6 = False
        st.session_state.clicked7 = False
    
    #Toggle button
    #If this toggle is activated we want to use the latest output files and keep curating it
    st. markdown('')
    tog=st.toggle("**Activate switch to use the same dataset**",on_change=onToggle,key='toggleSwitch')

    if not tog:
        left, right = st.columns([0.6, 0.4])
        left.info('To continue processing the same files, activate the switch above!', icon="ℹ️",)

    if st.session_state.toggle==True:  #If the user turns the toggle ON
        #The version gets updated after each Next button. The first run will be false after the first download fucntion
        if st.session_state.version>=1 and st.session_state.firstRun==False:
            #Grab the alrady curated files
            _, _, files = next(os.walk(path))
            tempfiles=[f for f in files if '_cwout' in f]

            if tempfiles: #there are curated files already generated
                #Get the cols again since we wont do the upload func, and the cols may have changed
                c=0
                for file in tempfiles:
                    c=c+1
                    if c==1:
                        df=pd.read_csv(file, nrows=1) # just get a row
                        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                        tempcols= list(df.columns)

                #If a certain radio button is chosen with the toggle on, go to that function directly
                if radiobutton=='Reorder columns':
                    st.markdown('-------------')
                    st.markdown('### Reorder Columns')
                    st.markdown(' ')
                    reorder(tempfiles,tempcols)
                    
                if radiobutton=='Add columns':
                    st.markdown('-------------')
                    st.markdown('### Add Columns')
                    st.markdown(' ')
                    how_many_vars_widget(tempfiles, tempcols)
                    
                if radiobutton=='Remove columns':
                    st.markdown('-------------')
                    st.markdown('### Remove Columns')
                    st.markdown(' ')
                    which_cols(tempfiles, tempcols)

                if radiobutton=='Merge multiple files':
                    st.markdown('-------------')
                    st.markdown('### Merge multiple files')
                    st.markdown(' ')
                    merge(tempfiles, tempcols)

                if radiobutton=='Clean column headers':
                    st.markdown('-------------')
                    st.markdown('### Clean column headers')
                    st.markdown(' ')
                    clean_headers(tempfiles, tempcols)

                if radiobutton=='Rename columns':
                    st.markdown('-------------')
                    st.markdown('### Rename columns')
                    st.markdown(' ')
                    rename_headers(tempfiles, tempcols)

                if radiobutton=='Merge date and time columns':
                    st.markdown('-------------')
                    st.markdown('### Merge date and time columns')
                    st.markdown(' ')
                    mergedate_time(tempfiles, tempcols)
                        
                if radiobutton=='Convert DateTime column to ISO format':
                    st.markdown('-------------')
                    st.markdown('### Convert DateTime column to ISO format')
                    st.markdown(' ')
                    convert_dateTime(tempfiles, tempcols)

                if radiobutton=='Tidy Data Checker':
                    st.markdown('-------------')
                    st.markdown('### Tidy Data Checker')
                    st.markdown(' ')
                    file_cleanup(tempfiles,tempcols)

        else: # If the toggle is on, but we havent processed any files yet, we still need to use the uplaoder. 
            #If a certain radio button is chosen
            if radiobutton=='Reorder columns':
                st.markdown('-------------')
                st.markdown('### Reorder Columns')
                fileuploadfunc(reorder)
                
            if radiobutton=='Add columns':
                st.markdown('-------------')
                st.markdown('### Add Columns')
                fileuploadfunc(how_many_vars_widget)
                
            if radiobutton=='Remove columns':
                st.markdown('-------------')
                st.markdown('### Remove Columns')
                fileuploadfunc(which_cols)

            if radiobutton=='Merge multiple files':
                st.markdown('-------------')
                st.markdown('### Merge multiple files')
                fileuploadfunc(merge)

            if radiobutton=='Clean column headers':
                st.markdown('-------------')
                st.markdown('### Clean column headers')
                fileuploadfunc(clean_headers)

            if radiobutton=='Rename columns':
                st.markdown('-------------')
                st.markdown('### Rename columns')
                fileuploadfunc(rename_headers)

            if radiobutton=='Merge date and time columns':
                st.markdown('-------------')
                st.markdown('### Merge date and time columns')
                fileuploadfunc(mergedate_time)
                    
            if radiobutton=='Convert DateTime column to ISO format':
                st.markdown('-------------')
                st.markdown('### Convert DateTime column to ISO format')
                fileuploadfunc(convert_dateTime)

            if radiobutton=='Tidy Data Checker':
                st.markdown('-------------')
                st.markdown('### Tidy Data Checker')
                fileuploadfunc(file_cleanup)

                # if radiobutton=='Add Result Value Qualifiers':
                #     fileuploadfunc(True,add_rvqs)


    else: #Toggle is OFF, use the uplaoder
        #If a certain radio button is chosen
        if radiobutton=='Reorder columns':
            st.markdown('-------------')
            st.markdown('### Reorder Columns')
            fileuploadfunc(reorder)
            
        if radiobutton=='Add columns':
            st.markdown('-------------')
            st.markdown('### Add Columns')
            fileuploadfunc(how_many_vars_widget)
            
        if radiobutton=='Remove columns':
            st.markdown('-------------')
            st.markdown('### Remove Columns')
            fileuploadfunc(which_cols)

        if radiobutton=='Merge multiple files':
            st.markdown('-------------')
            st.markdown('### Merge multiple files')
            fileuploadfunc(merge)

        if radiobutton=='Clean column headers':
            st.markdown('-------------')
            st.markdown('### Clean column headers')
            fileuploadfunc(clean_headers)

        if radiobutton=='Rename columns':
            st.markdown('-------------')
            st.markdown('### Rename columns')
            fileuploadfunc(rename_headers)

        if radiobutton=='Merge date and time columns':
            st.markdown('-------------')
            st.markdown('### Merge date and time columns')
            fileuploadfunc(mergedate_time)
                
        if radiobutton=='Convert DateTime column to ISO format':
            st.markdown('-------------')
            st.markdown('### Convert DateTime column to ISO format')
            fileuploadfunc(convert_dateTime)

        if radiobutton=='Tidy Data Checker':
            st.markdown('-------------')
            st.markdown('### Tidy Data Checker')
            fileuploadfunc(file_cleanup)

            # if radiobutton=='Add Result Value Qualifiers':
            #     fileuploadfunc(True,add_rvqs)        

def reorder(datafiles, cols):
    #Create widgets for ordering the data variables
    #st.markdown('#####')
    st.markdown('#### Sort Columns')
    st.markdown('Organize column headers below in the order they should be in your file. ')
    st.markdown('Press **Next** to finish. ')

    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked1' not in st.session_state:
        st.session_state.clicked1 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked1 = True
        st.session_state.version=st.session_state.version+1
            
    #Sort the list using sort_items  
    var_list=sort_items(cols)

    #Next button
    st.button("Next", type="primary", key='Next_Button1', on_click=click_button) #next button
    if st.session_state.clicked1==True: #If "next is clicked"
    
        df_list=[] # a list of all the dataframes created for each file
        
        # Read all the data files
        for file in datafiles:

            if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files if toggle is simply off, or its just the first run
                
                try: #Just because there is no on_change function for the sort_items customized streamlit widget, so we cant set st.session_state.clicked1 = False for a change
                    file.seek(0) #Go back to beginning of file
                except AttributeError:
                    st.session_state.version=st.session_state.version+1
                    left, right = st.columns([0.8, 0.2])
                    left.warning('Oops, you might have to make that switch again, sorry!', icon="⚠️")

            df=pd.read_csv(file)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns

            #Create a new dataframe
            new_df=pd.DataFrame()

            # Loop through the widget selections and update new dataframe 
            for v in var_list:
                new_df[v]=df[v]

            #Create and save the output csv files
            if st.session_state.version==1 or st.session_state.toggle==False: # if we are using the filenames from the uploader   
                #create the output file name
                output_filename=file.name[:-4]+'_cwout.csv' 

            else:#Toggle is ON - using previously edited files

                #Rename files
                newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
                os.rename(file, newfilename) #rename the file

                # Add back cwout + a version number to reflect changes
                output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
                os.remove(newfilename) #Remove the old file (which now has the name- newfilename)
                
            #save the data frame as CSV using the above filename
            new_df.to_csv(output_filename, index=False) 

            # Append new data frame to data frame list
            df_list.append(new_df)


        #Call download function
        download_output(path, df_list)

def how_many_vars_widget(datafiles, cols):
    # Ask how many variables to add?
    st.markdown('')
    st.markdown('#### How many fields would you like to add?')
    
    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked2' not in st.session_state:
        st.session_state.clicked2 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked2 = True
        st.session_state.processedFiles=True # Set the processed files session state to true, so now the toggle button will show up (if it didn't before)

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked2 = False

    # int widget
    left2, right2 = st.columns([0.1, 0.9])
    var_num=left2.number_input(label="Number of fields to add", value=1, on_change=change_vars, key='addnum')
    st.button("Next", type="primary", key='Next_Button2', on_click=click_button) #next button

    if st.session_state.clicked2 ==True:
        # Call next function
        add_cols(datafiles, cols, var_num)

def add_cols(datafiles, cols, var_num):
    st.markdown('')
    st.markdown('##### Steps')
    st.markdown('1. Enter the name of the column to add')
    st.markdown('2. Enter the value for that column. **ℹ️ Note: The value will be the same throughout the column**')
    st.markdown(f'3. Enter the column number where it should be added in your file (first column is 1, last column of this data is {len(list(cols))} )')
    left, right = st.columns([0.6, 0.4])
    left.info('If you change your mind, just leave fields empty and click next, or change the number above. 🙂', icon="ℹ️")

    #st.markdown('If you change your mind, just leave fields empty and click next, or change the number above. 🙂')
    
    txt_list=[]
    txt_values_list=[]
    int_values_list=[]

    #Setting States
    #clicked3 is for 3rd button. It is set to false at first (not clicked yet)
    if 'clicked3' not in st.session_state:
        st.session_state.clicked3 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked3 = True
        st.session_state.version=st.session_state.version+1 #update the version

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked3 = False

    #create widgets to enter col, value and col position
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
        exit=False
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
        
        # Read all the data files
        for file in datafiles:
            if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files
                file.seek(0) #Go back to beginning of file
            df=pd.read_csv(file)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns

            #Create a new dataframe
            new_df=df

            # Add the additional variables to new dataframe
            try:
                if var_list:
                    for va, val, pos in zip(var_list, var_values_list, var_colNum_list,):
                        new_df.insert(pos-1, va, val)
            except ValueError as e:
                left, right = st.columns([0.8, 0.2])
                left.markdown('')
                left.error("You already have that column name!",icon="🚨",)
                exit=True

        if exit==False:
            #Create and save the output csv files
            if st.session_state.version==1 or st.session_state.toggle==False: # if we are using the filenames from the uploader   
                #create the output file name
                output_filename=file.name[:-4]+'_cwout.csv'

            else:#Toggle is ON - using previously edited files
                #Rename files
                newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
                os.rename(file, newfilename) #rename   

                # Add back cwout + a version number to reflect changes     
                output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
                os.remove(newfilename) #Remove the old file (which now has the name- newfilename)
                
            #save the data frame as CSV using the above filename
            new_df.to_csv(output_filename, index=False)

            #Append this data frame to the list
            df_list.append(new_df)
    
            # Call download
            download_output(path, df_list)

def which_cols(datafiles, cols):
    st.markdown('#### Remove columns')
    st.markdown('##### Which columns would you like to remove?')

    #Setting States
    #clicked4 is set to false at first (not clicked yet)
    if 'clicked4' not in st.session_state:
        st.session_state.clicked4 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        
        st.session_state.clicked4 = True
        st.session_state.version=st.session_state.version+1 #update the version

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_vars():
        st.session_state.clicked4 = False

    left, right = st.columns([0.8,0.2])
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
        if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files
            file.seek(0) #Go back to beginning of file
        df=pd.read_csv(file)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns
          
        #Drop columns
        new_df=df.drop(columns=vars_to_rem)

        #Create and save the output csv files
        if st.session_state.version==1 or st.session_state.toggle==False: # if we are using the filenames from the uploader   
            #create the output file name
            output_filename=file.name[:-4]+'_cwout.csv' 

        else:#Toggle is ON - using previously edited files

            #Rename files
            newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
            os.rename(file, newfilename) #rename   

            # Add back cwout + a version number to reflect changes     
            output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
            os.remove(newfilename) #Remove the old file (which now has the name- newfilename)

        #save the data frame as CSV using the above filename
        new_df.to_csv(output_filename, index=False)

        #Append this data frame to the list
        df_list.append(new_df)        
        
    # Call download
    download_output(path,df_list )

def merge(datafiles, cols):
    st.markdown('#### Merging all your files')

    df_list=[] # a list of all the dataframes created for each file
    filename_list=[]

    if len(datafiles)==1:
        left, right = st.columns([0.8,0.2])
        left.info('There is only one file uploaded so no work for us! 😌', icon='ℹ️')

    # Read all the data files
    for file in datafiles:
        if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files
            file.seek(0) #Go back to beginning of file
        df=pd.read_csv(file)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns

        # Append each data frame data frame list
        df_list.append(df)
        
    # Concatenate the list of data frames
    final_df=pd.concat(df_list,ignore_index=True)

    #check if the columns in all files were the same
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
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns

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
        left.markdown(' ')
        left.success('Column headers are cleaned!',icon='✅')    
    
    path=os.path.abspath(os.curdir)
    download_output(path,df_list)

def rename_headers(datafiles, cols):
    #st.markdown('#### Rename headers')

    #Create widgets for matching the raw data
    st.markdown('#### Enter the variable names that should be used in your processed output file(s)')

    #Setting States
    #clicked2 is for 2nd button. It is set to false at first (not clicked yet)
    if 'clicked5' not in st.session_state:
        st.session_state.clicked5 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked5 = True
        st.session_state.version=st.session_state.version+1 #update the version

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
            if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files
                file.seek(0) #Go back to beginning of file
            df=pd.read_csv(file)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]             
            

        #Check if all cols are the same    
        if all([set(df_list[0].columns) == set(df.columns) for df in df_list]): #Ensure all the columns are the same
            left, right = st.columns([0.8,0.2])
            left.success('Column headers in all files are the same! Renaming columns...',icon='✅')
            
            #Replace column names
            df.columns=st_names

            #Create and save the output csv files
            if st.session_state.version==1 or st.session_state.toggle==False: # if we are using the filenames from the uploader   
                #create the output file name
                output_filename=file.name[:-4]+'_cwout.csv' 

            else:#Toggle is ON - using previously edited files

                #Rename files
                newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
                os.rename(file, newfilename) #rename   

                # Add back cwout + a version number to reflect changes     
                output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
                os.remove(newfilename) #Remove the old file (which now has the name- newfilename)

            #save the data frame as CSV using the above filename
            df.to_csv(output_filename, index=False)

            #Append this data frame to the list
            df_list.append(df) 

            #Call download function
            download_output(path,df_list)

        else:
            left, right = st.columns([0.8,0.2])
            left.error('Column headers are not the same in all files 👎🏼. Please uplaod files with the same headers.',icon='🚨')
        
def mergedate_time(datafiles, cols):

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
        st.session_state.version=st.session_state.version+1 #update the version

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
        if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files
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

        #Create and save the output csv files
        if st.session_state.version==1 or st.session_state.toggle==False: # if we are using the filenames from the uploader   
            #create the output file name
            output_filename=file.name[:-4]+'_cwout.csv' 

        else:#Toggle is ON - using previously edited files
 
            #Rename files
            newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
            os.rename(file, newfilename) #rename   

            # Add back cwout + a version number to reflect changes     
            output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
            os.remove(file) #Remove the old file

        #save the data frame as CSV using the above filename
        rawdata_df.to_csv(output_filename, float_format="%.2f", index=False)

        #Append this data frame to the list
        df_list.append(rawdata_df)

    # Call download
    download_output(path,df_list)

def convert_dateTime(datafiles, cols):
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
        st.session_state.version=st.session_state.version+1 #update the version

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
        if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files
            file.seek(0) #Go back to beginning of file
        rawdata_df=pd.read_csv(file)
        rawdata_df = rawdata_df.loc[:, ~rawdata_df.columns.str.contains('^Unnamed')] #Remove unnamed columns

        cols=rawdata_df.columns
        if date_time_col in cols: 
            rawdata_df[date_time_col] = pd.to_datetime(rawdata_df[date_time_col])         # Parse the date time
            rawdata_df[date_time_col] = rawdata_df[date_time_col].dt.strftime(out_format) # Convert dates to given output format   


        #Create and save the output csv files
        if st.session_state.version==1 or st.session_state.toggle==False: # if we are using the filenames from the uploader   
            #create the output file name
            output_filename=file.name[:-4]+'_cwout.csv' 

        else:#Toggle is ON - using previously edited files
            
            #Rename files
            newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
            os.rename(file, newfilename) #rename   

            # Add back cwout + a version number to reflect changes     
            output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
            os.remove(newfilename) #Remove the old file (which now has the name- newfilename)

        #save the data frame as CSV using the above filename
        rawdata_df.to_csv(output_filename,index=False)

        #Append this data frame to the list
        df_list.append(rawdata_df)


    # Call download
    download_output(path,df_list)

def file_cleanup(datafiles,cols):

    st.markdown('#### File Cleanup 🗒️ ')

    with st.container(border=True):
        st.markdown('##### Nan Check')
        st.markdown('')
        st.markdown('Are there any Nan representations in your file(s) that are not in the following list?')
        st.markdown('**NA**, **?**, **N/A**, **" "**, **np.nan**, **None**, **Nan**, **NaN**')
        # str_Nan_list=['NA', '?', 'N/A', '" "', 'np.nan', 'None', 'Nan', 'NaN']
        # nan_str_df=pd.DataFrame(str_Nan_list)
        # st.table(nan_str_df.T)
        st.markdown('If yes, enter the Nan representation(s) below. **Click Add** after each entry.')
        st.markdown('When you are finished, or **if you have nothing to enter**, click **Continue**.')
        
        # Widget for user to enter NAN
        nans=[]
        left, middle1,middle2, right = st.columns([2,1,1,5],vertical_alignment='bottom')
        user_nan=left.text_input('Enter',label_visibility='hidden')
        
        #ADD Button
        if middle1.button("Add Entry"):#If Add button is pressed, add the Nan entered by user
            nans.append(user_nan) #Add user nan to list
            st.markdown(f'{user_nan} was added to list')
        
        #CONTINUE Button
        def click_button():
            st.session_state.version=st.session_state.version+1 #update the version
        continue_button=middle2.button("Continue",on_click=click_button,type='primary')

    if continue_button:
        df_list=[]
        for file in datafiles: # Loop through all the files
            
            # Read the data!
            if st.session_state.version==1 or st.session_state.toggle==False: #using the uploader files
                file.seek(0) #Go back to beginning of file
            df=pd.read_csv(file)

            # 1. EMPTY COLUMNS
            empty_cols_list=[]
            unnamed_cols = [col for col in df.columns if 'Unnamed' in col]
            if unnamed_cols:
                unnamed_cols_num=len(unnamed_cols) #number of Unnamed columns
                emptyCols=0
                for col in unnamed_cols:
                    if df[col].isnull().all(): #ensuring that the column is completely empty
                        emptyCols=emptyCols+1 #num of empty cols
                
                if emptyCols>0:
                    empty_cols_list.append(emptyCols) #Keeping track of the empty cols per file

                if unnamed_cols_num==emptyCols: #all unnamed cols are just empty cols
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns
                    cols=list(df.columns) #update the cols


            #2. EMPTY ROWS
            # empty rows check
            empty_rows_list=[]
            empty_rows= df[df.isna().all(axis=1)]
            if not empty_rows.empty:
                emptyRows=len(empty_rows) #number of empty rows
                empty_rows_list.append(emptyRows) #Keeping track of the empty rows per file

            # Remove empty rows
            df = df.dropna(how='all')

            #3. CHECKING NANS--------------------------------------------------------
            # Identify different NaN representations
            na_values = ['NA', '?', 'N/A', '', np.nan, None, 'Nan', 'NaN']

            if nans:
                na_values.extend(nans) #Add the user provided nans
            
            # Replace all identified NaN values with empty strings
            df = df.replace(na_values, '')
            
        
            #4. CLEANING HEADERS--------------------------------------------------------
            headers_list=[]
            cleaned_headers=[]
            for header in cols:
                # Cleaning up the headers
                header=header.rstrip() # Remove trailing white space
                header = re.sub(r"[^\w\s\/]", '', header)# Remove all non-word characters (everything except numbers and letters)
                header = re.sub(r"\s+", '_', header) # Replace all remaining whitespace with _
                header=header.replace('/','_')  # Replace all / with _
                cleaned_headers.append(header)

            df.columns=list(cleaned_headers) #add new headers

            if cleaned_headers==cols:
                headers_already_clean=True
            else:
                headers_already_clean=False
                headers_list.append(headers_already_clean)
                

            #Create and save the output csv files
            if st.session_state.version==1 or st.session_state.toggle==False: # if we are using the filenames from the uploader   
                #create the output file name
                output_filename=file.name[:-4]+'_cwout.csv' 

            else:#Toggle is ON - using previously edited files
                
                #Rename files
                newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
                os.rename(file, newfilename) #rename   

                # Add back cwout + a version number to reflect changes     
                output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
                os.remove(newfilename) #Remove the old file (which now has the name- newfilename)

            #save the data frame as CSV using the above filename
            df.to_csv(output_filename,index=False)

            #Append this data frame to the list
            df_list.append(df)


        #Display chamges made
        st.markdown('######')
        if empty_cols_list:
            st. markdown(f'✅ There were empty columns found in one or more files that were removed')
        else:
            st. markdown(f'✅ There were no empty columns found 🥳')


        if empty_rows_list:
            st. markdown(f'✅ There were empty rows found in one or more files that were removed')
        else:
            st. markdown(f'✅ There were no empty rows found 🥳')

        st.markdown(f'✅ All NaNs were converted to blank spaces 🥳')

        if headers_list:
            st.markdown('✅ Column headers with special characters or extra spaces were found and corrected')
        else:
            st.markdown('✅ Your column headers were pretty clean 🥳')
    

        # Call download
        download_output(path,df_list)   

def download_output(path,df_list):
    from zipfile import ZipFile

    def on_download():
        st.balloons()
        st.session_state.new_upload=False

    #Update the first run session state. Once it gets to the first download set the first run to false
    st.session_state.firstRun=False

    st.markdown('######')
    st.markdown('#### Data Download')
    left, right = st.columns([0.6, 0.4])
    left.success('All Done! 🎉', icon="✅")
 
    _, _, files = next(os.walk(path))
    files=[f for f in files if '_cwout' in f]
    file_count = len(files)

    if file_count==1:
        try:
            filename=files.pop()
            fp=df_list[0].to_csv().encode("utf-8")
            st.download_button(
            label="Download CSV",
            data=fp,
            file_name=filename,
            mime="text/csv",
            on_click=on_download,
            icon=":material/download:"
            )
        except TypeError as e:
            st.write(f'e')
            pass


    if file_count>1:
        try:
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
                on_click=on_download,
                mime="application/zip",
                icon=":material/download:",
                )

        except TypeError:
            pass


main()