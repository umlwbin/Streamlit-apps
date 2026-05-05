# app.py

#import posit password
import os
import datetime

APP_PASSWORD = os.getenv("APP_PASSWORD")

import streamlit as st
import pandas as pd
from ckan_utils import get_all_packages, filter_datasets, classify_resources, search_datasets, delete_dataset, filter_by_date, list_users, extract_metadata,analyze_tags, delete_all_resources, search_datasets_by_date
from erddap_metadata_profile import extract_erddap_attributes
from data_dictionary import build_resource_table
from group_metadata import get_group_metadata, list_groups
from data_dictionary_uploader import read_excel_dictionary, map_excel_to_ckan, upload_data_dictionary, get_ckan_schema, clean_excel_dictionary, find_mismatches


st.set_page_config(layout="wide")
st.title("CKAN Management App")
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13 = st.tabs(
    ["Resource Checker", "Dataset Search", "Dataset Delete", "Date Filter", "User Management", "Metadata Extractor", 
     "Keyword Analysis", "ERDDAP Metadata Attributes", "CSV variables", "Theme Metadata", "Data Dictionary Uploader", 
     "Remove All Resources from Dataset", "Dataset Search by Date"])

# --- Password Gate ---
st.sidebar.header("Authentication")
password = st.sidebar.text_input("Enter app password", type="password")

if password != APP_PASSWORD:
    st.warning("Please enter the correct password in the sidebar to access the app.")
    st.stop()  # Prevents the rest of the app from running


# --- Resource Checker ---
with tab1:
    st.header("Resource Checker")
    if st.button("Run CKAN Resource Check"):
        with st.spinner("Fetching data from CKAN..."):
            all_data = get_all_packages()
            datasets = filter_datasets(all_data)
            counts, classified = classify_resources(datasets)

        st.success("Data fetched and classified!")

        st.subheader("Resource Counts by Type")
        st.write(pd.DataFrame(counts.items(), columns=["Resource Type", "Count"]))

        for category, resources in classified.items():
            with st.expander(f"{category.capitalize()} ({len(resources)})"):
                df = pd.DataFrame(resources, columns=["Title", "Format", "URL"])
                st.dataframe(df)
                st.download_button(
                    label=f"Download {category} as CSV",
                    data=df.to_csv(index=False),
                    file_name=f"{category}.csv",
                    mime="text/csv"
                )

# --- Dataset Search ---
with tab2:
    st.header("Dataset Search")
    st.markdown("Uses CKAN's **package_search** endpoint. Searches across multiple fields.")
    query = st.text_input("Enter search keyword")
    rows = st.slider("Number of results", 1, 50, 10)

    if st.button("Search"):
        with st.spinner("Searching datasets..."):
            results = search_datasets(query, rows=rows)

        st.success(f"Found {len(results)} datasets")

        # Normalize results into DataFrame
        df = pd.json_normalize(results)

        # Ensure expected columns exist
        for col in ["id", "title", "notes"]:
            if col not in df.columns:
                df[col] = ""

        st.dataframe(df[["id", "title", "notes"]])
        st.download_button(
            label="Download search results",
            data=df.to_csv(index=False),
            file_name="search_results.csv",
            mime="text/csv"
        )

# --- Dataset Delete ---
with tab3:
    st.header("Dataset Delete")
    st.warning("⚠️ Deleting datasets is permanent. Use with caution.")
    dataset_id = st.text_input("Enter dataset ID or name")
    api_key = st.text_input("Enter your CKAN API key", type="password", key="delete_api_key")

    if st.button("Delete Dataset"):
        if dataset_id and api_key:
            try:
                result = delete_dataset(dataset_id, api_key)
                st.success(f"Dataset {dataset_id} deleted successfully!")
                st.json(result)
            except Exception as e:
                st.error(f"Error deleting dataset: {e}")
        else:
            st.error("Please provide both dataset ID and API key.")


# --- Filter datasets by Date ---
with tab4:
    '''
    Uses CKAN’s metadata_created field (ISO timestamp).
    '''
    st.header("Filter Datasets by Date")
    start_date = st.date_input("Start date", value=None)
    end_date = st.date_input("End date", value=None)

    if st.button("Filter by Date"):
        with st.spinner("Fetching datasets..."):
            all_data = get_all_packages()
            datasets = filter_datasets(all_data)
            filtered = filter_by_date(
                datasets,
                start_date.strftime("%Y-%m-%d") if start_date else None,
                end_date.strftime("%Y-%m-%d") if end_date else None,
            )

        st.success(f"Found {len(filtered)} datasets in the selected period")

        df = pd.DataFrame(filtered)
        # Ensure safe columns
        for col in ["id", "title", "metadata_created"]:
            if col not in df.columns:
                df[col] = ""
        st.dataframe(df[["id", "title", "metadata_created"]])
        st.download_button(
            label="Download filtered datasets",
            data=df.to_csv(index=False),
            file_name="filtered_datasets.csv",
            mime="text/csv"
        )

