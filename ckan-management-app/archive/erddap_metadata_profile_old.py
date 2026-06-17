import pandas as pd
from ckanapi import RemoteCKAN

# ERDDAP Metadata Profile------------------------------------------------------------------
def extract_erddap_attributes(dataset_url, resource_url, api_key):
    """
    Extract metadata from a CKAN dataset and merge with ERDDAP-required attributes.
    Returns a list of <att name="...">...</att> strings.
    """
    # Connect to CKAN
    demo = RemoteCKAN('https://canwin-datahub.ad.umanitoba.ca/data',
                      apikey=api_key, user_agent='ckanapi', get_only=True)

    dataset_id = dataset_url.partition("dataset/")[2]
    package = demo.action.package_show(id=dataset_id)
    df = pd.DataFrame([package])   # one-row DataFrame

    all_fields = []

    # Always include infoUrl and sourceUrl
    all_fields.append(f'<att name="infoUrl">{dataset_url}</att>')
    all_fields.append(f'<att name="sourceUrl">{resource_url}</att>')

    # Example: add institution, title, summary, license
    if "title" in df.columns:
        all_fields.append(f'<att name="title">{df["title"].iloc[0]}</att>')
    if "notes" in df.columns:
        all_fields.append(f'<att name="summary">{df["notes"].iloc[0]}</att>')
    if "Rights" in df.columns:
        all_fields.append(f'<att name="license">{df["Rights"].iloc[0]}</att>')
    if "startDate" in df.columns:
        all_fields.append(f'<att name="data_collection_start_date">{df['startDate'].iloc[0]}</att>')
    if "endDate" in df.columns:
        all_fields.append(f'<att name="data_collection_end_date">{df['endDate'].iloc[0]}</att>')
    if "Research_Area" in df.columns:
        all_fields.append(f'<att name="research_area">{df['Research_Area'].iloc[0]}</att>')
    if "Dataset_Status" in df.columns:
        all_fields.append(f'<att name="dataset_status">{df['Dataset_Status'].iloc[0]}</att>')

    if "creatorName" in df.columns:
        authors = df["creatorName"].iloc[0]
        if isinstance(authors, list) and len(authors) > 0:
            if len(authors) == 1:
                a = authors[0]
                all_fields.append(f'<att name="author_name">{a.get("author","")}</att>')
                all_fields.append(f'<att name="author_email">{a.get("creatorEmail","")}</att>')
                all_fields.append(f'<att name="author_affiliation">{a.get("creatorAffiliation","")}</att>')
            else:
                for i, a in enumerate(authors, start=1):
                    all_fields.append(f'<att name="author_name_{i}">{a.get("author","")}</att>')
                    all_fields.append(f'<att name="author_email_{i}">{a.get("creatorEmail","")}</att>')
                    all_fields.append(f'<att name="author_affiliation_{i}">{a.get("creatorAffiliation","")}</att>')

    if "contributors" in df.columns:
        contributors = df["contributors"].iloc[0]
        if isinstance(contributors, list) and len(contributors) > 0:
            if len(contributors) == 1:
                c = contributors[0]
                all_fields.append(f'<att name="contributor_name">{c.get("contributorName","")}</att>')
                all_fields.append(f'<att name="contributor_role">{c.get("contributorType","")}</att>')
                all_fields.append(f'<att name="contributor_email">{c.get("email","")}</att>')
                all_fields.append(f'<att name="contributor_affiliation">{c.get("affiliation","")}</att>')
            else:
                for i, c in enumerate(contributors, start=1):
                    all_fields.append(f'<att name="contributor_name_{i}">{c.get("contributorName","")}</att>')
                    all_fields.append(f'<att name="contributor_role_{i}">{c.get("contributorType","")}</att>')
                    all_fields.append(f'<att name="contributor_email_{i}">{c.get("email","")}</att>')
                    all_fields.append(f'<att name="contributor_affiliation_{i}">{c.get("affiliation","")}</att>')

    # Keywords
    if "tags" in df.columns:
        tags = [t["display_name"] for t in df["tags"].iloc[0]]
        all_fields.append(f'<att name="keywords">{", ".join(tags)}</att>')

    # Merge with ERDDAP-required defaults
    erddap_defaults = {
        "cdm_data_type": "Other",
        "creator_url": "null",
        "history": "null",
        "subsetVariables": "fileType",
        "standard_name_vocabulary": "CF Standard Name Table v55"
    }

    for k, v in erddap_defaults.items():
        if not any(f'<att name="{k}"' in f for f in all_fields):
            all_fields.append(f'<att name="{k}">{v}</att>')

    return all_fields