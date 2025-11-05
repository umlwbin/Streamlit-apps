import streamlit as st
import pandas as pd
import os

def create_csv_files(file, df, df_list):
    #Create the output CSV filename
    if st.session_state.version<=1 or st.session_state.toggle==False : # if we are using the filenames from the uploader
        #create the output file name
        output_filename=file.name[:-4]+'_cwout.csv' 

    else:#Toggle is ON - using previously edited files
        #Rename files
        newfilename=file[:-10]+'.csv' #remove the cwout from the filenames
        os.rename(file, newfilename) #rename the file

        # Add back cwout
        output_filename=newfilename[:-4]+'_cwout.csv' #create the output file name
        os.remove(newfilename) #Remove the old file (which now has the name- newfilename)

    #save the data frame as CSV using the above filename
    df.to_csv(output_filename, index=False)

    # Append new data frame to data frame list
    df_list.append(df)
    return df_list

def show_snapshot(df_list):
    st.markdown('')
    st.markdown('###### Here is a snapshot of your processed file!')
    st.write(df_list[0].head(5))