with tab5:
    st.header("User Management")
    api_key = st.text_input("Enter your CKAN sysadmin API key", type="password", key="user_api_key")

    if st.button("List Users"):
        if api_key:
            try:
                users = list_users(api_key)
                df = pd.DataFrame(users)
                st.dataframe(df[["display_name", "name","created", "number_created_packages","id"]])
                st.download_button(
                    label="Download user list",
                    data=df.to_csv(index=False),
                    file_name="users.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error fetching users: {e}")
        else:
            st.error("Please provide an API key.")


with tab6:
    st.header("Metadata Extractor")
    st.markdown("Extract specific metadata fields (e.g., creatorName) from all datasets.")

    field = st.text_input("Enter metadata field name", value="creatorName")
    dataset_type = st.selectbox("Dataset type", ["dataset", "project", "publication"])

    if st.button("Extract Metadata"):
        with st.spinner("Fetching metadata..."):
            results = extract_metadata(field=field, dataset_type=dataset_type)

        st.success(f"Found {len(results)} entries for field '{field}'")

        df = pd.DataFrame(results, columns=[field, "Dataset URL"])
        st.dataframe(df)

        st.download_button(
            label="Download metadata as CSV",
            data=df.to_csv(index=False),
            file_name=f"{field}_metadata.csv",
            mime="text/csv"
        )


with tab7:
    st.header("Tag / Keyword Analysis")
    st.markdown("Analyze tag usage across all non-federated datasets.")

    if st.button("Run Tag Analysis"):
        with st.spinner("Fetching and analyzing tags..."):
            tag_counter, dataset_tags = analyze_tags()

        st.success("Tag analysis complete!")

        # Show top tags
        st.subheader("Top Tags")
        top_tags = pd.DataFrame(tag_counter.most_common(20), columns=["Tag", "Count"])
        st.dataframe(top_tags)

        st.download_button(
            label="Download full tag frequency CSV",
            data=pd.DataFrame(tag_counter.items(), columns=["Tag", "Count"]).to_csv(index=False),
            file_name="tag_frequency.csv",
            mime="text/csv"
        )

        # Show dataset-tag mapping
        st.subheader("Dataset → Tags")
        dataset_tag_df = pd.DataFrame(dataset_tags, columns=["Dataset Title", "Tags"])
        st.dataframe(dataset_tag_df)

        st.download_button(
            label="Download dataset-tag mapping CSV",
            data=dataset_tag_df.to_csv(index=False),
            file_name="dataset_tags.csv",
            mime="text/csv"
        )


with tab8:
    st.header("ERDDAP Metadata Extractor")
    st.markdown("Extract CKAN metadata and merge with ERDDAP-required attributes.")

    dataset_url = st.text_input("Dataset URL")
    resource_url = st.text_input("Resource URL")
    api_key = st.text_input("CKAN API Key", type="password", key="erddap_api_key")

    if st.button("Generate ERDDAP Attributes"):
        with st.spinner("Extracting metadata..."):
            try:

                attributes = extract_erddap_attributes(dataset_url, resource_url, api_key)
                st.success("Attributes generated successfully!")

                # Show attributes
                xml_output = extract_erddap_attributes(dataset_url, resource_url, api_key)
                st.code(xml_output, language="xml")
                st.download_button(
                    label="Download ERDDAP XML",
                    data=xml_output,
                    file_name="erddap_attributes.xml",
                    mime="application/xml"
                )
            except Exception as e:
                st.error(f"Error: {e}")



with tab9:
    import csv
    st.header("Variable Checker")
    st.markdown("Extract CSV headers, labels and description from data dictionary ")

    if st.button("Grab headers!"):
        with st.spinner("Fetching CSV resources and data dictionaries..."):
            df = build_resource_table()

        st.success("All done")
        st.dataframe(df)

        st.download_button(
            label="Download resource table",
            data=df.to_csv(index=False, quoting=csv.QUOTE_MINIMAL),
            file_name="variable_standardization.csv",
            mime="text/csv"
        )


