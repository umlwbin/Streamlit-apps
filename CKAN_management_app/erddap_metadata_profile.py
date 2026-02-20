import pandas as pd
from ckanapi import RemoteCKAN

def extract_erddap_attributes(dataset_url, resource_url, api_key):
    """
    Extract metadata from a CKAN dataset and merge with ERDDAP-required attributes.
    Returns a string containing <addAttributes>...</addAttributes> block in fixed order.
    """
    # Connect to CKAN
    demo = RemoteCKAN(
        'https://canwin-datahub.ad.umanitoba.ca/data',
        apikey=api_key,
        user_agent='ckanapi',
        get_only=True
    )

    dataset_id = dataset_url.partition("dataset/")[2]
    package = demo.action.package_show(id=dataset_id)
    df = pd.DataFrame([package])   # one-row DataFrame

    # --- Extract values safely ---
    title = df["title"].iloc[0] if "title" in df.columns else ""
    summary = df["notes"].iloc[0] if "notes" in df.columns else ""
    license = df["Rights"].iloc[0] if "Rights" in df.columns else ""
    start_date = df["startDate"].iloc[0] if "startDate" in df.columns else ""
    end_date = df["endDate"].iloc[0] if "endDate" in df.columns else ""
    keywords = ", ".join([t["display_name"] for t in df["tags"].iloc[0]]) if "tags" in df.columns else ""

    # Author / creator info
    creator_name = "null"
    creator_email = "null"
    institution = ""
    if "creatorName" in df.columns:
        authors = df["creatorName"].iloc[0]
        if isinstance(authors, list) and len(authors) > 0:
            a = authors[0]  # only first author for ERDDAP
            creator_name = a.get("author", "null")
            creator_email = a.get("creatorEmail", "null")
            institution = a.get("creatorAffiliation", "")

    # --- Ordered attributes ---
    ordered_attrs = [
        ("cdm_data_type", "Other"),
        ("creator_email", creator_email),
        ("creator_name", creator_name),
        ("infoUrl", dataset_url),
        ("sourceUrl", resource_url),
        ("title", title),
        ("summary", summary),
        ("license", license),
        ("data_collection_start_date", start_date),
        ("data_collection_end_date", end_date),
        ("author_name", creator_name),
        ("author_email", creator_email),
        ("institution", institution),
        ("keywords", keywords),
        ("creator_url", "null"),
        ("history", "null"),
        ("subsetVariables", "fileType"),
        ("standard_name_vocabulary", "CF Standard Name Table v55"),
    ]

    # --- Build XML block ---
    lines = ["<addAttributes>"]
    for name, value in ordered_attrs:
        lines.append(f'    <att name="{name}">{value}</att>')
    lines.append("</addAttributes>")

    return "\n".join(lines)