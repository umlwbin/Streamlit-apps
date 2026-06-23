import requests
import pandas as pd

BASE_URL = "https://canwin-datahub.ad.umanitoba.ca/data/api/3/action"

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


def list_groups():
    """
    List all available CKAN groups.
    """
    url = f"{BASE_URL}/group_list"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["result"]