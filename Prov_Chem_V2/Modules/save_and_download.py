import streamlit as st
import os



def save_raw_files_if_no_rvq(df_merged,csv):
    st.info('No RVQ Variable was selected, downloading files!')
    df_merged.to_csv(csv, index=False) # Save as csv file


def download_view_widgets(cleaned_df_list):
    if cleaned_df_list==None or cleaned_df_list==[]:
        st.info('No processing has been done yet!',icon="ℹ️")
    else:
        st.markdown('#### 👩🏽‍💻 Data Download')
        st.success('Processed Files Updated! 🎉', icon="✅")
        st.markdown(' The processed files are updated after each step. Click **Ready to Download** to convert files to CSV for downloading.')
        st.markdown(' ######')
        st.markdown(' ###### Snapshot of your processed file so far:')
        st.write(cleaned_df_list[0].head(20))

    def on_change():
        st.session_state.allDone=True
    st.button('Ready to Download!', on_click=on_change)

def download_output(output_path, cleaned_df_list, csvfileNames, supplementary_df_list):

    from zipfile import ZipFile
    def on_download():
        st.balloons()

    file_count = len(cleaned_df_list+supplementary_df_list)

    if file_count==1:
        filename=csvfileNames[0]
        fp=cleaned_df_list[0].to_csv().encode("utf-8")
        st.download_button(
        label="Download CSV",data=fp,file_name=filename,mime="text/csv",
        icon=":material/download:",on_click=on_download)

    if file_count>1:
        filename='output_data.zip'
        from os.path import basename
        with ZipFile(filename, 'w') as zipObj:

            # Iterate over all dfs and create CSV files
            for df, csv in zip(cleaned_df_list,csvfileNames):
                df.to_csv(csv, index=False)

            #Get all output files including supplementary files
            _, _, files = next(os.walk(output_path))
            files=[f for f in files if '_curated' in f]
            file_count = len(files)

            for file in files:
                filePath = os.path.join(output_path, file)
                # Add file to zip
                zipObj.write(filePath, basename(filePath))
        
        with open(filename, "rb") as fp:
            st.download_button(label="Download ZIP",data=fp,file_name=filename,
            mime="application/zip",icon=":material/download:", on_click=on_download)