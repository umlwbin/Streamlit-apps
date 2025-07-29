import streamlit as st
from zipfile import ZipFile
import os


#Output Path
path=os.path.abspath(os.curdir)

def download_output(df_list):
    def on_download():
        st.balloons()
        st.session_state.new_upload=False
        #st.session_state.toggle = False

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