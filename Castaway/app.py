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
    st.sidebar.title('Castaway CTD Processor 🌊')
    st.sidebar.image("https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Castaway/img/ctd.jpg", width=60)
    st.sidebar.html('''
    <style>
    div.s {    
        font-size: 16px;
        ul,ol {font-size: 16px; color: #333333; margin-bottom: 24px;}
        }
    </style>

    <div class="s"">

        <b>The Castaway CTD</b> <br>

        The small, handy CastAway-CTD is a lightweight, easy-to-use instrument designed for quick and accurate conductivity, temperature and depth profiles.<br>
        <br>

        <b>What This App Does</b> <br>
        This app cleans Castaway CTD files to be ingested into the ODV software. It does the following:<br>
        <ul>
        <li>Extracts specific variables from the metadata rows of the files</li>
        <li>Removes the metadata rows</li>
        <li>Creates a data new table</li>
        <li>Adds variables extracted from the metadata to new table</li>
        <li>Adds any additional variables to the new table</li>
        <li>Organizes table so that it is ODV compatible</li>
        <li>Renames specific variable names</li>
        </ul>
        
        <b>Example File </b> <br>
                  
    </div>
    '''
    )
    st.sidebar.image("https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Castaway/img/img_example.png?ref_type=heads", use_container_width=True)

    #Download example files Widget
    main_path=os.path.abspath(os.curdir)
    full_path=main_path+'/Castaway/'
    
    _, _, files = next(os.walk(full_path))
    files=[f for f in files if 'example' in f]
    filepath=os.path.join(full_path,files[0])
    
    with open(filepath, "rb") as file:
        st.sidebar.download_button(
            label="Download Example CSV",
            data=file,
            file_name="example.csv",
            mime="text/csv",
            icon=":material/download:",
            )
    
    # Clear output data
    for f in os.listdir(full_path):
        if 'output' in f or 'example.csv' in f:
            os.remove(os.path.join(full_path, f))

    file_upload()


def file_upload(): 
    st.markdown('#### Upload CSV File(s) here')

    datafiles = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
    #If there are files uplaoded call get header widget function
    if datafiles!=[]:
        the_filenames=[d.name for d in datafiles if '.csv' in d.name] #check for csv files

        if the_filenames:
            get_header_widget(datafiles)

        else:
            left, right = st.columns(2)
            left.warning('Oops, please uplaod CSV files', icon="⚠️")

def get_header_widget(datafiles):
    f=0
    for datafile in datafiles:
        f=f+1
        if f==1: #Get the header row from the first file
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

            #Delimiter
            data_file_delimiter = ','
    
            #The max num of columns come from the last line
            max_col_num = len(last_line.split(data_file_delimiter)) + 1
    
            # Any rows with num of cols less than the max are likely metadata rows
            met_count=0
            for l in lines:
                #Count the column count for the current line
                col_count = len(l.split(data_file_delimiter)) + 1
                
                if col_count<max_col_num:
                    met_count=met_count+1
                else:
                    break
    
            header_row=met_count#met_count is 0 if there are no metadata rows
            
            # Get the metadata df to see if there is atually metadata
            df=pd.read_csv(datafile, header=header_row)
            datafile.seek(0) #Go back to beginning of file

            if header_row>0:
                if len(df.columns)>3 or 'Temperature (Celsius)'.casefold() in (name.casefold() for name in list(df.columns)):
                    
                    # Grab all the metadata before the actual data
                    metadata_df=pd.read_csv(datafile,nrows=header_row-1)
                    datafile.seek(0) #Go back to beginning of file
            else:
                metadata_df=pd.DataFrame()

    #Create Widgets
    st.markdown('')
    with st.container(border=True): 
        # Get the number of rows to remove
        st.markdown('#### Lets find the column headers and any metadata 🔎')
        
        #Create some columns so that the info box is not too long
        left, right = st.columns([0.8,0.2])
        left.info('All the information above your actual data is referred to as metadata', icon="ℹ️")
        
        if header_row!=None:
            st.markdown(f'**The header row seems to be row {header_row+1}:**')
            st.dataframe(df.head(0))
            st.markdown('**If that is incorrect, change it here. Otherwise, click Next**')

        else:
            st.markdown('**Please add your header row below (as shown in your csv viewer)**')

        #Clicked1 is for first button. It is set to false at first (not clicked yet)
        if 'clicked1' not in st.session_state:
            st.session_state.clicked1 = False

        # If the button is clicked, the session state is set to true (button is clicked)
        def click_button():
            st.session_state.clicked1 = True

        # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
        def change_num():
            st.session_state.clicked1 = False

        #Widget for accepting the header row number from user and next button
        left, right = st.columns(2)
        num=left.number_input("Insert header row",value=29, on_change=change_num)
        Next_button=left.button("Next", type="primary", key='1', on_click=click_button)

        #If you have clicked the next button
        if st.session_state.clicked1:
            # Header row from user
            header_row=num-2

            # Check if this is indeed the header row
            # Read the based on the input
            user_header_row=lines[header_row+1]
            #Count the number of columns in this header row
            user_header_row_count=len(user_header_row.split(data_file_delimiter))
              
            # df=pd.read_csv(datafile, header=header_row+1)
            #if len(df.columns)<3 or 'Temperature (Celsius)'.casefold() not in (name.casefold() for name in list(df.columns)):

            if user_header_row_count<3:
                left, right = st.columns([0.8,0.2])
                left.error('This does not look like a header row (the selected row is printed below)', icon="🚨")
                st.write(user_header_row)
            else:
                # Call next function
                if metadata_df.empty:
                    metadata_vars=[]
                    add_extra_vars_widget(header_row, metadata_vars, datafiles)
                else:
                    get_met_vars(header_row,datafiles,metadata_df)  

