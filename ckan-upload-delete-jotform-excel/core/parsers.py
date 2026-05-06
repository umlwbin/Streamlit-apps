"""
parsers.py- Excel long‑text metadata parsing

This module parses long‑text metadata blocks exported from Jotform Excel files.
All block‑based fields (Authors, Contributors, Sampling, Analysis, Funding,
Related Resources) follow the same pattern:

1. Identify the correct column using find_column().
2. Convert the cell to a string.
3. Split the string into blocks using extract_metadata_blocks() and the
   appropriate anchor defined below.
4. For each block, extract individual fields using extract_metadata_value().
5. Clean the resulting dict using clean_dict_values().

"""

from core.helpers import (
    find_column,
    extract_metadata_blocks,
    extract_metadata_value,
    clean_dict_values,
    slugify
)

# ---------------------------------------------------------
# ANCHORS- Update these if Jotform labels change
# ---------------------------------------------------------
# These strings mark the beginning of each repeated metadata block
# inside the long‑text Excel export (They come from the configurable table widget in jotform).

AUTHOR_ANCHOR = "Name:"                     # e.g., "Name: Dadjoo, Mehran, Type of Name:"
CONTRIBUTOR_ANCHOR = "Name:"                # e.g., "Name: , Role: , Email:"
SAMPLING_ANCHOR = "Sample Instrument Name:" # e.g., "Sample Instrument Name: , Sample Collection Method Name:"
ANALYSIS_ANCHOR = "Analytical Instrument Name:"  # e.g., "Analytical Instrument Name: ProSensing, Identifier ID:"
FUNDING_ANCHOR = "Award Title:"             # e.g., "Award Title: , Website:"
RELATED_RESOURCES_ANCHOR = "Related Resource Name:"  # e.g., "Related Resource Name: A Study on..."

# ---------------------------------------------------------
# PARSERS
# (parse_authors, parse_contributors, parse_sampling, etc.)
# ---------------------------------------------------------

# ---------------------------------------------------------
# AUTHORS
# ---------------------------------------------------------
def parse_authors(df, index, normalized_cols):
    """Parse long‑text author blocks into structured dicts."""
    col = find_column(normalized_cols, "author")
    raw = str(df[col][index])
    blocks = extract_metadata_blocks(raw, anchor=AUTHOR_ANCHOR)

    authors = []
    for block in blocks:
        authors.append(clean_dict_values({
            "author": extract_metadata_value(block, "Name: ", ", Type of Name:"),
            "nameType": extract_metadata_value(block, "Type of Name: ", ", Email:"),
            "creatorEmail": extract_metadata_value(block, "Email: ", ", Affiliation:"),
            "creatorAffiliation": extract_metadata_value(block, "Affiliation: ", ", ORCID ID:"),
            "creatorNameIdentifier": extract_metadata_value(block, "ORCID ID: ")
        }))
    return authors


# ---------------------------------------------------------
# CONTRIBUTORS
# ---------------------------------------------------------
def parse_contributors(df, index, normalized_cols):
    """Parse long‑text contributor blocks into structured dicts."""
    col = find_column(normalized_cols, "contributor")
    raw = str(df[col][index])
    blocks = extract_metadata_blocks(raw, anchor=CONTRIBUTOR_ANCHOR)

    contributors = []
    for block in blocks:
        role = extract_metadata_value(block, "Role: ", ", Email:").replace(" ", "")
        contributors.append(clean_dict_values({
            "contributorName": extract_metadata_value(block, "Name: ", ", Role:"),
            "contributorType": role,
            "email": extract_metadata_value(block, "Email: ", ", Affiliation:"),
            "affiliation": extract_metadata_value(block, "Affiliation: ", ", ORCID ID:"),
            "nameIdentifier": extract_metadata_value(block, "ORCID ID: ")
        }))
    return contributors


# ---------------------------------------------------------
# DATA CURATOR
# ---------------------------------------------------------
def parse_data_curator(df, index, normalized_cols):
    """Parse long‑text data curator block into (name, email, affiliation)."""
    col = find_column(normalized_cols, "data curator")
    raw = str(df[col][index])

    name = extract_metadata_value(raw, "Project Data Curator: ", ", Data Curator Email:")
    email = extract_metadata_value(raw, "Data Curator Email: ", ", Data Curator Affiliation:")
    affiliation = raw.partition("Data Curator Affiliation: ")[-1]

    return name, email, affiliation


# ---------------------------------------------------------
# DATASET NAME
# ---------------------------------------------------------
def parse_dataset_name(df, row, normalized_cols):
    """Extract dataset title and slugified CKAN name."""
    col = find_column(normalized_cols, "dataset name")
    title = row[col]
    return title, slugify(title)


