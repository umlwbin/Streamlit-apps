import pandas as pd

def remove_metadata_rows(df, identifiers):
    """
    Remove metadata rows that appear above the true header row.

    Parameters
    ----------
    df : pandas.DataFrame
        The input dataset, possibly containing metadata rows above the header.

    identifiers : list[str]
        A list of three strings that must appear in the true header row.
        Matching is case-insensitive and whitespace-trimmed.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        The DataFrame with metadata rows removed and the detected header applied.

    summary : dict
        A minimal summary containing:
            {
                "task_name": "remove_metadata_rows",
                "metadata_preview": [... up to 10 rows ...]
            }
    """

    def make_unique(names):
        """
        Ensure column names are unique by adding suffixes _1, _2, etc.
        """
        seen = {}
        unique = []

        for name in names:
            if name not in seen:
                seen[name] = 0
                unique.append(name)
            else:
                seen[name] += 1
                new_name = f"{name}_{seen[name]}"
                unique.append(new_name)

        return unique



    # Normalize identifiers for comparison
    identifiers = [str(x).strip().lower() for x in identifiers]

    # Convert all cell values to strings for safe comparison
    df_str = df.astype(str).applymap(lambda x: x.strip().lower())

    header_index = None

    # Scan each row to find the header row
    for idx, row in df_str.iterrows():
        row_values = set(row.tolist())
        if all(identifier in row_values for identifier in identifiers):
            header_index = idx
            break

    if header_index is None:
        # No header row found; return original df unchanged
        summary = {
            "task_name": "remove_metadata_rows",
            "metadata_preview": []
        }
        return df.copy(), summary

    # Extract metadata rows above the header
    metadata_df = df.iloc[:header_index].copy()

    # Promote the detected header row to column names
    new_header = df.iloc[header_index].astype(str).tolist()
    new_header = make_unique(new_header)

    cleaned_df = df.iloc[header_index + 1:].copy()
    cleaned_df.columns = new_header
    cleaned_df = cleaned_df.reset_index(drop=True)

    # Build minimal summary
    preview = metadata_df.head(10).to_dict(orient="records")

    summary = {
        "task_name": "remove_metadata_rows",
        "metadata_preview": preview
    }

    return cleaned_df, summary
