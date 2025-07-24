import streamlit as st
import os


def download_view_widgets(cleaned_df_list):
    if cleaned_df_list==None or cleaned_df_list==[]:
        st.info('No processing has been done yet!',icon="ℹ️")
    else:
        st.markdown('#### 👩🏽‍💻 Data Download')
        st.success('Processed Files Updated! 🎉', icon="✅")
        st.markdown(' The processed files are updated after each step. Click **Ready to Download** to convert files to CSV for downloading.')
        st.markdown(' ######')
        st.markdown(' ###### Snapshot of your processed file so far:')
        st.dataframe(cleaned_df_list[0].head(20) )

    def on_change():
        st.session_state.allDone=True

        st.session_state.mergeRowsBegin = False
        st.session_state.pivotBegin = False
        st.session_state.headersBegin = False
        st.session_state.isoBegin = False
        st.session_state.parseBegin = False
        st.session_state.rvqBegin = False

        st.session_state.mergeRowsNext1=False
        st.session_state.PivotNext1=False
        st.session_state.PivotNext2=False
        st.session_state.isoNext1=False
        st.session_state.isoNext2=False
        st.session_state.parseNext1 = False
        st.session_state.rvqNext1=False
        st.session_state.rvqNext2=False

    st.button('Ready to Download!', on_click=on_change)



def download_output(output_path, cleaned_df_list, csvfileNames, supplementary_df_list):
    
    #Donwload button function
    def downloadButton(lab, fp, filename, mi):
        def on_download_click():
            st.session_state.allDone=False
            st.balloons()

        st.download_button(label=lab,data=fp, file_name=filename, mime=mi,
                           icon=":material/download:", on_click=on_download_click)

    #How many total output files do we have? #The supplementary list contains all extra files created (files other than the processed uplaoded files)
    file_count = len(cleaned_df_list+supplementary_df_list) 

    #Just one file
    if file_count==1:
        filename=csvfileNames[0]
        fp=cleaned_df_list[0].to_csv().encode("utf-8")

        #Create download button
        downloadButton("Download CSV", fp, filename, "text/csv" )


    #Mulitple files - create zip file
    if file_count>1:
        from os.path import basename
        from zipfile import ZipFile

        filename='output_data.zip'
        with ZipFile(filename, 'w') as zipObj:

            # Iterate over all dfs and create CSV files
            for df, csv in zip(cleaned_df_list,csvfileNames):
                df.to_csv(csv,index=False)

            #Get all output files including supplementary files
            _, _, files = next(os.walk(output_path))
            files=[f for f in files if '_curated' in f]

            #Add each file to zipped file
            for file in files:
                filePath = os.path.join(output_path, file)
                zipObj.write(filePath, basename(filePath))

        #Create download button
        with open(filename, "rb") as fp:
            downloadButton("Download ZIP", fp, filename, "application/zip" )