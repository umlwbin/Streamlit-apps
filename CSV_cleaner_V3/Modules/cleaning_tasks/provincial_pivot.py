import pandas as pd

def provincial_pivot(df, var_col, value_col, additional_params=None):
    """
    Provincial Chemistry Pivot
    --------------------------
    Restructures a provincial chemistry file where:
      - one column contains variable/parameter names
      - one column contains values
    Each variable becomes its own column, and optional metadata columns
    can be merged into the header names.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.
    var_col : str
        Column containing variable/parameter names.
    value_col : str
        Column containing values.
    additional_params : list[str] or None
        Optional metadata columns to merge into the header name.

    Returns
    -------
    cleaned_df : pandas.DataFrame
    summary : dict
        Summary of transformations performed.
    """

    # Make a copy to avoid modifying original
    df = df.copy()

    # Drop rows where variable is missing
    df = df[df[var_col].notna()].copy()

    # Extract unique variables
    variables = df[var_col].unique().tolist()

    filtered_dfs = []
    summary_details = []

    for var in variables:
        # Filter rows for this variable
        sub = df[df[var_col] == var].copy()

        # Rename VALUE column to the variable name
        new_col_name = var

        # Merge metadata into header if requested
        if additional_params:
            # Extract first-row metadata values
            meta_values = [str(sub[param].iloc[0]) for param in additional_params]
            meta_str = "_".join(meta_values)
            new_col_name = f"{var}_{meta_str}"

            # Drop metadata columns
            sub = sub.drop(columns=additional_params)

        # Rename VALUE → new header
        sub = sub.rename(columns={value_col: new_col_name})

        # Drop the variable column
        sub = sub.drop(columns=[var_col])

        # Move the new variable column to the end
        extracted = sub[new_col_name]
        sub = sub.drop(columns=[new_col_name])
        sub[new_col_name] = extracted

        # Reset index
        sub = sub.reset_index(drop=True)

        filtered_dfs.append(sub)

        summary_details.append({
            "variable": var,
            "new_column_name": new_col_name,
            "rows": len(sub)
        })

    # Merge all filtered variable tables vertically
    cleaned_df = pd.concat(filtered_dfs, ignore_index=True)

    # Build summary
    summary = {
        "variables_processed": len(variables),
        "variable_names": variables,
        "metadata_used": additional_params if additional_params else [],
        "details": summary_details
    }

    return cleaned_df, summary