import pandas as pd
import io

# ------------------------------------------------------------
# FILE PARSING HELPERS
# ------------------------------------------------------------

def split_metadata_and_data(lines):
    """
    Given a list of lines from a Castaway CSV file, split them into:
    - metadata_rows: the top block (usually 2 columns)
    - data_start: the index where the data table begins

    The data table is detected by finding the first row that contains
    a column named "Temperature".
    """
    metadata_rows = []
    data_start = None

    for i, line in enumerate(lines):
        parts = line.split(",")

        # Metadata rows usually have fewer than 3 columns
        if len(parts) < 3:
            metadata_rows.append(parts)
        else:
            # The first row containing "Temperature" marks the start of the data table
            if any("Temperature" in col for col in parts):
                data_start = i
                break

    return metadata_rows, data_start


def parse_castaway_file(file_obj):
    """
    Parse a single Castaway CSV file into:
    - metadata_df: a small DataFrame with columns ["Variable", "Value"]
    - data_df: the main data table

    This function does not clean names or normalize anything.
    It only extracts the two sections cleanly.
    """
    content = file_obj.getvalue().decode("utf-8")
    lines = content.splitlines()

    metadata_rows, data_start = split_metadata_and_data(lines)

    # Build metadata DataFrame
    metadata_df = pd.DataFrame(metadata_rows, columns=["Variable", "Value"])

    # Build data DataFrame
    data_df = pd.read_csv(io.StringIO("\n".join(lines[data_start:])))

    return metadata_df, data_df


def extract_metadata_and_data(files):
    """
    Parse multiple Castaway files at once.

    Returns:
        metadata_list: list of metadata DataFrames
        data_list:     list of data DataFrames
    """
    metadata_list = []
    data_list = []

    for file_obj in files:
        meta, data = parse_castaway_file(file_obj)
        metadata_list.append(meta)
        data_list.append(data)

    return metadata_list, data_list
