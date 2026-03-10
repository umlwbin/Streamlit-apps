import pandas as pd

def add_row(df, row_values=None, as_header=False, auto_headers=False):
    """
    Add a new row to the DataFrame or generate alphabetical headers.

    Summary returned:
        {
            "task_name": "add_row",
            "row_added": [...],     # or None
            "as_header": True/False
        }
    """

    # ---------------------------------------------------------
    # CASE 1: AUTO-GENERATE ALPHABETICAL HEADERS
    # ---------------------------------------------------------
    if auto_headers:
        # Recover the original first row (pandas used it as header)
        recovered_first_row = list(df.columns)

        # Insert the recovered row back into the data as row 0
        df = pd.concat(
            [pd.DataFrame([recovered_first_row], columns=df.columns), df],
            ignore_index=True
        )

        # Create alphabetical headers: A, B, C, ...
        new_header = [chr(65 + i) for i in range(len(df.columns))]
        df.columns = new_header

        summary = {
            "task_name": "add_row",
            "row_added": None,
            "as_header": True
        }
        return df, summary

    # ---------------------------------------------------------
    # CASE 2: NORMAL ADD ROW BEHAVIOR
    # ---------------------------------------------------------
    # Validate row length
    if len(row_values) != len(df.columns):
        raise ValueError(
            f"Row has {len(row_values)} values but DataFrame has {len(df.columns)} columns."
        )

    # Convert the list of values into a one-row DataFrame
    new_row_df = pd.DataFrame([row_values], columns=df.columns)

    # ---------------------------------------------------------
    # CASE 2A: PROMOTE ROW TO HEADER
    # ---------------------------------------------------------
    if as_header:
        # Insert the new row at the top
        df = pd.concat([new_row_df, df], ignore_index=True)

        # Convert row values into new column names
        new_header = [str(v) if pd.notna(v) else "" for v in row_values]
        df.columns = new_header

        # Remove the promoted row from the data
        df = df.iloc[1:].reset_index(drop=True)

        summary = {
            "task_name": "add_row",
            "row_added": None,
            "as_header": True
        }
        return df, summary

    # ---------------------------------------------------------
    # CASE 2B: INSERT ROW AS NORMAL DATA
    # ---------------------------------------------------------
    df = pd.concat([new_row_df, df], ignore_index=True)

    summary = {
        "task_name": "add_row",
        "row_added": row_values,
        "as_header": False
    }
    return df, summary
