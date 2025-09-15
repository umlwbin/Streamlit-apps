import streamlit as st
import pandas as pd


def pivot_widgets():
    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown(" ")
    st.markdown('##### Flipping your data! 🤸🏽‍♂️ ')


    # WIDGET CREATION --------------------------------------------   
    #Next Button
    st.button("Let's Go", type="primary", key='pivotContinue') 

    #IF NEXT BUTTON IS CLICKED
    if st.session_state.get("pivotContinue"): 
        task_inputs = {}              
        return task_inputs

#PROCESSING************************************************************************
def pivot(df):
    st.markdown("##### 📄 Original DataFrame")
    st.dataframe(df.head(5))

    # Step 2: Transpose the DataFrame
    df_transposed = df.T.reset_index()  

    # Step 3: Set the first row as header
    new_header = df_transposed.iloc[0]  # First row becomes header
    df_cleaned = df_transposed[1:]      # Remove the header row from data
    df_cleaned.columns = new_header     # Set new header

    # Step 4: Attempt to restore original data types
    # We'll infer types based on the original DataFrame
    for col in df.columns:
        if col in df_cleaned.columns:
            original_dtype = df[col].dtype
            try:
                df_cleaned[col] = df_cleaned[col].astype(original_dtype)
            except Exception as e:
                st.warning(f"Could not convert column '{col}' to {original_dtype}: {e}")

    st.markdown("##### 🔁 Transposed & Cleaned DataFrame")
    st.dataframe(df_cleaned.head(5))

    return df_cleaned