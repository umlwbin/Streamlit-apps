import streamlit as st

def rename_cols_widgets(cols):

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('#### Enter the variable names that should be used in your processed output file(s)')
    left, right = st.columns([0.8,0.2])

    # WIDGET CREATION ---------------------------------------------------------------       
    #Dropdown lists for variable names
    stNames=list()
    col1, col2=st.columns(2)
    for c in range(0,len(cols)):
        stan=col1.text_input(label=f' Variable in file: {cols[c]}', value=cols[c]) #user text input
        stNames.append(stan) # append to the standardized names list

    # Widget for next button
    col1.button("Next", type="primary", key='renameNext_WidgetKey')
    #--------------------------------------------------------------------------------------------  

    if st.session_state.get("renameNext_WidgetKey"):# If button is clicked
        if stNames:
            task_inputs = {"standardized_names": stNames}
            return task_inputs
        else:
            st.error('Nothing was entered!', icon="🚨")
        

def rename_cols(df,standardized_names):
    # PROCESS
    # Check if the number of columns in the DataFrame matches the length of the list
    if len(df.columns) == len(standardized_names):            
        
        #Replace column names
        df.columns=standardized_names
        return df
    else:
        st.warning('Some files had different column lengths, those files were not changed. Please uplaod files with the same headers.', icon="⚠️")


