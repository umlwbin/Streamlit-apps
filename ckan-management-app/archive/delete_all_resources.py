# data_dictionary_uploader.py
#
# This script helps upload metadata (a “data dictionary”) from an Excel file
# into an existing CKAN datastore resource.
#
# The goal: students can take a curated Excel sheet, clean it, map it to CKAN’s
# expected JSON structure, and upload it WITHOUT changing the actual datastore
# schema (the columns already stored in CKAN).
#
# Each function below handles one clear step in that workflow.

import pandas as pd
import requests
import math

# Base URL for the CKAN API on the CanWIN DataHub.
BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"


# ---------------------------------------------------------------------------
# 1. READ THE EXCEL FILE
# ---------------------------------------------------------------------------
def read_excel_dictionary(file):
    """
    Read an uploaded Excel file into a pandas DataFrame.

    Parameters
    ----------
    file : str or file-like object
        Path to the Excel file or an uploaded file object.

    Returns
    -------
    DataFrame
        The raw Excel data as a pandas DataFrame.
    """
    return pd.read_excel(file)


# ---------------------------------------------------------------------------
# 2. CLEAN THE EXCEL DATA DICTIONARY
# ---------------------------------------------------------------------------
def clean_excel_dictionary(df):
    """
    Clean the Excel data dictionary by removing rows that should NOT be uploaded.

    Why this matters:
    - Excel sheets often contain description rows, blank rows, or header-like rows.
    - CKAN requires each row to represent ONE variable with a valid ID.
    - This function removes anything that would break the upload.

    Steps performed:
    1. Normalize the "Cleaned Variable Name" column (strip spaces, convert to string)
    2. Remove long description rows (these are not variable IDs)
    3. Remove rows where the ID contains spaces (real CKAN IDs never contain spaces)
    4. Remove blank or "nan" IDs
    5. Remove header-like rows that appear in the Excel sheet
    """

    # Normalize the column so comparisons work reliably
    df["Cleaned Variable Name"] = (
        df["Cleaned Variable Name"]
        .astype(str)
        .str.strip()
    )

    # 1. Remove description rows (these tend to be long text blocks)
    df = df[df["Cleaned Variable Name"].str.len() < 80]

    # 2. Remove rows with spaces — CKAN column IDs never contain spaces
    df = df[~df["Cleaned Variable Name"].str.contains(" ")]

    # 3. Remove blank or "nan" values
    df = df[
        (df["Cleaned Variable Name"] != "") &
        (df["Cleaned Variable Name"] != "nan")
    ]

    # 4. Remove header-like rows that sometimes appear in Excel exports
    invalid_ids = [
        "Cleaned Variable Name",
        "Original Header",
        "Type",
        "Notes",
        "Standardized Source Term",
    ]
    df = df[~df["Cleaned Variable Name"].isin(invalid_ids)]

    return df


# ---------------------------------------------------------------------------
# 3. CLEAN INDIVIDUAL VALUES FOR SAFE JSON
# ---------------------------------------------------------------------------
def clean_value(v):
    """
    Convert values into safe JSON strings.

    Why this matters:
    - CKAN expects strings for metadata fields.
    - Excel often stores empty cells as NaN (Not a Number).
    - This function ensures we never upload NaN or None.

    Returns
    -------
    str
        A clean string value (empty string if missing).
    """
    if v is None:
        return ""
    if isinstance(v, float) and math.isnan(v):
        return ""
    return str(v)


# ---------------------------------------------------------------------------
# 4. FETCH CKAN DATASTORE SCHEMA
# ---------------------------------------------------------------------------
def get_ckan_schema(resource_id, api_key):
    """
    Fetch the list of column names currently stored in a CKAN datastore resource.

    Why this matters:
    - We must ensure the Excel file matches the existing CKAN schema.
    - CKAN will NOT create new columns unless explicitly told to.
    - This function helps detect mismatches before uploading.

    Returns
    -------
    list of str
        The list of CKAN column IDs.
    """
    url = f"{BASE_URL}/datastore_search"
    headers = {"Authorization": api_key}
    payload = {"resource_id": resource_id, "limit": 0}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    fields = response.json()["result"]["fields"]
    return [f["id"] for f in fields]


