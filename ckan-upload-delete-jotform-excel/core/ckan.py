# core/ckan.py
import requests

def upload_metadata(dataset_dict, api_key, base_url):
    """
    Upload a dataset to CKAN using the package_create endpoint.
    
    Parameters:
        dataset_dict (dict): CKAN dataset metadata payload.
        api_key (str): CKAN API key for authorization.
        base_url (str): CKAN base URL (e.g., https://data.example.com).
    
    Returns:
        dict: JSON response from CKAN.
    """
    headers = {"Authorization": api_key,"Content-Type": "application/json"}
    endpoint = f"{base_url}/api/3/action/package_create"
    response = requests.post(endpoint, json=dataset_dict, headers=headers)
    try:
        return response.json()
    except Exception:
        return {"success": False, "error": "Invalid JSON response", "status_code": response.status_code}


def delete_dataset(dataset_id, api_key, base_url):
    """
    Delete a dataset from CKAN using the package_delete endpoint.
    
    Parameters:
        dataset_id (str): The CKAN dataset ID or name.
        api_key (str): CKAN API key for authorization.
        base_url (str): CKAN base URL.
    
    Returns:
        dict: JSON response from CKAN.
    """
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    endpoint = f"{base_url}/api/3/action/package_delete"
    response = requests.post(endpoint, headers=headers, json={"id": dataset_id})
    try:
        return response.json()
    except Exception:
        return {"success": False, "error": "Invalid JSON response", "status_code": response.status_code}


def update_dataset(dataset_dict, api_key, base_url):
    """
    Update an existing dataset in CKAN using the package_update endpoint.
    
    Parameters:
        dataset_dict (dict): CKAN dataset metadata payload (must include 'id' or 'name').
        api_key (str): CKAN API key for authorization.
        base_url (str): CKAN base URL.
    
    Returns:
        dict: JSON response from CKAN.
    """
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    endpoint = f"{base_url}/api/3/action/package_update"
    response = requests.post(endpoint, json=dataset_dict, headers=headers)
    try:
        return response.json()
    except Exception:
        return {"success": False, "error": "Invalid JSON response", "status_code": response.status_code}