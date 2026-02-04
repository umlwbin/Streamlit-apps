# ------------------------------------------------------------
# GENERAL HELPER FUNCTIONS
# ------------------------------------------------------------

def safe_insert_column(df, col_name, value):
    """
    Insert a column at the front of the DataFrame.
    If the column already exists, overwrite it instead of inserting.
    """
    if col_name not in df.columns:
        df.insert(0, col_name, value)
    else:
        df[col_name] = value


def drop_columns(df, omit_list):
    """
    Drop columns that appear in omit_list.
    Ignores any names that are not present in the DataFrame.
    """
    cols_to_drop = [c for c in omit_list if c in df.columns]
    return df.drop(columns=cols_to_drop)
