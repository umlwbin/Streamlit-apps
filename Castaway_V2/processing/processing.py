import pandas as pd

# Import name cleaning + normalization helpers
from processing.normalizing_headers import clean_metadata_name, normalize_column_name

# Import general utilities
from processing.helpers import safe_insert_column, drop_columns


# ------------------------------------------------------------
# FINAL DATAFRAME BUILDER
# ------------------------------------------------------------

def build_final_dataframe(
    data_list,
    metadata_list,
    selected_vars,
    new_vars,
    omit_list,
    normalization_mode="Keep cleaned names"
):
    """
    Build the final cleaned dataset by combining:
    - The extracted data tables
    - Selected metadata variables
    - Optional new variables added by the curator
    - Columns the curator wants to omit
    - Column name normalization (snake_case, ODV, etc.)

    This function processes each file independently, then concatenates
    all cleaned files into one final DataFrame.

    Parameters
    ----------
    data_list : list of DataFrames
        The parsed data tables from each Castaway file.

    metadata_list : list of DataFrames
        The parsed metadata tables from each Castaway file.

    selected_vars : list of str
        Metadata variable names chosen by the curator.

    new_vars : dict
        Optional new variables to insert (name → value).

    omit_list : list of str
        Column names to remove from the final dataset.

    normalization_mode : str
        How to normalize column names:
        - "Keep cleaned names"
        - "snake_case"
        - "ODV-friendly (UPPERCASE_UNDERSCORES)"

    Returns
    -------
    DataFrame
        A single concatenated DataFrame containing all cleaned files.
    """

    final_frames = []

    # Process each file's data + metadata together
    for df, meta in zip(data_list, metadata_list):

        # Remove empty metadata columns
        meta = meta.dropna(axis=1, how="all")

        # --------------------------------------------------------
        # 1. Insert selected metadata variables into the data table
        # --------------------------------------------------------
        for var in selected_vars:
            var_clean = clean_metadata_name(var)

            # Find matching metadata row
            row = meta[meta["Variable"].astype(str).str.contains(var, regex=False)]

            if not row.empty:
                value = row["Value"].iloc[0]
                safe_insert_column(df, var_clean, value)

        # --------------------------------------------------------
        # 2. Insert new user-defined variables
        # --------------------------------------------------------
        for name, value in new_vars.items():
            safe_insert_column(df, name, value)

        # --------------------------------------------------------
        # 3. Remove unwanted columns
        # --------------------------------------------------------
        df = drop_columns(df, omit_list)

        # --------------------------------------------------------
        # 4. Normalize column names
        # --------------------------------------------------------
        df.columns = [
            normalize_column_name(col, normalization_mode)
            for col in df.columns
        ]

        final_frames.append(df)

    # Combine all cleaned files into one dataset
    return pd.concat(final_frames, ignore_index=True)
