import pandas as pd

# Public CSV export link to your Google Sheet
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFYGhlbknWKOOAezrkK4_-gJNGk--1PAiGaBKvTOkjdF2MIvT0d0AS04rEyWElgcYgfvTR0jbKIoRd/pub?output=csv"

def load_keywords(url: str = URL) -> pd.DataFrame:
    """
    Load and clean the keywords DataFrame from a Google Sheet.

    Steps:
    - Read the sheet with no header (header=None).
    - Use the 2nd row (index 1) as the header row.
    - Drop the first column (hidden pull from another sheet).
    - Reset index for cleanliness.
    - Remove placeholder letters (e.g. 'A', 'B', 'C') that appear
      as the first element in each column.

    Returns:
        A cleaned pandas DataFrame with columns A–Z containing keywords.
    """
    raw_df = pd.read_csv(url, header=None)

    # Use 2nd row as header, drop first row
    df = raw_df[1:]
    df.columns = raw_df.iloc[1]
    df = df.drop(df.columns[0], axis=1).reset_index(drop=True)

    # Remove placeholder letters (first element equal to column name)
    for col in df.columns:
        if df[col].iloc[0] == col:
            df[col] = df[col].iloc[1:]

    return df


def group_columns(df, chunk_size=3):
    """
    Group columns into larger blocks (e.g. A–C, D–F, etc.).

    Args:
        df: Cleaned DataFrame of keywords.
        chunk_size: Number of consecutive columns to group together.

    Returns:
        Dictionary where keys are group labels (e.g. "A – C")
        and values are dictionaries mapping each letter column
        to its list of keywords.
    """
    cols = list(df.columns)
    groups = {}
    for i in range(0, len(cols), chunk_size):
        block_cols = cols[i:i+chunk_size]
        label = f"{block_cols[0]} – {block_cols[-1]}"

        # Store keywords grouped by column
        col_dict = {}
        for c in block_cols:
            kws = df[c].dropna().tolist()
            # Remove placeholder letter if present
            if kws and kws[0] == c:
                kws = kws[1:]
            col_dict[c] = kws

        groups[label] = col_dict
    return groups


def build_dropdown_options(df: pd.DataFrame) -> list:
    """
    Build a flat list of options for a dropdown menu.

    Format:
    - Each column (letter) starts with a heading like "--- A ---".
    - Followed by all keywords under that column.

    Args:
        df: Cleaned DataFrame of keywords.

    Returns:
        List of strings suitable for use in a Streamlit selectbox.
        Headings can be detected with startswith('---').
    """
    options = []
    for col in df.columns:
        options.append(f"--- {col} ---")  # heading marker
        options.extend(df[col].dropna().tolist())
    return options
    