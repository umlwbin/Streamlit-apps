import streamlit as st

def which_cols_widgets(cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown('##### Which columns would you like to remove?')

    # WIDGET CREATION -------------------------------------------- 
    left, right = st.columns([0.8,0.2])
    variables_to_remove = left.multiselect(label='Select columns',options=cols, key='remove1')
    left.button("Next", type="primary", key='removeColsNext_WidgetKey')

    #IF NEXT BUTTON IS CLICKED
    if st.session_state.get("removeColsNext_WidgetKey"):
        if variables_to_remove:
            task_inputs = {"variables_to_remove": variables_to_remove}
            return task_inputs
        else:
            left.error('Please enter one or more columns!', icon="🚨")



def remove_cols(df, variables_to_remove):
    # PROCESSING *************************************
    processed_df=df.drop(columns=variables_to_remove) # Drop columns
    return processed_df

 