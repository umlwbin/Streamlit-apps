# ckan_utils.py
import requests
import json
import pandas as pd


BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"
CKAN_URL = "https://canwin-datahub.ad.umanitoba.ca/data"

# Filter Federated Datasets-----------------------------------------------------------------------------------------------------
def filter_non_federated(datasets):
    """Remove federated datasets (those with 'extras')."""
    return [d for d in datasets if not d.get("extras", {})]


# Geting all datasets, projects and publications-----------------------------------------------------------------------------------------------------
def load_native_packages():
    """Fetch all public, native CKAN packages (datasets, projects, publications)."""
    
    canwin_data = []
    page_size = 250
    start_row = 0

    fq_expression = (
        "type:(dataset OR project OR publication) "
        "AND -extras_federated_index_profile:*"
    )

    while True:
        payload = {
            "q": "*:*",
            "fq": fq_expression,
            "start": start_row,
            "rows": page_size,
        }

        response = requests.post(f"{BASE_URL}/package_search", json=payload)
        response.raise_for_status()

        all_data = response.json()
        result = all_data.get("result", {})
        results = result.get("results", [])

        if not results:
            break

        #Remove private data
        public_data = [pkg for pkg in results if not pkg.get('private', False)]

        canwin_data.extend(public_data)

        start_row += page_size
        if start_row >= result.get("count", 0):
            break

    return canwin_data

# Geting all resources-----------------------------------------------------------------------------------------------------
def get_package_resources(canwin_data):

    datasets = canwin_data
    full_packages = []

    for pkg in datasets:
        name = pkg["name"]
        url = f"{BASE_URL}/package_show?id={name}"
        response = requests.get(url)
        response.raise_for_status()
        resource_metadata = response.json()["result"]
        full_packages.append(resource_metadata)

    return full_packages

# Classify resources -----------------------------------------------------------------------------------------------------
def classify_resources(full_packages):
    """Classify resources by type and return counts + lists."""
    docs, measured, web, multimedia, unknown = [], [], [], [], []
    counts = {"docs": 0, "measured": 0, "web": 0, "multimedia": 0, "unknown": 0}

    for dataset in full_packages:
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

    return counts, {
        "docs": docs,
        "measured": measured,
        "web": web,
        "multimedia": multimedia,
        "unknown": unknown
    }



# Search dataset -----------------------------------------------------------------------------------------------------
def search_datasets(query, rows=10):
    """Search CKAN datasets by keyword, excluding federated ones."""
    # url = f"{BASE_URL}/package_search?q={query}&rows={rows}"
    # response = requests.get(url)
    # response.raise_for_status()
    # results = response.json()["result"]["results"]
    # return filter_non_federated(results)

    url = f"{BASE_URL}/package_search"
    payload={
        "q":query,
        "rows":rows
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    results = response.json()["result"]["results"]
    return filter_non_federated(results)


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


# Delete dataset -----------------------------------------------------------------------------------------------------
def delete_dataset(dataset_id, api_key):
    """Delete a dataset by ID or name. Requires API key."""
    
    # Fetch dataset and check if federated first
    url = f"{BASE_URL}/package_show?id={dataset_id}"
    response = requests.get(url)
    response.raise_for_status()
    dataset = response.json()["result"]
    if dataset.get("extras", {}):
        raise ValueError("This dataset is federated and cannot be deleted.")
    
    #Delete dataset
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
    Extract any metadata field from all non-federated datasets.
    Returns a list of tuples (value, dataset_url).
    """

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
        if field not in metadata:
            continue

        value = metadata[field]

        # Case 1: simple value
        if isinstance(value, (str, int, float)):
            results.append((value, page_url))

        # Case 2: list of strings
        elif isinstance(value, list) and all(isinstance(v, str) for v in value):
            results.append((json.dumps(value, indent=2), page_url))

        # Case 3: list of dicts
        elif isinstance(value, list) and all(isinstance(v, dict) for v in value):
            results.append((json.dumps(value, indent=2), page_url))

        # Case 4: dict
        elif isinstance(value, dict):
            results.append((json.dumps(value, indent=2), page_url))

        # Fallback: convert anything else to JSON
        else:
            results.append((json.dumps(value, indent=2), page_url))

    return results


# Analyze Keywords --------------------------------------------------------------------------
from collections import Counter
def analyze_tags(limit=1000, total=35464):
    """
    Fetch all non-federated datasets and analyze tag usage.
    Returns a Counter of tag frequencies and a list of (dataset, tags).
    """
    datasets = load_native_packages()

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

