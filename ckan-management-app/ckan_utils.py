# ckan_utils.py
import requests
import json
import pandas as pd
import streamlit as st
import datetime
from ckanapi import RemoteCKAN

BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"
CKAN_URL = "https://canwin-datahub.ad.umanitoba.ca/data"

# Filter Federated Datasets-----------------------------------------------------------------------------------------------------
def filter_non_federated(datasets):
    """Remove federated datasets (those with 'extras')."""
    return [d for d in datasets if not d.get("extras", {})]

# Checking Resources-----------------------------------------------------------------------------------------------------
def get_all_packages(limit=1000, total=35464):
    """Fetch all CKAN packages (datasets, projects, publications).
    Currently we have 35464 datasets TOTAL. Change this as needed. 1000 is the max amount the api will print at a time, so we use an offset of 1000, to grab every 1000
    API endpoint
    """
    canwin_data = []
    for offset in range(0, total, limit):
        url = f"{BASE_URL}/current_package_list_with_resources?limit={limit}&offset={offset}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["result"]

        # Filter out federated datasets (those with 'extras')
        canwin_data.extend(filter_non_federated(data))
    return canwin_data

# Filter Datasets-----------------------------------------------------------------------------------------------------
def filter_datasets(canwin_data):
    """Return only datasets, projects, and publications."""
    return [cd for cd in canwin_data if cd.get("type") in ["dataset", "project", "publication"]]

# Classify resources -----------------------------------------------------------------------------------------------------
def classify_resources(canwin_datasets):
    """Classify resources by type and return counts + lists."""
    docs, measured, web, multimedia, unknown = [], [], [], [], []
    counts = {"docs": 0, "measured": 0, "web": 0, "multimedia": 0, "unknown": 0}

    for dataset in canwin_datasets:
        for res in dataset.get("resources", []):
            r_title = res.get("name")
            r_type = res.get("format", "").upper()
            r_url = res.get("url")

            if r_type in ["PDF", "DOCX"]:
                docs.append((r_title, r_type, r_url))
                counts["docs"] += 1
            elif r_type in ["CSV", "ZIP", "XLSX", "XLS", "TXT", "NC", "NETCDF", "RMD", "R"]:
                measured.append((r_title, r_type, r_url))
                counts["measured"] += 1
            elif r_type in ["HTML", "GEOJSON", "URL", "XML"]:
                web.append((r_title, r_type, r_url))
                counts["web"] += 1
            elif r_type in ["PNG", "JPG", "JPEG", "MP4"]:
                multimedia.append((r_title, r_type, r_url))
                counts["multimedia"] += 1
            else:
                unknown.append((r_title, r_type, r_url))
                counts["unknown"] += 1

    return counts, {"docs": docs, "measured": measured, "web": web, "multimedia": multimedia, "unknown": unknown}

# Get dataset -----------------------------------------------------------------------------------------------------
def get_dataset(dataset_id, api_key=None):
    """
    Fetch a CKAN dataset (package_show).
    API key optional unless dataset is private.
    """
    url = f"{BASE_URL}/package_show"
    headers = {"Authorization": api_key} if api_key else {}
    payload = {"id": dataset_id}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["result"]

# Search dataset -----------------------------------------------------------------------------------------------------
def search_datasets(query, rows=10):
    """Search CKAN datasets by keyword, excluding federated ones."""
    url = f"{BASE_URL}/package_search?q={query}&rows={rows}"
    response = requests.get(url)
    response.raise_for_status()
    results = response.json()["result"]["results"]
    return filter_non_federated(results)

# Delete dataset -----------------------------------------------------------------------------------------------------
def delete_dataset(dataset_id, api_key):
    """Delete a dataset by ID or name. Requires API key."""
    # Optional: fetch dataset first to check if federated
    check_url = f"{BASE_URL}/package_show?id={dataset_id}"
    check_resp = requests.get(check_url)
    check_resp.raise_for_status()
    dataset = check_resp.json()["result"]

    if dataset.get("extras", {}):
        raise ValueError("This dataset is federated and cannot be deleted.")

    url = f"{BASE_URL}/dataset_purge"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    payload = {"id": dataset_id}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# User Management--------------------------------------------------------------------------
def list_users(api_key, limit=50, offset=0):
    """List CKAN users. Requires sysadmin API key."""
    url = f"{BASE_URL}/user_list"
    headers = {"Authorization": api_key}
    params = {"limit": limit, "offset": offset}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["result"]

# Extract Metadata--------------------------------------------------------------------------
def extract_metadata(field="creatorName", dataset_type="dataset"):
    """
    Extract specific metadata field (e.g., creatorName) from all non-federated datasets.
    Returns a list of tuples (value, dataset_url).
    """
    # Get list of all dataset IDs
    package_url = f"{BASE_URL}/package_list"
    response = requests.get(package_url)
    response.raise_for_status()
    dataset_ids = response.json()["result"]

    results = []
    for d in dataset_ids:
        metadata_url = f"{BASE_URL}/package_show?id={d}"
        page_url = f"https://canwin-datahub.ad.umanitoba.ca/data/dataset/{d}"

        resp = requests.get(metadata_url)
        resp.raise_for_status()
        metadata = resp.json()["result"]

        # Skip federated datasets
        if metadata.get("extras", {}):
            continue

        # Only include certain dataset types
        if metadata.get("type") != dataset_type:
            continue

        # Extract field if present
        if field in metadata:
            field_value = metadata[field]
            # Handle case where field is a list of dicts (like creatorName)
            if isinstance(field_value, list):
                for entry in field_value:
                    author = entry.get("author")
                    if author:
                        results.append((author, page_url))
            else:
                results.append((field_value, page_url))

    return results

