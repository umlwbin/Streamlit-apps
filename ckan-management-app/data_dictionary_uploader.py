import pandas as pd
import requests
import math

# Base URL for the CKAN API on the CanWIN DataHub
BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"


# ---------------------------------------------------------------------------
# 1. READ EXCEL FILE
# ---------------------------------------------------------------------------
def read_excel_dictionary(file):
    """
    Read an uploaded Excel file into a pandas DataFrame.
    Streamlit passes the uploaded file object directly to pandas.
    """
    return pd.read_excel(file)


# ---------------------------------------------------------------------------
# 2. CLEAN EXCEL FILE (BEGINNER-FRIENDLY + SAFE)
# ---------------------------------------------------------------------------
def clean_excel_dictionary(df):
    """
    Clean the Excel data dictionary by removing rows that should NOT be uploaded.

    - Remove fully empty rows
    - Remove rows where all cells are blank/whitespace
    - Remove the explanation row used in CanWIN templates (that row contains several known phrases listed below)
    - Clean column names

    IMPORTANT:
    We do NOT try to guess which column is the ID column.
    The user selects that later in the UI.
    """

    # 1. Remove fully empty rows
    df = df.dropna(how="all")

    # 2. Remove rows where every cell is blank or whitespace
    df = df[~df.apply(lambda row: row.astype(str).str.strip().eq("").all(), axis=1)]

    # 3. Remove the single explanation row (it contains ANY of these partial phrases)
    explanation_headers = [
        "the exact column name as it appeared",
        "a common or understandable name",
        "the physical units",
        "a description explaining"
    ]

    # Safe lowercase helper (avoids .lower() errors on floats/NaN)
    def safe_lower(v):
        return v.lower() if isinstance(v, str) else ""

    # Remove the explanation row if ANY cell contains ANY of the known phrases
    df = df[~df.apply(
        lambda row: any(
            any(h in safe_lower(cell) for h in explanation_headers)
            for cell in row
        ),
        axis=1
    )]

    # 4. Strip whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]

    return df


# ---------------------------------------------------------------------------
# 3. CLEAN INDIVIDUAL CELL VALUES
# ---------------------------------------------------------------------------
def clean_value(v):
    """
    Convert Excel cell values into safe strings for CKAN.

    - CKAN expects strings for metadata fields.
    - Excel often stores empty cells as NaN (float).
    - This function ensures we never upload NaN or None.
    """
    if v is None:
        return ""
    if isinstance(v, float) and math.isnan(v):
        return ""
    return str(v).strip()


# ---------------------------------------------------------------------------
# 4. MAP EXCEL ROWS → CKAN METADATA FORMAT
# ---------------------------------------------------------------------------
def map_excel_to_ckan(df, mapping):
    """
    Convert Excel rows into CKAN metadata using the user-selected mapping.

    The UI provides a mapping like:
        {
            "id": "Original Header",
            "info.label": "Label",
            "info.notes": "Description",
            ...
        }

    This function:
    - Reads each row of the Excel file
    - Extracts the ID column (required)
    - Builds CKAN metadata fields (info.label, info.notes, etc.)
    """

    # 1. Validate that the user selected an ID column
    id_col = mapping.get("id")

    if not id_col or id_col == "-- None --":
        raise ValueError("You must select a column to use as the CKAN 'id' field.")

    if id_col not in df.columns:
        raise ValueError(f"The selected ID column '{id_col}' does not exist in the Excel file.")

    ckan_fields = []

    # 2. Build metadata for each row
    for _, row in df.iterrows():

        raw_id = clean_value(row[id_col])

        # Skip blank or invalid IDs
        if raw_id == "" or raw_id.lower() == "nan":
            continue

        field = {"id": raw_id}

        # 3. Map all other CKAN metadata fields
        for ckan_key, excel_col in mapping.items():

            if ckan_key == "id":
                continue  # already handled

            if excel_col in (None, "-- None --"):
                continue  # user chose not to map this field

            if excel_col not in df.columns:
                continue  # skip invalid mappings

            raw_value = row.get(excel_col, "")
            value = clean_value(raw_value)

            # CKAN uses nested structure: info.label, info.notes, etc.
            parent, child = ckan_key.split(".")
            field.setdefault(parent, {})
            field[parent][child] = value

        ckan_fields.append(field)

    return ckan_fields


# ---------------------------------------------------------------------------
# 5. UPLOAD METADATA TO CKAN (NO SCHEMA CHANGES)
# ---------------------------------------------------------------------------
def upload_data_dictionary(resource_id, mapped_fields, api_key):
    """
    Upload metadata to CKAN WITHOUT modifying the datastore schema.

    This function:
    - Fetches CKAN's existing schema
    - Ensures the Excel file contains ALL required CKAN fields
    - Ignores extra Excel rows safely
    - Uploads metadata using datastore_create (metadata-only mode)
    """

    # 1. Fetch CKAN schema
    schema_url = f"{BASE_URL}/datastore_search"
    headers = {"Authorization": api_key}
    payload = {"resource_id": resource_id, "limit": 0}

    schema_response = requests.post(schema_url, json=payload, headers=headers)
    schema_response.raise_for_status()

    # CKAN returns a list of fields; we only care about their IDs
    ckan_fields = [f["id"] for f in schema_response.json()["result"]["fields"]]
    ckan_fields = [c for c in ckan_fields if c != "_id"]  # remove CKAN internal field

    # 2. Extract IDs from Excel
    excel_ids = [f["id"] for f in mapped_fields]

    # 3. Check if Excel is missing any required CKAN fields
    missing_fields = [c for c in ckan_fields if c not in excel_ids]

    if missing_fields:
        return {
            "status": "error",
            "missing_fields": missing_fields,
            "ignored_fields": [],
            "updated_fields": []
        }

    # 4. Keep only fields CKAN already knows
    updated_fields = [f for f in mapped_fields if f["id"] in ckan_fields]

    # 5. Identify extra Excel rows (ignored safely)
    ignored_fields = [f["id"] for f in mapped_fields if f["id"] not in ckan_fields]

    # 6. Upload metadata only (no schema changes)
    url = f"{BASE_URL}/datastore_create"
    payload = {
        "resource_id": resource_id,
        "force": True,      # allow metadata updates
        "fields": updated_fields,
        "records": []       # MUST be empty to avoid schema changes
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