with tab10:
    st.header("Theme Metadata")
    st.markdown("Retrieve details of CKAN groups (themes/collections).")

    groups = list_groups()
    selected_group = st.selectbox("Select a group", groups)

    if st.button("Get Group Metadata"):
        with st.spinner("Fetching group details..."):
            metadata = get_group_metadata(selected_group)
            df = pd.DataFrame([metadata])

        st.success("Group metadata retrieved!")
        st.dataframe(df)

        st.download_button(
            label="Download group metadata as CSV",
            data=df.to_csv(index=False),
            file_name=f"{selected_group}_metadata.csv",
            mime="text/csv"
        )


with tab11:
    st.header("Upload Data Dictionary to CKAN")
    st.markdown("Upload an Excel data dictionary and push selected fields into CKAN's datastore metadata.")

    excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    resource_id = st.text_input("CKAN Resource ID (CSV resource)", key="dd_resource_id")
    api_key = st.text_input("CKAN API Key", type="password", key="dd_upload_api_key")

    if excel_file:
        df = read_excel_dictionary(excel_file)
        df = clean_excel_dictionary(df)
        st.subheader("Preview Excel Data")
        st.dataframe(df)


        if st.button("Check for mismatches"):
            try:
                ckan_columns = get_ckan_schema(resource_id, api_key)
                missing_in_ckan, missing_in_excel = find_mismatches(df, ckan_columns)

                st.subheader("Columns in Excel but NOT in CKAN")
                st.write(missing_in_ckan)

                st.subheader("Columns in CKAN but NOT in Excel")
                st.write(missing_in_excel)

            except Exception as e:
                st.error(f"Error checking mismatches: {e}")

        # Initialize session state
        if "mapped" not in st.session_state:
            st.session_state["mapped"] = None

        if st.button("Map Columns"):
            st.session_state["mapped"] = map_excel_to_ckan(df)
            st.subheader("Mapped CKAN Fields")
            st.json(st.session_state["mapped"])

        if st.button("Upload to CKAN"):
            if st.session_state["mapped"] is None:
                st.error("Please map the columns first.")
            else:
                try:
                    result = upload_data_dictionary(resource_id, st.session_state["mapped"], api_key)
                    st.success("Data dictionary uploaded successfully!")
                    st.json(result)
                except Exception as e:
                    st.error(f"Error uploading data dictionary: {e}")


with tab12:
    st.header("Remove All Resources from Dataset")
    st.warning("⚠️ This will permanently delete ALL resources from the dataset.")

    dataset_id = st.text_input("Dataset ID or name")
    api_key = st.text_input("CKAN API Key", type="password", key="delete_resources_api_key")

    if st.button("Delete All Resources"):
        if dataset_id and api_key:
            try:
                deleted = delete_all_resources(dataset_id, api_key)
                st.success(f"Deleted {len(deleted)} resources.")
                st.write(deleted)
            except Exception as e:
                st.error(f"Error deleting resources: {e}")
        else:
            st.error("Please provide both dataset ID and API key.")


# --- Dataset Search by Creation Date ---
with tab13:

    st.header("Search by Date Created")
    st.markdown("Great for end of year! 😎")

    # --- Default date values ---
    default_start = datetime.date(2025, 4, 1)
    default_end = datetime.date(2026, 3, 31)

    # --- UI Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=default_start, key="t13_start")
    with col2:
        end_date = st.date_input("End date", value=default_end, key="t13_end")

    # --- Validate Inputs ---
    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()

    # --- Search Button ---
    if st.button("Search", key="t13_search"):

        with st.spinner("Searching CKAN…"):

            # Convert UI dates → Solr padded strings
            solr_start = f"{start_date}T00:00:00Z"
            solr_end = f"{end_date}T23:59:59Z"

            results = search_datasets_by_date(
                solr_start,
                solr_end
            )

        # --- No Results ---
        if not results:
            st.warning("No datasets, projects, or publications found in this date range.")
            st.stop()

        # --- Results Header ---
        st.success(f"Found {len(results)} result(s)")

        # --- Build table ---
        table_rows = []
        for d in results:
            name = d.get("name")
            url = f"https://canwin-datahub.ad.umanitoba.ca/data/dataset/{name}"

            table_rows.append({
                "Title": d.get("title") or "(No title)",
                "Type": d.get("type", "unknown"),
                "Created": d.get("metadata_created", "unknown"),
                "URL": url
            })

        st.dataframe(table_rows, use_container_width=True)