# Analyze Keywords --------------------------------------------------------------------------
from collections import Counter
def analyze_tags(limit=1000, total=35464):
    """
    Fetch all non-federated datasets and analyze tag usage.
    Returns a Counter of tag frequencies and a list of (dataset, tags).
    """
    all_data = get_all_packages(limit=limit, total=total)
    datasets = filter_datasets(all_data)

    tag_counter = Counter()
    dataset_tags = []

    for d in datasets:
        tags = d.get("tags", [])
        tag_names = [t.get("name") for t in tags if "name" in t]
        if tag_names:
            tag_counter.update(tag_names)
            dataset_tags.append((d.get("title", ""), tag_names))

    return tag_counter, dataset_tags


# Get Group Metadata --------------------------------------------------------------------------
def list_groups():
    """
    List all available CKAN groups.
    """
    url = f"{BASE_URL}/group_list"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["result"]

def get_group_metadata(group_name):
    """
    Retrieve metadata for a CKAN group by name.
    Returns a dictionary of group details.
    """
    url = f"{BASE_URL}/group_show?id={group_name}"
    response = requests.get(url)
    response.raise_for_status()
    result = response.json()["result"]

    # Flatten into a DataFrame-friendly dict
    metadata = {
        "id": result.get("id"),
        "name": result.get("name"),
        "title": result.get("title"),
        "description": result.get("description"),
        "created": result.get("created"),
        "package_count": result.get("package_count"),
        "image_display_url": result.get("image_display_url"),
    }
    return metadata
# ----------------------------------------------------------------------------------------------------------------


# Delete all resources --------------------------------------------------------------------------
def delete_all_resources(dataset_id, api_key):
    """
    Delete all resources from a CKAN dataset.
    """
    base_url = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"

    # 1. Fetch dataset details
    dataset_url = f"{base_url}/package_show"
    headers = {"Authorization": api_key}
    payload = {"id": dataset_id}

    response = requests.post(dataset_url, json=payload, headers=headers)
    response.raise_for_status()
    dataset = response.json()["result"]

    deleted = []

    # 2. Loop through resources
    for resource in dataset.get("resources", []):
        resource_id = resource["id"]
        delete_url = f"{base_url}/resource_delete"
        delete_payload = {"id": resource_id}

        del_response = requests.post(delete_url, json=delete_payload, headers=headers)
        del_response.raise_for_status()

        deleted.append(resource_id)

    return deleted


# Search by Date -------------------------------------------------------------------------------------------------

# 1. Load all native public records ONCE (cached for 1 hour)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def load_all_native_records():
    """
    Fetch all public, non-federated datasets/projects/publications from CKAN.
    This is the ONLY function that talks to CKAN.
    Everything else reuses this cached list.
    """
    ckan = RemoteCKAN(CKAN_URL)

    all_items = []
    page_size = 250
    start_row = 0
    fq_expression = "type:(dataset OR publication OR project)"

    # Stable pagination (prevents skipped datasets)
    while True:
        response = ckan.action.package_search(
            q="*:*",
            fq=fq_expression,
            sort="metadata_created asc",
            start=start_row,
            rows=page_size
        )

        results = response.get("results", [])
        if not results:
            break

        all_items.extend(results)

        # Stop when all results have been retrieved
        if len(all_items) >= response.get("count", 0):
            break

        start_row += len(results)

    # Remove federated datasets
    items = filter_non_federated(all_items)

    # Keep only public datasets
    native_public = [pkg for pkg in items if not pkg.get("private", False)]

    return native_public

# 2. Extract all organizations from native public records
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def get_native_orgs():
    """
    Return a sorted list of (org_id, org_title) for all native public records.
    Used to populate the organization multiselect in the UI.
    """
    items = load_all_native_records()

    orgs = {}
    for pkg in items:
        org = pkg.get("organization")
        if not org:
            continue

        oid = org.get("id")
        title = org.get("title") or org.get("name") or "(No org)"

        orgs[oid] = title

    # Return list of (id, title), sorted alphabetically by title
    return sorted([(oid, title) for oid, title in orgs.items()],
                  key=lambda x: x[1].lower())

# 3. Filter by date, org, and type using metadata_created ONLY
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def search_datasets_by_date(start_date, end_date, allowed_orgs, allowed_types):
    """
    Filter the cached native records by:
      - organization IDs
      - record types (dataset/project/publication)
      - metadata_created date range
    """
    start_dt = datetime.datetime.combine(start_date, datetime.time.min)
    end_dt = datetime.datetime.combine(end_date, datetime.time.max)

    items = load_all_native_records()
    filtered = []

    for pkg in items:

        # Type filter
        if pkg.get("type") not in allowed_types:
            continue

        # Organization filter
        org = pkg.get("organization", {})
        if not org or org.get("id") not in allowed_orgs:
            continue

        # Use metadata_created ONLY (ignore "Date" field)
        ts = pkg.get("metadata_created")
        if not ts:
            continue

        try:
            ts_str = ts.strip().replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(ts_str).replace(tzinfo=None)
        except Exception:
            continue

        pkg["display_date_clean"] = dt.strftime("%Y-%m-%d")
        pkg["extracted_year"] = dt.year
        pkg["in_range"] = (start_dt <= dt <= end_dt)

        filtered.append(pkg)

    return filtered

# ----------------------------------------------------------------------------------------------------------------