# ---------------------------------------------------------
# SAMPLING
# ---------------------------------------------------------
def parse_sampling(df, index, normalized_cols):
    """Parse long‑text sampling blocks into structured dicts."""
    col = find_column(normalized_cols, "sampling information")
    raw = str(df[col][index])
    blocks = extract_metadata_blocks(raw, anchor=SAMPLING_ANCHOR)

    sampling = []
    activity_type = ""

    for block in blocks:
        sampling.append(clean_dict_values({
            "instrumentTitle": extract_metadata_value(block, "Sample Instrument Name: ", ", Sample Collection Method Name:"),
            "methodTitle": extract_metadata_value(block, "Sample Collection Method Name: ", ", Method Link:"),
            "methodUrl": extract_metadata_value(block, "Method Link: ", ", Method Summary:"),
            "methodDescrioption": extract_metadata_value(block, "Method Summary: ", ", Activity Collection Type:"),
            "comment": extract_metadata_value(block, "Comments: ")
        }))
        activity_type = extract_metadata_value(block, "Activity Collection Type: ", ", Comments")

    return sampling, activity_type


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------
def parse_analysis(df, index, normalized_cols):
    """Parse long‑text analysis blocks into method + instrument dicts."""
    col = find_column(normalized_cols, "analysis information")
    raw = str(df[col][index])
    blocks = extract_metadata_blocks(raw, anchor=ANALYSIS_ANCHOR)

    methods = []
    instruments = []

    for block in blocks:
        methods.append(clean_dict_values({
            "analyticalMethodName": extract_metadata_value(block, "Analytical Method: ", ", Method Link:"),
            "methodLink": extract_metadata_value(block, "Method Link: ", ", Method Summary:"),
            "methodSummary": extract_metadata_value(block, "Method Summary: ", ", Laboratory:"),
            "laboratory": extract_metadata_value(block, "Laboratory: ", ", Variables measured:"),
            "variablesMeasured": extract_metadata_value(block, "Variables measured: ", ", Comments:"),
            "comments": extract_metadata_value(block, "Comments: ")
        }))

        instruments.append(clean_dict_values({
            "name": extract_metadata_value(block, "Analytical Instrument Name: ", ", Identifier ID:"),
            "analyticalInstrumentIdentifier": extract_metadata_value(block, "Identifier ID: ", ", Identifier Type:"),
            "identifierType": extract_metadata_value(block, "Identifier Type: ", ", Analytical Method:"),
            "Title": " ",
            "titleType": "Alternative Title"
        }))

    return methods, instruments


# ---------------------------------------------------------
# FUNDING
# ---------------------------------------------------------
def parse_funding(df, index, normalized_cols):
    """Parse long‑text funding blocks into structured dicts."""
    col = find_column(normalized_cols, "funding")
    raw = str(df[col][index])
    blocks = extract_metadata_blocks(raw, anchor=FUNDING_ANCHOR)

    funding = []
    for block in blocks:
        funding.append(clean_dict_values({
            "awardTitle": extract_metadata_value(block, "Award Title: ", ", Website:"),
            "awardURI": extract_metadata_value(block, "Website: ", ", Funder Name:"),
            "funderName": extract_metadata_value(block, "Funder Name: ", ", Funder Identifier Code:"),
            "funderIdentifier": extract_metadata_value(block, "Funder Identifier Code: ", ", Funder Identifier Type:"),
            "funderIdentifierType": extract_metadata_value(block, "Funder Identifier Type: ", ", Grant number:"),
            "grantNumber": extract_metadata_value(block, "Grant number: ")
        }))
    return funding


# ---------------------------------------------------------
# RELATED RESOURCES
# ---------------------------------------------------------
def parse_related_resources(df, index, normalized_cols):
    """Parse long‑text related resource blocks into structured dicts."""
    col = find_column(normalized_cols, "related resources")
    raw = str(df[col][index])
    blocks = extract_metadata_blocks(raw, anchor=RELATED_RESOURCES_ANCHOR)

    resources = []
    for block in blocks:
        resources.append(clean_dict_values({
            "name": extract_metadata_value(block, "Related Resource Name: ", ", Resource Code:"),
            "RelatedIdentifier": extract_metadata_value(block, "Resource Code: ", ", Identifier Type:"),
            "relatedIdentifierType": extract_metadata_value(block, "Identifier Type: ", ", Relationship to Dataset:"),
            "relationship": extract_metadata_value(block, "Relationship to Dataset: ", ", Type:"),
            "resourceType": "Online Resource",  # CKAN requires this
            "seriesName": extract_metadata_value(block, "Series Name: ")
        }))
    return resources


# ---------------------------------------------------------
# KEYWORDS
# ---------------------------------------------------------
def parse_keywords(df, index, normalized_cols):
    """Parse comma‑separated keywords into CKAN tag dicts."""
    col = [c for c in normalized_cols if "keywords" in c.lower()][0]
    raw = str(df[col][index])
    return [{"display_name": k.strip(), "name": k.strip()} for k in raw.split(",") if k.strip()]
