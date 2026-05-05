# ckan_utils.py
import requests
import json
import pandas as pd
import streamlit as st

BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"


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


def filter_datasets(canwin_data):
    """Return only datasets, projects, and publications."""
    return [cd for cd in canwin_data if cd.get("type") in ["dataset", "project", "publication"]]


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

#--------------------------------------------------------------------------------------------------------------------

def search_datasets(query, rows=10):
    """Search CKAN datasets by keyword, excluding federated ones."""
    url = f"{BASE_URL}/package_search?q={query}&rows={rows}"
    response = requests.get(url)
    response.raise_for_status()
    results = response.json()["result"]["results"]
    return filter_non_federated(results)

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


from datetime import datetime
def filter_by_date(datasets, start_date=None, end_date=None):
    """
    Filter datasets by creation date.
    Dates should be strings in 'YYYY-MM-DD' format.
    """
    filtered = []
    for d in datasets:
        created = d.get("metadata_created")
        if not created:
            continue
        created_dt = datetime.fromisoformat(created.replace("Z", ""))  # CKAN returns ISO timestamps

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            if created_dt < start_dt:
                continue
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            if created_dt > end_dt:
                continue

        filtered.append(d)
    return filtered

# User Management--------------------------------------------------------------------------
def list_users(api_key, limit=50, offset=0):
    """List CKAN users. Requires sysadmin API key."""
    url = f"{BASE_URL}/user_list"
    headers = {"Authorization": api_key}
    params = {"limit": limit, "offset": offset}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["result"]



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


import requests
from datetime import datetime
from dateutil.parser import parse

BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"





#In the CKAN API world, package_search is essentially a wrapper for a search engine (Solr). 
# Solr is designed to handle GET requests for queries, and because your parameters (the date range and the three types) are relatively short, 
# they fit easily within the URL character limit (which is usually around 2,000+ characters).
# Why stick with GET?
# Standard Practice: It’s the "native" way to use package_search. Most CKAN documentation and community examples use GET.

@st.cache_data(ttl=3600)  # Caches for 1 hour
def search_datasets_by_date(start_date, end_date, rows=100):
    """
    Fetch ALL datasets, projects, and publications from CKAN,
    then filter by metadata_created in Python.

    IMPORTANT POINTS
    - CKAN instances that use ckanext‑scheming (like CanWIN) silently force type:dataset into every package_search query unless you override it in the q parameter.
    - q  --->  main query (strongest)
    - fq --->  filter query (weaker)

    You must put typr into q, not fq
    """

    api_url = f"{BASE_URL}/package_search"

    # Solr requires the full timestamp: YYYY-MM-DDTHH:MM:SSZ
    #Input is "2025-04-01", so need to pad it:
    solr_start = f"{start_date}T00:00:00Z" if "T" not in start_date else start_date
    solr_end = f"{end_date}T23:59:59Z" if "T" not in end_date else end_date

    params = {
        "q": "(type:dataset OR type:publication OR type:project)",
        "fq": f"metadata_created:[{solr_start} TO {solr_end}]",
        "rows": rows
    }

    response = requests.get(api_url, params=params)
    
    if response.status_code != 200:
        # This will now show the detailed Solr error if it happens again
        st.error(f"Error {response.status_code}: {response.text}")
        response.raise_for_status()

    result=response.json()["result"]["results"]
    results = filter_non_federated(result)

    return results


    # from ckanapi import RemoteCKAN

    # # Initialize connection
    # ckan = RemoteCKAN('https://canwin-datahub.ad.umanitoba.ca/data')

    # # Define your time range (ISO 8601 format)
    # # Use 'NOW' for the current time
    # start_date = "2025-04-01T00:00:00Z"
    # end_date = "2026-03-31T00:00:00Z"

    # # We use the 'q' parameter to force CKAN to look for all three types
    # # Note: 'dataset' is the standard type name for datasets in CKAN
    # types_query = "(type:dataset OR type:publication OR type:project)"

    # results_dict = ckan.action.package_search(
    #     q=types_query,
    #     fq=f"metadata_created:[{start_date} TO {end_date}]",
    #     rows=200
    # )

    # results = results_dict["results"]
    # results = filter_non_federated(results)

    # for d in results:
    #     st.write(f"[{d['type'].upper()}]--- {d['title']} ---- Created: {d['metadata_created']}")
