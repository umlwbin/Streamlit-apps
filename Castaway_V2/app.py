import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO
import io
import re
import os
from datetime import datetime as dt

#PATHS----------------------------------------------------------------------------------------------------------------------------
#Input_path is where the script and any input files are found, output_path is where the output files are created -the current dir.
#input_path=os.path.abspath(os.curdir)+'/Castaway/' #For Streamlit Directory
input_path=os.path.abspath(os.curdir) #For desktop
output_path=os.path.abspath(os.curdir)
#----------------------------------------------------------------------------------------------------------------------------------

#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

def main():
    # ============================================
    # SIDEBAR - APP INTRO
    # ============================================
    with st.sidebar:
        # GEt CanWIN Logo
        logo='https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Vocab%20app/UM-EarthObservationScience-cmyk-left.png?ref_type=heads'
        st.image(logo, width=250)

        # Title and Description
        st.title('Castaway CTD Processor ⛴️')
        
        st.image("https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Castaway/img/ctd.jpg", width=60)
        st.markdown("The small, handy CastAway-CTD is a lightweight, easy-to-use instrument designed for quick and accurate conductivity, temperature and depth profiles.")

        with st.expander("**What This App Does**"):
            intro="""
                This app cleans Castaway CTD files to be ingested into the ODV software. It does the following:
                
                - Extracts specific variables from the metadata rows of the files
                
                -  Removes the metadata rows

                - Creates a data new table

                - Adds variables extracted from the metadata to new table

                - Adds any additional variables to the new table

                - Organizes table so that it is ODV compatible

                - Renames specific variable names 

                """
            st.markdown(intro)

        st.markdown("")
        st.markdown("### Example File")
        st.image("https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/-/raw/master/Apps/Castaway/img/img_example.png?ref_type=heads", use_container_width=True)


        #Download example files Widget
        _, _, files = next(os.walk(input_path))
        files=[f for f in files if 'example' in f]
        filepath=os.path.join(input_path,files[0])   

        with open(filepath, "rb") as file:
            st.download_button(
                label="Download Example CSV",
                data=file,
                file_name="example.csv",
                mime="text/csv",
                icon=":material/download:",
                )
        
    # Clear output data
    for f in os.listdir(output_path):
        if 'output' in f or 'example.csv' in f:
            os.remove(os.path.join(output_path, f))

    file_upload()


def file_upload(): 
    # ============================================
    # FILE UPLAODS
    # ============================================
    st.markdown('#### Upload CSV File(s) here')
    
    #Set the session state. After downloads, this gets set to False, so that the app returns to the file upload step. 
    if 'new_upload' not in st.session_state:
        st.session_state.new_upload=False

    #File uploader widget
    def newUpload(): #on change fucntion
        st.session_state.new_upload=True
        st.session_state.clicked1 = False
        st.session_state.clicked2 = False
        st.session_state.clicked3 = False
        st.session_state.clicked4 = False

    datafiles=st.file_uploader("Choose a CSV file", accept_multiple_files=True, on_change=newUpload, type="csv")
    
    #If there are files uplaoded call get header widget function
    if st.session_state.new_upload:
        if datafiles:
            get_data_metadata_tables(datafiles)

        else:
            left, right = st.columns(2)
            left.warning('Oops, please uplaod CSV files', icon="⚠️")



