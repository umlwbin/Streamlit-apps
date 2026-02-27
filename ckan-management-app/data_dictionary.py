import requests
import pandas as pd
from ckan_utils import get_all_packages, filter_datasets, filter_non_federated
import streamlit as st

BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"

def get_csv_resources(limit=1000, total=35464):
    """Fetch all non-federated CSV resources and their headers."""
    all_data = get_all_packages(limit=limit, total=total)
    datasets = filter_datasets(all_data)
    datasets = filter_non_federated(datasets)

    csv_resources = []
    for d in datasets:
        for res in d.get("resources", []):
            if res.get("format", "").lower() == "csv":
                headers = get_data_dictionary(res)
                if headers:
                    csv_resources.append({
                        "dataset_title": d.get("title"),
                        "dataset_id": d.get("id"),
                        "resource_id": res.get("id"),
                        "resource_name": res.get("name"),
                        "resource_url": res.get("url"),
                        "headers": headers   # store headers here
                    })
    return csv_resources

def get_data_dictionary(resource):
    """Fetch the data dictionary (table designer) for a resource if datastore_active=True."""
    if not resource.get("datastore_active", False):
        return []  # No datastore table, skip
    
    resource_id = resource["id"]
    url = f"{BASE_URL}/datastore_search?resource_id={resource_id}&limit=1"
    response = requests.get(url)
    response.raise_for_status()
    result = response.json()["result"]
    fields = result.get("fields", [])
    
    headers = []
    for f in fields:
        headers.append({
            "id": f.get("id"),
            "label": f.get("info", {}).get("label", ""),
            "description": f.get("info", {}).get("notes", "")
        })
    return headers


def build_resource_table():
    """Build a table of header terms, labels, descriptions, and dataset link."""
    resources = get_csv_resources()
    rows = []
    for res in resources:
        headers = res["headers"]  # we stored headers earlier
        dataset_link = f"https://canwin-datahub.ad.umanitoba.ca/data/dataset/{res['dataset_id']}"
        for h in headers:
            rows.append({
                "header_term": h["id"],
                "label": h["label"],
                "description": h["description"],
                "dataset": res["dataset_title"],
                "dataset_link": dataset_link
            })
    return pd.DataFrame(rows)