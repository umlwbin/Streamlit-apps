import pandas as pd

def add_row(df, row_values, as_header=False):
    """
    Insert a new row at the top of the DataFrame.
    
    If as_header=True:
        - The inserted row becomes the new header.
        - Existing data is shifted down.
        - Column names are replaced by the new row values.
    """

    # Validate length
    if len(row_values) != len(df.columns):
        raise ValueError(f"Row has {len(row_values)} values but DataFrame has {len(df.columns)} columns.")

    # Create a DataFrame for the new row
    new_row_df = pd.DataFrame([row_values], columns=df.columns)

    if as_header:
        # Promote row to header
        new_header = [str(v) if pd.notna(v) else "" for v in row_values]

        # Shift data down
        df = pd.concat([df], ignore_index=True)

        # Replace header
        df.columns = new_header

        summary = {
            "operation": "add_row",
            "as_header": True,
            "new_header": new_header
        }
        return df, summary

    else:
        # Insert row at top
        df = pd.concat([new_row_df, df], ignore_index=True)

        summary = {
            "operation": "add_row",
            "as_header": False,
            "inserted_row": row_values
        }
        return df, summary
