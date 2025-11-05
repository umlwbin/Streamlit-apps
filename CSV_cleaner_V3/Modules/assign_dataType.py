import streamlit as st
import pandas as pd

'''
This task:
✅ Uploads a CSV 
✅ Infers column data types using pandas 
✅ Allows users to override those types via dropdowns 
✅ Applies the selected types (handling NaNs and datetime quirks) 
✅ Outputs a cleaned DataFrame ready for export
'''

def assign_widgets(df, cols):
    '''
    This function analyzes each column and returns the most likely data type
    - Numeric check comes first: avoids misclassifying numeric-looking strings as dates.
    - Date pattern check: only attempts datetime conversion if values resemble actual dates (e.g. 2023-09-05).
    - Threshold: requires at least 50% of values to look like dates before trying to convert.
    '''


    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    st.markdown("##### 🧬 Review & Adjust Column Data Types")

    def suggest_dtype(series):
        non_null = series.dropna().astype(str).str.strip().replace("", pd.NA)

        # Try numeric first
        try:
            numeric = pd.to_numeric(non_null, errors='raise')
            if numeric.apply(float.is_integer).all():
                return "int"
            else:
                return "float"
        except:
            pass

        # Try datetime — but only if values contain typical date patterns
        date_like = non_null.str.contains(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", regex=True)
        if date_like.mean() > 0.5:  # at least half look like dates
            try:
                pd.to_datetime(non_null, errors='raise')
                return "datetime"
            except:
                pass

        # Try boolean
        if non_null.str.lower().isin(["true", "false", "yes", "no", "1", "0"]).all():
            return "bool"

        return "str"


    # Define options for user to choose from
    type_options = ["int", "float", "str", "bool", "datetime"]

    # WIDGET CREATION---------------------------------------------
    user_selected_types = {} # Store user selections

    for col in cols:
        # Suggest type only if not already stored
        if col not in st.session_state.selected_types: 
            st.session_state.selected_types[col] = suggest_dtype(df[col])

        #Select Box Widget
        selected_type = st.selectbox(
            f"{col}:", 
            options=type_options, 
            index=type_options.index(st.session_state.selected_types[col]), key=f"type_select_{col}")
        
        st.session_state.selected_types[col] = selected_type
        user_selected_types[col] = selected_type

    #Next Button Widget
    st.button("Next", type="primary", key='assignNext_WidgetKey') 

    #IF NEXT BUTTON IS CLICKED
    if st.session_state.get("assignNext_WidgetKey"): 
        if user_selected_types:
            task_inputs = {"user_selected_types": user_selected_types}              
            return task_inputs
        
        else:
            st.error('You did not choose data types 🙃', icon="🚨")


#PROCESSING************************************************************************
def assign(df, user_selected_types):

    # --- Apply User-Selected Data Types ---
    #NaNs: This loop uses pandas nullable types like Int64 and boolean to preserve NaNs.
    cleaned_df = df.copy()
    for col, dtype in user_selected_types.items():
        cleaned_df[col] = convert_column(cleaned_df[col], dtype)

    return cleaned_df

def convert_column(col_data, dtype):
    '''
    This function handles:
    - Empty strings: Converted to pd.NA
    - Whitespace-only cells: Stripped and treated as missing
    - Mixed types: Coerced safely with fallback to NaN or original
    Boolean strings: Interprets "yes", "no", "1", "0" as True/False
    Datetime strings: Coerced with pd.to_datetime, invalid entries become NaT
    Nullable types: Uses Int64 and boolean to preserve missing values cleanly
    '''

    # Strip whitespace and replace empty strings with NaN
    cleaned = col_data.astype(str).str.strip().replace("", pd.NA)

    if dtype == "int":
        try:
            numeric = pd.to_numeric(cleaned, errors="coerce")
            # Use nullable Int64 to preserve NaNs
            return numeric.astype("Int64")
        except:
            return cleaned  # fallback to original if conversion fails

    elif dtype == "float":
        try:
            return pd.to_numeric(cleaned, errors="coerce")
        except:
            return cleaned

    elif dtype == "bool":
        # Normalize common boolean-like strings
        bool_map = {
            "true": True, "false": False,
            "yes": True, "no": False,
            "1": True, "0": False
        }
        lowered = cleaned.str.lower()
        mapped = lowered.map(bool_map).astype("boolean")
        return mapped

    elif dtype == "datetime":
        try:
            return pd.to_datetime(cleaned, errors="coerce")
        except:
            return cleaned

    elif dtype == "str":
        return cleaned.astype(str)

    else:
        return cleaned
