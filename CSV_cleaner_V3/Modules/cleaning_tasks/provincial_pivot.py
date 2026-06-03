import pandas as pd


def provincial_pivot(
    df: pd.DataFrame,
    *,
    var_col,
    value_col,
    additional_params=None,
    **kwargs
):
    """
    Pivot a provincial chemistry dataset where variables are stored in rows.

    This task restructures a dataset where:
    - one column contains variable/parameter names
    - one column contains values
    - optional metadata columns can be merged into the final header names

    Each unique variable becomes its own column. Metadata values (if provided)
    are appended to the header name using underscores.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    var_col : str
        Column containing variable/parameter names.

    value_col : str
        Column containing values.

    additional_params : list[str] or None, optional
        Optional metadata columns whose first-row values will be merged into
        the new header names.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A vertically concatenated table where each variable becomes its own
        column, with metadata optionally merged into the header.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    for col in [var_col, value_col]:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' does not exist in the dataset.")

    if additional_params is not None:
        if not isinstance(additional_params, list) or not all(isinstance(x, str) for x in additional_params):
            raise ValueError("additional_params must be a list of strings or None.")

        for col in additional_params:
            if col not in df.columns:
                raise ValueError(f"Metadata column '{col}' listed in additional_params does not exist.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    # Drop rows where variable is missing
    cleaned_df = cleaned_df[cleaned_df[var_col].notna()].copy()

    variables = cleaned_df[var_col].unique().tolist()
    filtered_dfs = []

    for var in variables:
        sub = cleaned_df[cleaned_df[var_col] == var].copy()

        # Base column name
        new_col_name = var

        # Merge metadata into header
        if additional_params:
            meta_values = []
            for param in additional_params:
                first_val = sub[param].dropna().iloc[0] if sub[param].notna().any() else "NA"
                meta_values.append(str(first_val))

            meta_str = "_".join(meta_values)
            new_col_name = f"{var}_{meta_str}"

            # Drop metadata columns
            sub = sub.drop(columns=additional_params)

        # Rename value column
        sub = sub.rename(columns={value_col: new_col_name})

        # Drop variable column
        sub = sub.drop(columns=[var_col])

        # Move new column to end
        extracted = sub[new_col_name]
        sub = sub.drop(columns=[new_col_name])
        sub[new_col_name] = extracted

        sub = sub.reset_index(drop=True)
        filtered_dfs.append(sub)

    # Merge vertically
    final_df = pd.concat(filtered_dfs, ignore_index=True)

    # -----------------------------------------------------
    # 3. RETURN
    # -----------------------------------------------------
    return final_df