# ---------------------------------------------------------------------------
# 5. FIND MISMATCHES BETWEEN EXCEL AND CKAN
# ---------------------------------------------------------------------------
def find_mismatches(df, ckan_columns):
    """
    Compare Excel variable IDs with CKAN column IDs.

    Returns
    -------
    missing_in_ckan : list
        Variables present in Excel but NOT in CKAN.
    missing_in_excel : list
        Variables present in CKAN but NOT in Excel (excluding CKAN's internal _id).
    """
    excel_columns = df["Cleaned Variable Name"].tolist()

    missing_in_ckan = [c for c in excel_columns if c not in ckan_columns]
    missing_in_excel = [c for c in ckan_columns if c not in excel_columns and c != "_id"]

    return missing_in_ckan, missing_in_excel


# ---------------------------------------------------------------------------
# 6. MAP EXCEL ROWS TO CKAN METADATA FORMAT
# ---------------------------------------------------------------------------
def map_excel_to_ckan(df):
    """
    Convert each Excel row into the JSON structure CKAN expects for metadata.

    Important:
    - This does NOT change the datastore schema.
    - It only updates metadata fields like label, notes, units, etc.

    CKAN expects metadata in this structure:
        {
            "id": "column_name",
            "info": {
                "label": "...",
                "notes": "...",
                "unit": "...",
                ...
            }
        }

    This function builds that structure for each row.
    """

    # Normalize IDs again for safety
    df["Cleaned Variable Name"] = df["Cleaned Variable Name"].astype(str).str.strip()

    # Remove empty or invalid IDs
    df = df[df["Cleaned Variable Name"] != ""]
    df = df[df["Cleaned Variable Name"] != "nan"]

    # Remove header-like rows
    invalid_ids = [
        "Cleaned Variable Name",
        "Original Header",
        "Type",
        "Notes",
        "Standardized Source Term"
    ]
    df = df[~df["Cleaned Variable Name"].isin(invalid_ids)]

    # Mapping from Excel column → CKAN metadata field
    mapping = {
        "Cleaned Variable Name": "id",
        "CanWIN Common Name": "info.label",
        "Data Provider Description": "info.notes",
        "Units": "info.units",
        "media_type": "info.media_type",
        "result_value_type": "info.result_value_type",
        "statistic_applied": "info.statistic_applied"
    }

    ckan_fields = []

    # Build CKAN metadata for each row
    for _, row in df.iterrows():
        field = {}

        # Required CKAN field: the column ID
        field["id"] = clean_value(row["Cleaned Variable Name"])

        # Add metadata fields
        for excel_col, ckan_key in mapping.items():
            if ckan_key == "id":
                continue  # already handled above

            raw_value = row.get(excel_col, "")
            value = clean_value(raw_value)

            # CKAN uses nested structure: info.label, info.notes, etc.
            parent, child = ckan_key.split(".")
            field.setdefault(parent, {})
            field[parent][child] = value

        ckan_fields.append(field)

    return ckan_fields


# ---------------------------------------------------------------------------
# 7. UPLOAD THE METADATA TO CKAN
# ---------------------------------------------------------------------------
def upload_data_dictionary(resource_id, fields, api_key):
    """
    Upload the metadata fields to CKAN WITHOUT modifying the datastore schema.

    Why this works:
    - CKAN's `datastore_create` endpoint can update metadata if:
        - "force": True
        - "records": [] (empty list)
    - An empty "records" list tells CKAN:
        "Do NOT touch the actual data or schema — only update metadata."

    Parameters
    ----------
    resource_id : str
        The CKAN resource to update.
    fields : list of dict
        The metadata fields generated by map_excel_to_ckan().
    api_key : str
        Your CKAN API key.

    Returns
    -------
    dict
        The CKAN API response.
    """

    url = f"{BASE_URL}/datastore_create"
    headers = {"Authorization": api_key}

    payload = {
        "resource_id": resource_id,
        "force": True,      # allow metadata updates
        "fields": fields,   # metadata only
        "records": []       # MUST be empty to avoid schema changes
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
