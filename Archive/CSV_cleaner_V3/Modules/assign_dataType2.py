import streamlit as st
import pandas as pd
import string

'''
This task:
✅ Uploads a CSV 
✅ Infers column data types using pandas 
✅ Allows users to override those types via dropdowns 
✅ Applies the selected types (handling NaNs and datetime quirks) 
✅ Outputs a cleaned DataFrame ready for export
'''

def assign_widgets(df):

    # INTRO WIDGETS FOR FUNCTION---------------------------------------------
    
    st.markdown("#### 👀 Column Preview")
    
    # 1. Preview Table with Index and Excel-style Letters

    #Convert Excel label to index
    def excel_label_to_index(label: str) -> int:
        label = label.upper()
        index = 0
        for i, char in enumerate(reversed(label)):
            index += (ord(char) - 64) * (26 ** i)
        return index - 1  # zero-based

    #Convert index to Excel label
    def excel_index_to_label(n: int) -> str:
        """Convert a zero-based column index to Excel-style letters."""
        result = ""
        while n >= 0:
            n, remainder = divmod(n, 26)
            result = chr(65 + remainder) + result
            n -= 1
        return result

    preview = df.head(2).copy()
    preview.columns = [f"{excel_index_to_label(i)} | {col}" for i, col in enumerate(df.columns)]
    st.dataframe(preview)


    # Parse letter range function
    def parse_range(input_str: str, df: pd.DataFrame) -> list:
        input_str = input_str.replace(" ", "").upper()
        if "-" not in input_str:
            return []

        start_label, end_label = input_str.split("-")
        try:
            start_idx = excel_label_to_index(start_label)
            end_idx = excel_label_to_index(end_label)
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
            return df.columns[start_idx:end_idx+1].tolist()
        except Exception:
            return []


    
    # 2. Create widgets to get the selected columns for each data type
    st.markdown(" ")
    st.markdown("#### ✍🏼 Assign Columns to Data Types")

    type_mapping = {}
    for dtype in ["date", "integer", "float", "string"]:
        with st.expander(f"Expand to select **{dtype.capitalize()}** columns"):
            #with st.container(border=True):

            st.markdown(f"###### {dtype.capitalize()} Columns")

            if dtype=="date":
                label=f"Select columns for {dtype} - **Columns with full dates only**"
            else:
                label=f"Select columns for {dtype}"
            st.multiselect(label, options=df.columns.tolist(),key=f"{dtype}_select")
            st.text_input(f"Or enter column range (e.g., B-F)",key=f"{dtype}_range")


    # 🔁 Rebuild mapping dynamically from session state
    type_mapping = {
        col: dtype
        for dtype in ["date", "integer", "float", "string"]
        for col in list(set(
            st.session_state.get(f"{dtype}_select", []) +
            parse_range(st.session_state.get(f"{dtype}_range", ""),df)
        ))
    }

    # 📋 Live summary
    if type_mapping:
        st.markdown(" ")
        st.markdown("##### 📋 Live Summary of Column Type Assignments")
        labeled_summary = []

        with st.expander("Expand for summary"):
            for i, col in enumerate(df.columns):
                if col in type_mapping:
                    label = excel_index_to_label(i)
                    labeled_summary.append((f"{label} | {col}", type_mapping[col]))

            summary_df = pd.DataFrame(labeled_summary, columns=["Column (Label)", "Assigned Type"])
            st.dataframe(summary_df.sort_values(by="Assigned Type"), use_container_width=True)
    else:
        st.info("No columns selected yet.")


    #Next Button Widget
    st.button("Next", type="primary", key='assignNext_WidgetKey') 

    #IF NEXT BUTTON IS CLICKED
    if st.session_state.get('assignNext_WidgetKey'):
        if type_mapping !={}:

            task_inputs = {"type_mapping":type_mapping}              
            return task_inputs
        else:
            st.warning("No columns were selected!", icon="⚠️")



#PROCESSING************************************************************************

def assign(df, type_mapping):

    df_converted = df.copy()

    converters = {
        "date": lambda s: pd.to_datetime(s, errors='coerce'),
        "integer": lambda s: pd.to_numeric(s, errors='coerce').astype("Int64"),
        "float": lambda s: pd.to_numeric(s, errors='coerce').astype(float),
        "string": lambda s: s.astype(str)
    }

    for col, dtype in type_mapping.items():
        if col in df_converted.columns:
            try:
                df_converted[col] = converters[dtype](df_converted[col])
            except Exception as e:
                st.warning(f"⚠️ Could not convert '{col}' to {dtype}: {e}")
    return df_converted