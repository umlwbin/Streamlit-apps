import pandas as pd
import streamlit as st

def remove_rows(df, *, filename, row_index, **kwargs):
    """
    Remove a single row by its CURRENT index.
    
    Updating row_map:
    In Streamlit, row_map is stored in session_state and must be updated
    because removing a row changes the mapping between:
    original_row_number  and the current_row_position

    If using this function OUTSIDE Streamlit, you must maintain your own row_map manually:
         old_map = list(range(1, len(df) + 1))
         new_map = [old_map[i] for i in range(len(old_map)) if i != row_index]
    """

    # ---------------------------------------------------------
    # 1. VALIDATION (hard)
    # ---------------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if not isinstance(row_index, int):
        raise ValueError("row_index must be an integer.")

    if row_index < 0 or row_index >= len(df):
        raise ValueError(f"Row index {row_index} is out of bounds for this dataset.")

    # ---------------------------------------------------------
    # 2. CORE PROCESSING
    # ---------------------------------------------------------
    cleaned_df = df.drop(index=row_index).reset_index(drop=True)

    # ---------------------------------------------------------
    # 3. UPDATE ROW MAP (Streamlit mode)
    # ---------------------------------------------------------
    old_map = st.session_state.row_map[filename]
    new_map = [old_map[i] for i in range(len(old_map)) if i != row_index]
    st.session_state.row_map[filename] = new_map

    # ---------------------------------------------------------
    # 4. RETURN
    # ---------------------------------------------------------
    # No metadata for this task
    return cleaned_df
