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
    - fully empty rows
    - rows where all values are NaN
    - long description blocks
    - header-like rows that appear inside the sheet
    """

    # Drop fully empty rows
    df = df.dropna(how="all")

    # Remove rows where every cell is blank or whitespace
    df = df[~df.apply(lambda row: row.astype(str).str.strip().eq("").all(), axis=1)]

    # Explanation rows to remove
    explanation_headers = [
        "the exact column name as it appeared",
        "a common or understandable name",
        "the physical units",
        "a description explaining"
    ]

    # Safe lowercase wrapper
    def safe_lower(v):
        if isinstance(v, str):
            return v.lower()
        return ""

    # Remove explanation rows safely
    df = df[~df.apply(
        lambda row: any(
            any(h in safe_lower(cell) for h in explanation_headers)
            for cell in row
        ),
        axis=1
    )]

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
def map_excel_to_ckan(df, mapping):
    """
    Convert Excel rows into CKAN metadata using a user-defined column mapping.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned Excel data dictionary.
    mapping : dict
        User-selected mapping of CKAN fields → Excel column names.
        Example:
            {
                "id": "Original Header",
                "info.label": "Label",
                "info.notes": "Description",
                ...
            }

    Returns
    -------
    list of dict
        CKAN metadata field definitions.
    """

    ckan_fields = []

    # ------------------------------------------------------------
    # 1. Validate that the user selected an ID column
    # ------------------------------------------------------------
    id_col = mapping.get("id")

    if not id_col or id_col == "-- None --":
        raise ValueError("You must select a column to use as the CKAN 'id' field.")

    if id_col not in df.columns:
        raise ValueError(f"The selected ID column '{id_col}' does not exist in the Excel file.")

    # ------------------------------------------------------------
    # 2. Iterate through rows and build CKAN metadata
    # ------------------------------------------------------------
    for _, row in df.iterrows():

        # Extract and validate the ID value
        raw_id = str(row[id_col]).strip()

        # Skip invalid IDs
        if raw_id == "" or raw_id.lower() == "nan":
            continue

        field = {"id": raw_id}

        # --------------------------------------------------------
        # 3. Map all other CKAN metadata fields dynamically
        # --------------------------------------------------------
        for ckan_key, excel_col in mapping.items():

            if ckan_key == "id":
                continue  # already handled

            if excel_col in (None, "-- None --"):
                continue  # user chose not to map this field

            if excel_col not in df.columns:
                continue  # skip invalid mappings

            raw_value = row.get(excel_col, "")
            value = "" if pd.isna(raw_value) else str(raw_value).strip()

            # CKAN nested structure: info.label, info.notes, etc.
            parent, child = ckan_key.split(".")
            field.setdefault(parent, {})
            field[parent][child] = value

        ckan_fields.append(field)

    return ckan_fields



# ---------------------------------------------------------------------------
# 7. UPLOAD THE METADATA TO CKAN
# ---------------------------------------------------------------------------
# def upload_data_dictionary(resource_id, mapped_fields, api_key):
#     """
#     Update CKAN metadata (data dictionary) WITHOUT modifying the schema.
#     Only fields that already exist in CKAN will be updated.
#     """

#     # 1. Fetch CKAN schema
#     schema_url = f"{BASE_URL}/datastore_search"
#     headers = {"Authorization": api_key}
#     payload = {"resource_id": resource_id, "limit": 0}

#     schema_response = requests.post(schema_url, json=payload, headers=headers)
#     schema_response.raise_for_status()

#     ckan_fields = [f["id"] for f in schema_response.json()["result"]["fields"]]

#     # 2. Filter mapped fields to only those that exist in CKAN
#     filtered = []
#     for field in mapped_fields:
#         if field["id"] in ckan_fields:
#             filtered.append(field)

#     # 3. Upload metadata only (no schema changes)
#     url = f"{BASE_URL}/datastore_create"
#     payload = {
#         "resource_id": resource_id,
#         "force": True,
#         "fields": filtered,   # metadata only
#         "records": []         # MUST be empty to avoid schema changes
#     }

#     response = requests.post(url, json=payload, headers=headers)
#     response.raise_for_status()

#     return response.json()


def upload_data_dictionary(resource_id, mapped_fields, api_key):
    """
    Update CKAN metadata (data dictionary) WITHOUT modifying the schema.
    Only fields that already exist in CKAN will be updated.
    Extra Excel rows are ignored IF all CKAN fields are present.
    """

    # 1. Fetch CKAN schema
    schema_url = f"{BASE_URL}/datastore_search"
    headers = {"Authorization": api_key}
    payload = {"resource_id": resource_id, "limit": 0}

    schema_response = requests.post(schema_url, json=payload, headers=headers)
    schema_response.raise_for_status()

    ckan_fields = [f["id"] for f in schema_response.json()["result"]["fields"]]
    ckan_fields = [c for c in ckan_fields if c != "_id"]  # remove internal field

    # 2. Extract Excel IDs
    excel_ids = [f["id"] for f in mapped_fields]

    # 3. Check completeness
    missing_fields = [c for c in ckan_fields if c not in excel_ids]

    if missing_fields:
        return {
            "status": "error",
            "missing_fields": missing_fields,
            "ignored_fields": [],
            "updated_fields": []
        }

    # 4. Filter mapped fields to only those CKAN knows
    updated_fields = [f for f in mapped_fields if f["id"] in ckan_fields]
    ignored_fields = [f["id"] for f in mapped_fields if f["id"] not in ckan_fields]

    # 5. Upload metadata only
    url = f"{BASE_URL}/datastore_create"
    payload = {
        "resource_id": resource_id,
        "force": True,
        "fields": updated_fields,
        "records": []
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    return {
        "status": "success",
        "missing_fields": [],
        "ignored_fields": ignored_fields,
        "updated_fields": [f["id"] for f in updated_fields],
        "ckan_response": response.json()
    }

