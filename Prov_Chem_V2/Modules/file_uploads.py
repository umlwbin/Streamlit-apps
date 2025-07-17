import streamlit as st
import pandas as pd
import os


#PATHS----------------------------------------------------------------------------------------------------------------------------
#Input_path is where the script and any input files are found, output_path is where the output files are created -the current dir.
#input_path=os.path.abspath(os.curdir)+'/Prov_chem/' #For Streamlit Directory
input_path=os.path.abspath(os.curdir) #For desktop
output_path=os.path.abspath(os.curdir)
#----------------------------------------------------------------------------------------------------------------------------------


def fileupload_Widget():
    #Setting States
    if 'new_upload' not in st.session_state:
        st.session_state.new_upload=False

    st.markdown('')
    st.markdown('#### Upload CSV files here')

    def newUpload(): #on change fucntion
        st.session_state.new_upload=True
        st.session_state.toggleChange=False
        st.session_state.mergeRowsBegin = False
        st.session_state.pivotBegin = False
        
        st.session_state.begin3 = False
        st.session_state.begin4 = False
        st.session_state.begin5 = False
        st.session_state.begin6 = False

        # st.session_state.next1=False
        # st.session_state.next2=False
        # st.session_state.next3=False
        # st.session_state.next4=False
        # st.session_state.next5=False
        # st.session_state.next6=False
        # st.session_state.next7=False
        # st.session_state.NextButton_Parse=False
        st.session_state.allDone=False

    datafiles = st.file_uploader("Choose CSV files", accept_multiple_files=True, on_change=newUpload, type="csv", key='fileupload')

    #If there are files uploaded retrun them
    if st.session_state.new_upload:
        return datafiles

def example_file_widget():
    st.markdown("##### ")
    st.markdown("##### Try an example file!")

    def on_toggle():
        st.session_state.toggleChange=True
  
    example_on=st.toggle("Yep, use an example", on_change=on_toggle, key=st.session_state.toggleChange)

    if example_on and st.session_state.toggleChange==True:
        example_file=output_path+'/example_LWOsis.csv'
        return example_file



@st.cache_data  # 👈 Add the caching decorator so that this function is not run every time a widget is interacted with
def read_dfs(datafiles, inconsistent_cols_error):
    file_dfs_list=[]
    csvfileNames=[]
    c=0
    for file in datafiles:

        #Check if it is the example file
        if file==input_path+'/example_LWOsis.csv':
            fn=file[:-4]+'_curated.csv'
        else:
            fn=file.name[:-4]+'_curated.csv' #Get the original file names and create output filenames
        csvfileNames.append(fn) #Add filenames to a list to create the output files.
        c=c+1
        if c==1:
            #Do a check to see if the columns are consistent
            #--------------------------------------------------------------------------------
            try:
                df = pd.read_csv(file)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns

                st.markdown('######')
                st.markdown('##### Here is a snapshot of your original file:')
                st.write(df.head(10))
                file_dfs_list.append(df)
            except pd.errors.ParserError as e:
                inconsistent_cols_error=True
                return file_dfs_list,csvfileNames, inconsistent_cols_error
        else:
            df = pd.read_csv(file)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #Remove unnamed columns
            file_dfs_list.append(df)
            

    return file_dfs_list,csvfileNames, inconsistent_cols_error

