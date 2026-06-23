import streamlit as st
import datetime
from ckanapi import RemoteCKAN

CKAN_URL = "https://canwin-datahub.ad.umanitoba.ca/data"

# Filter Federated Datasets-----------------------------------------------------------------------------------------------------
def filter_non_federated(datasets):
    """Remove federated datasets (those with 'extras')."""
    return [d for d in datasets if not d.get("extras", {})]

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