def get_data_metadata_tables(datafiles):
    # ============================================
    # GRAB THE METADTA AND THE DATA
    # ============================================

    f=0
    all_dfs=[]
    all_metadata_dfs=[]

    for datafile in datafiles:
        f=f+1

        # Read file as text
        content = datafile.getvalue().decode("utf-8")
        lines = content.splitlines()

        metadata_rows = []
        data_start_index = None

        # Identify metadata and data start
        for i, line in enumerate(lines):
            parts = line.split(",")
            if len(parts) <3:
                metadata_rows.append(parts)
            else:
                if len(parts)>= 3 and any("Temperature" in col for col in parts) :
                    data_start_index = i
                    break

        # Convert metadata to DataFrame
        metadata_df = pd.DataFrame(metadata_rows, columns=["Variable", "Value"])

        # Read actual data using pandas
        data_str = "\n".join(lines[data_start_index:])
        df = pd.read_csv(io.StringIO(data_str))

        #Save the dataframes
        all_dfs.append(df)
        all_metadata_dfs.append(metadata_df)

        # Display both just once
        if f==1:
            st. markdown("##### Awesome! This is what your metadata and data tables look like:")

            with st.expander("**Expand to see tables**"):
                st.markdown(" Metadata")
                st.dataframe(metadata_df.head(5))

                st.markdown("Data Table")
                st.dataframe(df.head(5))
    get_met_vars(all_dfs,all_metadata_dfs )

def get_met_vars(all_dfs,all_metadata_dfs):
    st.markdown('#####')
    st.markdown('#### Ok, let\'s add some variables from the metadata to the new data table 🕺🏻')
    left, right = st.columns([0.8,0.2])
    left.info('The values are to the right of these variables, see the table above', icon="ℹ️")
    
    # Get the metadata variables from first metadata_df in list
    original_metadata_cols=list(all_metadata_dfs[0].columns)
    
    #generate new header names for meatadata_df
    length_original_metadata_cols=len(original_metadata_cols)

    new_metadata_columns_list=[]
    for i in range(0,length_original_metadata_cols):
        new_metadata_columns_list.append(f'col{i}')

    #Generate new column names for metadata_dfs using the first metadata df
    all_metadata_dfs[0].columns=new_metadata_columns_list #(col0, col1 etc)

    # Get the variables in first col of metadata table, 
    col1=new_metadata_columns_list[0]
    col1_rows=all_metadata_dfs[0][col1].tolist()
    col1_rows=col1_rows[:-1]

    #Clean up the metadata variables exracted from column 1 of the metadta df. 
    # This cleaned list will appear in the dropdown menu for users to select a variable from the metadata
    allowed_rows=[]
    cleaned_metadata_variables=[]
    for c in col1_rows:
        c=str(c)
        #remove special characters
        c2=re.sub(r"[^a-zA-Z0-9 ]+", '', c)
        c2=c2.strip()
        cleaned_metadata_variables.append(c2)

        #Typical met variables to extract
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
    #Get chosen vars
    metadata_vars_to_add=left.multiselect("Click the dropdown menu below to add variables",options=cleaned_metadata_variables
                              ,default=allowed_rows,placeholder="Select variables...", on_change=change_vars)
    left.button("Next", type="primary", key='2', on_click=click_button)

    if st.session_state.clicked2:
        # Call next function
        add_extra_vars_widget( all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list)

def add_extra_vars_widget(all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list):
    st.markdown('#####')
    st.markdown('#### Are there any **new** variables that you would like to add as columns to the merged file? 🤔')

    #CREATE WIDGETS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Create some columns so that the info box is not too long
    left, right = st.columns([0.8,0.2])
    left.info('This variable will have the same value throughout the column in the merged file.', icon="ℹ️")
    rb=st.radio(" ",["Yes", "No"], captions=["Yup, I wanna add variables", "Nah, I'm good"],index=None )

    if rb=='Yes':
        # Call next function
        how_many_vars_widget(all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list)

    elif rb=='No':
        new_variables_to_add_list=[]
        values_of_new_variables_list=[]
        remove_and_merge(new_variables_to_add_list,values_of_new_variables_list,all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list)


def how_many_vars_widget(all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list):
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
    num_of_new_vars_to_add=left.number_input("Number of variables to add",value=2, on_change=change_num)
    left.button("Next", type="primary", key='3', on_click=click_button)

    if st.session_state.clicked3==True:
        enter_vars_widget(num_of_new_vars_to_add, all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list)


