import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items


def redorder_widget(cols):
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown(" ")
    st.markdown('##### Organize column headers below')
    st.markdown(" ")

    # WIDGET CREATION --------------------------------------------  
    # Sort Items widget    
    var_list=sort_items(cols)  

    #Next Button
    st.button("Next", type="primary", key='reorderNext_WidgetKey') 

    #IF NEXT BUTTON IS CLICKED
    if st.session_state.get("reorderNext_WidgetKey"): 
        if var_list:
            task_inputs = {"reordered_variables": var_list}              
            return task_inputs
        
        else:
            st.error('You did not reorder 🙃', icon="🚨")


def reorder(df, reordered_variables):

    
    #PROCESSING************************************************************************
    #Create a new dataframe
    new_df=pd.DataFrame() 

    # Loop through the varibales as sorted by the widget and update new dataframe with the new order 
    try:
        for v in reordered_variables:  
            new_df[v]=df[v]
        return new_df
        
    except KeyError as e:
        st.error('There is an error with a column header, perhaps a special character. Please use the **Clean column headers** function and try again.', icon="🚨")
