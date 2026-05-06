# core/dataset_builder.py

"""
dataset_builder.py - Convert parsed Excel metadata into CKAN dataset dictionaries.

This module assembles all parsed metadata (authors, contributors, sampling,
analysis, funding, related resources, keywords, dates, spatial info, etc.)
into a CKAN‑compatible dataset dictionary.

Curators typically only need to adjust:
- Theme --> CKAN group mapping (THEME_TO_GROUP)
- Field names used in safe_get() if Jotform labels change

Everything else is handled automatically.
"""

from core.helpers import normalize_date, safe_get, normalize_spatial_region
from core.parsers import (
    parse_authors,
    parse_contributors,
    parse_sampling,
    parse_dataset_name,
    parse_funding,
    parse_related_resources,
    parse_analysis,
    parse_keywords,
    parse_data_curator
)
from core.mappings import THEME_TO_GROUP


# ---------------------------------------------------------
# THEME --> CKAN GROUP MAPPING
# ---------------------------------------------------------
def add_theme_group(dataset_dict, row):
    """Assign CKAN group + theme based on the Theme field."""
    raw_value = row.get("Theme", "")
    if not isinstance(raw_value, str):
        raw_value = ""

    theme_value = raw_value.strip()

    if theme_value in THEME_TO_GROUP:
        group_obj = THEME_TO_GROUP[theme_value]
        dataset_dict["groups"] = [group_obj]
        dataset_dict["theme"] = group_obj["id"]
    else:
        dataset_dict["groups"] = []
        dataset_dict["theme"] = None

    return dataset_dict


# ---------------------------------------------------------
# DATASET BUILDER
# ---------------------------------------------------------
def create_dataset_dict(df, normalized_cols, resource_type=None):
    """Build CKAN dataset dictionaries from dataframe rows."""
    dataset_dicts = []

    for index, row in df.iterrows():

        # -------------------------------------------------
        # PARSED METADATA (from parsers.py)
        # -------------------------------------------------
        keywords = parse_keywords(df, index, normalized_cols)
        authors = parse_authors(df, index, normalized_cols)
        contributors = parse_contributors(df, index, normalized_cols)
        sampling, activity_type = parse_sampling(df, index, normalized_cols)
        funding = parse_funding(df, index, normalized_cols)
        related = parse_related_resources(df, index, normalized_cols)
        analysis_methods, analysis_instruments = parse_analysis(df, index, normalized_cols)
        dc_name, dc_email, dc_aff = parse_data_curator(df, index, normalized_cols)
        title, name = parse_dataset_name(df, row, normalized_cols)

        # -------------------------------------------------
        # RESOURCE TYPE
        # -------------------------------------------------
        if resource_type:
            chosen_resource_type = resource_type
        else:
            chosen_resource_type = safe_get(row, "Dataset Type", default="Dataset")

        # -------------------------------------------------
        # BUILD CKAN DICTIONARY
        # -------------------------------------------------
        dataset_dict = {

            # ---------------------------------------------
            # HARD‑CODED CKAN METADATA
            # ---------------------------------------------
            "descriptionType": "Abstract",
            "RelatedIdentifierType": "URL",
            "RelationType": "IsSupplementTo",
            "dateType": "Updated",
            "IdentifierType": "DOI",
            "Publisher": "CanWIN",
            "datasetPublisher": "CanWIN",
            "contributorType": "DataCurator",
            "rightsURI": "https://spdx.org/licenses/CC-BY-4.0.html",
            "rightsIdentifier": "CC-BY-4.0",

            # ---------------------------------------------
            # CORE DATASET FIELDS
            # ---------------------------------------------
            "name": name,
            "title": title,
            "type": "dataset",
            "datasetLevel": "1.1",
            "kvSchemeURI": "https://www.polardata.ca/pdcinput/public/keywordlibrary",
            "subjectScheme": "Polar Data Catalogue",
            "projectImage": safe_get(row, "Dataset Image"),
            "datasetCitation": safe_get(row, "Preferred citation"),
            "embargoDate": safe_get(row, "Embargo Date"),
            "private": True,
            "notes": safe_get(row, "Dataset Summary"),
            "resourceTypeGeneral": "Dataset",
            "ResourceType": chosen_resource_type,
            "tags": keywords,
            "status": safe_get(row, "Dataset Status"),
            "Version": safe_get(row, "Version"),
            "frequency": safe_get(row, "Maintenance and Update Frequency"),

            # ---------------------------------------------
            # DATES
            # ---------------------------------------------
            "Date": normalize_date(safe_get(row, "Dataset Last Revision Date")),
            "metadata_created": normalize_date(safe_get(row, "Metadata Creation Date")),
            "startDate": normalize_date(safe_get(row, "Dataset Collection Start Date")),
            "endDate": normalize_date(safe_get(row, "Dataset Collection End Date")),
            "datasetIdentifier": safe_get(row, "Dataset DOI"),

            # ---------------------------------------------
            # SPATIAL
            # ---------------------------------------------
            "spatial_regions": normalize_spatial_region(safe_get(row, "Spatial Regions")),

            # ---------------------------------------------
            # PEOPLE
            # ---------------------------------------------
            "creatorName": authors,
            "contributors": contributors,
            "contributorName": dc_name,
            "dataCuratorEmail": dc_email,
            "dataCuratorAffiliation": dc_aff,

            # ---------------------------------------------
            # SAMPLING / ANALYSIS
            # ---------------------------------------------
            "sample_collection": sampling,
            "analyticalMethod": analysis_methods,
            "activityCollectionType": activity_type,
            "analyticalInstrument": analysis_instruments,

            # ---------------------------------------------
            # FUNDING / RELATED RESOURCES
            # ---------------------------------------------
            "awards": funding,
            "supplementalResources": related,

            # ---------------------------------------------
            # TERMS & LICENSING
            # ---------------------------------------------
            "startDateType": "Collected",
            "endDateType": "Other",
            "licenceType": "Open",
            "Rights": "Creative Commons Attribution 4.0 International",
            "rightsIdentifierScheme": "SPDX",
            "accessTerms": (
                "CanWIN datasets are licensed individually, however most are licensed under the "
                "Creative Commons Attribution 4.0 International (CC BY 4.0) Public License. "
                "Details for the licence applied can be found using the Licence URL link provided "
                "with each dataset. By using data and information provided on this site you accept "
                "the terms and conditions of the License."
            ),
            "useTerms": (
                "By accessing this data you agree to CanWIN's Terms of Use "
                "(/data/publication/canwin-data-statement/resource/5b942a87-ef4e-466e-8319-f588844e89c0)."
            ),

            # ---------------------------------------------
            # FACILITY
            # ---------------------------------------------
            "owner_org": "9e21f6b6-d13f-4ba2-a379-fd962f507071",
        }

        # Add theme + CKAN group
        dataset_dict = add_theme_group(dataset_dict, row)

        dataset_dicts.append(dataset_dict)

    return dataset_dicts