def enter_vars_widget(num_of_new_vars_to_add, all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list):
    st.markdown('#####')
    st.markdown('#### Enter the variable names and their corresponding values:📝')

    new_variables_to_add_list=[]
    values_of_new_variables_list=[]

    #Set States
    if 'clicked4' not in st.session_state:
        st.session_state.clicked4 = False

    def click_button():
        st.session_state.clicked4 = True

    def change_name():
        st.session_state.clicked4 = False
    
    def change_val():
        st.session_state.clicked4 = False


    for c in range(0, num_of_new_vars_to_add):      
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
        new_variables_to_add_list.append(var_name)

        var_value=val_col.text_input(f"Value of variable {c+1}",value=val, on_change=change_val)
        values_of_new_variables_list.append(var_value)

    st.button("Next", type="primary", key='4', on_click=click_button)

    if st.session_state.clicked4==True:      
        # Call next function
        remove_and_merge(new_variables_to_add_list,values_of_new_variables_list,all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list)

def remove_and_merge(new_variables_to_add_list,values_of_new_variables_list,all_dfs,all_metadata_dfs, metadata_vars_to_add, cleaned_metadata_variables, new_metadata_columns_list):

    left, right = st.columns([0.8, 0.2])
    left.markdown('#####')
    left.markdown('#### Data Processing & Download ⬇️')
    left.info('OK, processing files...This might take a few seconds 🙂', icon="ℹ️")

    df_list_cleaned=[] #add cleaned dfs to this list
    f=0

    # ============================================
    # PROCESSING STEPS
    # ============================================

    for df, metadata_df in zip(all_dfs, all_metadata_dfs):
        if not metadata_df.empty and not df.empty:
            metadata_df = metadata_df.loc[:, ~metadata_df.columns.str.contains('^Unnamed')] #Remove unnamed columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns

            metadata_df.columns=new_metadata_columns_list #(col0, col1 etc)
            col1=new_metadata_columns_list[0] # This is the first column with metadata variables

            # Update metadata dfs with the cleaned variables (metadata_vars_to_add will be selected from this list)
            for i, c1 in zip(metadata_df.index,cleaned_metadata_variables):
                metadata_df.at[i, col1] = c1
            
            #--------------------------------------------------------------------------------------
            # 1. Grab the metadata vars that should be added as columns and add them to the data table
            c=-1
            for mvar in metadata_vars_to_add:
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

                    # Get the value of the metadata variable
                    value=metadata_df.iloc[r_index, c_index+1]
                    
                    if 'longitude' in mvar:
                        mvar=  'Longitude [degrees_east]'
                    if 'latitude' in mvar:
                        mvar= 'Latitude [degrees_north]'
                    
                    # If there is a date-time variable, separate out into yr, month, day, time:
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

            #--------------------------------------------------------------------------------------
            # 2. Get any additional (new) variables that should be added to columns 
            c=-1
            for var,val in zip(new_variables_to_add_list, values_of_new_variables_list):   
                c=c+1
                if var != '':
                    df.insert(c,var,val)

            #--------------------------------------------------------------------------------------
            # 3. omit certain variables and rearrange  
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
            
            # -----------------------------------------------------------------------------------------
            # 4. Add data frames to a list
            df_list_cleaned.append(df)

        # -----------------------------------------------------------------------------------------
    # 5. Concatenate the list of data frames
    final_df=pd.concat(df_list_cleaned)  

    #Call download function
    download_output(final_df)

def download_output(final_df):
    st.markdown('######')
    st.markdown('#### Data Download')
    left, right = st.columns([0.6, 0.4])
    left.success('All Done! 🎉', icon="✅")

    def on_download():
        st.balloons()
        st.session_state.new_upload=False

    csv=final_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="output.csv",
        mime="text/csv",
        icon=":material/download:",
        on_click=on_download
        )


main()