def get_met_vars(header_row,datafiles,metadata_df):

    st.markdown('#####')
    st.markdown('#### Ok, let\'s add some variables from the metadata to the new data table 🕺🏻')
    #Create some columns so that the info box is not too long
    left, right = st.columns([0.8,0.2])
    left.info('The values are to the right of these variables in the CSV file', icon="ℹ️")
    # Get the metadata variables from first metadata_df in list
    mcols=list(metadata_df.columns)
    
    #generate new col names
    mcols_len=len(mcols)
    newmcol_list=[]
    for i in range(0,mcols_len):
        newmcol=f'col{i}'
        newmcol_list.append(newmcol)

    #Add to metadata_df
    metadata_df.columns=newmcol_list #(col0, col1 etc)

    #first column with met variables
    col1=newmcol_list[0]
    col1_rows=metadata_df[col1].tolist()
    col1_rows=col1_rows[:-1]
    #Clean up the metadata variables exracted from column 1 of the metadta df
    allowed_rows=[]
    col1_rows_cleaned=[]
    for c in col1_rows:
        c=str(c)
        #remove special characters
        c2=re.sub(r"[^a-zA-Z0-9 ]+", '', c)
        c2=c2.strip()
        col1_rows_cleaned.append(c2)

        #typical met variables to extract
        if 'Cast time (UTC)' in c or 'Start latitude' in c or 'Start longitude' in c or 'File name' in c:
            allowed_rows.append(c2)


    #CREATE WIDGETS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    #Widgets
    left, right = st.columns([0.8,0.2])
    new_vars=left.multiselect("Click the dropdown menu below to add variables",options=col1_rows_cleaned
                              ,default=allowed_rows,placeholder="Select variables...", on_change=change_vars)
    Next_Button2=left.button("Next", type="primary", key='2', on_click=click_button)

    if st.session_state.clicked2:
        #Get chosen vars
        metadata_vars=new_vars
        # Call next function
        add_extra_vars_widget( header_row, metadata_vars, datafiles, col1_rows_cleaned,newmcol_list)

def add_extra_vars_widget( header_row, metadata_vars, datafiles, col1_rows_cleaned,newmcol_list):
    st.markdown('#####')
    st.markdown('#### Are there any new variables that you would like to add as columns to the merged file? 🤔')

    #CREATE WIDGETS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Create some columns so that the info box is not too long
    left, right = st.columns([0.8,0.2])
    left.info('This variable will have the same value throughout the column in the merged file.', icon="ℹ️")
    rb=st.radio("",["Yes", "No"], captions=["Yup, I wanna add variables", "Nah, I'm good"],index=None )

    if rb=='Yes':
        # Call next function
        how_many_vars_widget(header_row, metadata_vars, datafiles, col1_rows_cleaned,newmcol_list)

    elif rb=='No':
        var_list=[]
        var_values_list=[]
        remove_and_merge(var_list,var_values_list,header_row, metadata_vars, datafiles,col1_rows_cleaned,newmcol_list)

def how_many_vars_widget( header_row, metadata_vars, datafiles, col1_rows_cleaned, newmcol_list):
    st.markdown('#####')
    st.markdown('#### How many variables would you like to add? 🤓')

    #Clicked3 is for third button. It is set to false at first (not clicked yet)
    if 'clicked3' not in st.session_state:
        st.session_state.clicked3 = False

    # If the button is clicked, the session state is set to true (button is clicked)
    def click_button():
        st.session_state.clicked3 = True

    # If the number is changed, the session state is set to False (button is unclicked, so user has to click again)
    def change_num():
        st.session_state.clicked3 = False

    #Widget for accepting the header row number from user and next button
    left, right = st.columns(2)
    num3=left.number_input("Number of variables to add",value=2, on_change=change_num)
    Next_button=left.button("Next", type="primary", key='3', on_click=click_button)

    if st.session_state.clicked3==True:
        var_num=num3
        enter_vars_widget(var_num, header_row, metadata_vars,datafiles,col1_rows_cleaned, newmcol_list)

def enter_vars_widget(var_num, header_row, metadata_vars,datafiles,col1_rows_cleaned, newmcol_list):
    st.markdown('#####')
    st.markdown('#### Enter the variable names and their corresponding values:📝')

    txt_list=[]
    txt_values_list=[]

    #Set States
    if 'clicked4' not in st.session_state:
        st.session_state.clicked4 = False

    def click_button():
        st.session_state.clicked4 = True

    def change_name():
        st.session_state.clicked4 = False
    
    def change_val():
        st.session_state.clicked4 = False


    for c in range(0, var_num):      
        if c==0:
            the_var='Cruise'
            val='WK22'         
        elif c==1:
            the_var='Type'
            val='C'
        else:
            the_var=None
            val=None

        var_col, val_col = st.columns(2)

        # Widgets for getting the variable names and values
        var_name=var_col.text_input(f"Variable {c+1}", value=the_var, on_change=change_name)
        txt_list.append(var_name)

        var_value=val_col.text_input(f"Value of variable {c+1}",value=val, on_change=change_val)
        txt_values_list.append(var_value)

    Next_button=st.button("Next", type="primary", key='4', on_click=click_button)

    if st.session_state.clicked4==True:
        # Get the variable entries
        var_list=[]
        var_values_list=[]
        for t, tv in zip(txt_list, txt_values_list):
            var_list.append(t)
            var_values_list.append(tv)
            
        # Call next function
        remove_and_merge(var_list,var_values_list,header_row, metadata_vars, datafiles, col1_rows_cleaned, newmcol_list)

def remove_and_merge(var_list,var_values_list,header_row, metadata_vars, datafiles, col1_rows_cleaned, newmcol_list):
    #Progress loader
    #Create some columns so that the info box is not too long
    left, right = st.columns([0.8, 0.2])

    left.markdown('#####')
    left.markdown('#### Data Processing & Download ⬇️')
    left.info('OK, processing files...This might take a few seconds 🙂', icon="ℹ️")

    df_list_cleaned=[] #add cleaned dfs to this list
    plot_df_list=[] 
    f=0
    for file in datafiles:
        f=f+1
        file.seek(0) #Go back to beginning of file 
        df=pd.read_csv(file, header=header_row+1)

        if header_row>0:
            if len(df.columns)>3 or 'Temperature (Celsius)'.casefold() in (name.casefold() for name in list(df.columns)):
                
                # Grab all the metadata before the actual data
                file.seek(0) #Go back to beginning of file
                metadata_df=pd.read_csv(file,nrows=header_row-1)
        else:
            metadata_df=pd.DataFrame()

        if df.empty:
            continue

        if not metadata_df.empty:
            metadata_df.columns=newmcol_list #(col0, col1 etc)
    
            #first column with met variables
            col1=newmcol_list[0]

            #update metadata dfs with the cleaned variables (metadata_vars will be from this list)
            for i, c1 in zip(metadata_df.index,col1_rows_cleaned):
                metadata_df.at[i, col1] = c1
            
            # Grab the metadata vars that should be added as columns
            c=-1
            for mvar in metadata_vars:
    
                r_index=999
                c=c+1

                #Get the rows and columns in metadata_df where the string mvar is present (boolean values)
                ro=metadata_df.apply(lambda row: row.astype(str).str.contains(mvar,regex=False).any(), axis=1)
                rows_list=ro.tolist()
                co=metadata_df.apply(lambda column: column.astype(str).str.contains(mvar,regex=False).any(), axis=0)
                cols_list=co.tolist()
                
                # Get the indices for that variable name
                for rows in rows_list:    
                    if rows:
                        r_index=rows_list.index(rows)
    
                for cols in cols_list:
                    if cols:
                        c_index=cols_list.index(cols)
    
                if r_index!=999:                        
                    # Get the value
                    
                    value=metadata_df.iloc[r_index, c_index+1]
                    
                    if 'longitude' in mvar:
                        mvar=  'Longitude [degrees_east]'
                    if 'latitude' in mvar:
                        mvar= 'Latitude [degrees_north]'
                    # If there is a date-time variable:
                    if 'time' in mvar or 'date' in mvar or 'Time' in mvar or 'Date' in mvar:
                        year_str='Year'
                        month_str='Month'
                        day_str='Day'
                        hour_str='Hour'
                        min_str='Minute'
                        sec_str='Second'
                        
                        #If there are no seconds in the format
                        if len(value)==16:
                            value=value+':00'
                        
                        # Convert string to datetime
                        datetime_object = dt.strptime(value, '%Y-%m-%d %H:%M:%S')

                        #odv iso date format
                        iso_date=datetime_object.strftime("%Y-%m-%dT%H:%M:%S")
                        
                        #Convert datetime to individual strings->integers
                        year = int(datetime_object.strftime("%Y"))
                        month = int(datetime_object.strftime("%m"))
                        day = int(datetime_object.strftime("%d"))
                        hour = int(datetime_object.strftime("%H"))
                        minute = int(datetime_object.strftime("%M"))
                        second = int(datetime_object.strftime("%S"))
    
                        # Insert into dataframe
                        df.insert(c, "yyyy-mm-ddThh:mm:ss.sss",iso_date)
                        df.insert(c+1, year_str,year)
                        df.insert(c+2, month_str,month)
                        df.insert(c+3, day_str,day)
                        df.insert(c+4, hour_str,hour)
                        df.insert(c+5, min_str,minute)
                        df.insert(c+6, sec_str,second)
                        
                        c=c+6
                    else:
                        # Insert into dataframe
                        df.insert(c, mvar,value)
                else:
                    if f==1:
                        left.warning('The variable name **{}** was not found in the rows removed and was therefore not added to the final file.<br>Re-run notebook and enter the correct variable name if you made a mistake.<br><br>'.format(mvar), icon="ℹ️")
        
        # Get any additional vars that should be added to columns 
        c=-1
        for var,val in zip(var_list, var_values_list):   
            c=c+1
            if var != '':
                df.insert(c,var,val)
                
        # To omit certain varibales and rearrange--------------------------------------------------------------------
        all_cols=df.columns
        for col in all_cols:
            if "File name" in col:
                column_to_move = df.pop(col)
                # insert column with insert(location, column_name, column_value)
                df.insert(0, "Station", column_to_move)

            if 'Specific conductance' in col:
                df = df.drop(col, axis=1)
            if 'Sound velocity' in col:
                df = df.drop(col, axis=1)
            if 'Density' in col:
                df = df.drop(col, axis=1)

        #Make a copy of the df that has the filename as a column (for plotting in case the user removes file name)
        plot_df=df.copy()
        plot_df=plot_df.assign(File=file.name)
        
        #plot_df['File']=file['name']
        plot_df_list.append(plot_df)
        
        # ----------------------------------------------------------------------------------------------
        # Add data frames to a list
        df_list_cleaned.append(df)
        plot_df_list.append(plot_df)

       
        # Concatenate the list of data frames
        final_df=pd.concat(df_list_cleaned)  
        final_plot_df=pd.concat(plot_df_list)

        # Save as csv
        # csvname='output_cwout.csv'
        # csvname2='output_file.csv'
        # final_df.to_csv(csvname, index=False)
        # final_plot_df.to_csv(csvname2, index=False)

    #Call download function
    download_output(final_df, final_plot_df)

def download_output(final_df, final_plot_df):
    left, right = st.columns([0.8, 0.2])
    left.success('All Done! 🎉', icon="✅")

    csv=final_df.to_csv().encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="output.csv",
        mime="text/csv",
        icon=":material/download:",
        )


main()