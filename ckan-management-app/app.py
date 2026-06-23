# app.py
import sys, os
import datetime
import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(__file__))

from ckan_utils import (
    get_all_packages, filter_datasets, classify_resources, search_datasets,
    delete_dataset, list_users, extract_metadata,
    analyze_tags, get_group_metadata, list_groups, delete_all_resources, search_datasets_by_date, get_native_orgs
)

from erddap_metadata_profile import extract_erddap_attributes
from data_dictionary_uploader import read_excel_dictionary, map_excel_to_ckan, upload_data_dictionary, clean_excel_dictionary


# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(layout="wide")
st.title("CKAN Management App")


# ---------------------------------------------------------
# Increase the size of widget labels
# ---------------------------------------------------------
st.html("""
<style>
    /* All widget labels */
    [data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
    }

    /* All markdown text */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdown"] p,
    .stMarkdown p {
        font-size: 18px !important;
    }
</style>
""")


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------
st.markdown(" ")
#tab9, - "CSV variables" - depended on data_dictionry.py - moved to archive
tab1, tab2, tab3, tab5, tab6, tab7, tab8,  tab10, tab11, tab12, tab13 = st.tabs(
    ["Resource Checker", "Dataset Search", "Dataset Delete", "User Management", "Metadata Extractor", 
     "Keyword Analysis", "ERDDAP Metadata Attributes", "Theme Metadata", "Data Dictionary Uploader", 
     "Remove All Resources from Dataset", "Dataset Search by Date",])


# ---------------------------------------------------------
# Password Gate
# ---------------------------------------------------------
#import posit password
APP_PASSWORD = os.getenv("APP_PASSWORD")

st.sidebar.header("Authentication")
password = st.sidebar.text_input("Enter app password", type="password")

if password != APP_PASSWORD:
    st.warning("Please enter the correct password in the sidebar to access the app.")
    st.stop()  # Prevents the rest of the app from running


# ---------------------------------------------------------
# Task Functions 
# ---------------------------------------------------------

# --- Resource Checker ---
with tab1:
    st.markdown("### Resource Checker")
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
    st.markdown("### Dataset Search")
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
    st.markdown("### Dataset Delete")
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

# --- user Management ---
with tab5:
    st.markdown("### User Management")
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

# --- Metadata extractor ---
with tab6:
    st.markdown("### Metadata Extractor")
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

# --- keywords ---
with tab7:
    st.markdown("### Tag / Keyword Analysis")
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

# --- Erddap metadata extarctor ---
with tab8:
    st.markdown("### ERDDAP Metadata Extractor")
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

# --- Theme metadata ---
with tab10:
    st.markdown("### Theme Metadata")
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

# --- Data Dict Uplaod ---
with tab11:
    st.markdown("### Upload Data Dictionary to CKAN")
    st.markdown("Upload an Excel data dictionary and push selected fields into CKAN's datastore metadata.")

    excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    resource_id = st.text_input("CKAN Resource ID (CSV resource)", key="dd_resource_id")
    api_key = st.text_input("CKAN API Key", type="password", key="dd_upload_api_key")

    # Only proceed when ALL required inputs are provided
    if excel_file and resource_id and api_key:

        df = read_excel_dictionary(excel_file)
        df = clean_excel_dictionary(df)

        st.markdown('')
        st.markdown("#### Preview Excel Data")
        st.dataframe(df)

        st.markdown('')
        st.markdown("#### Step 1: Map Excel Columns to CKAN Metadata Fields")

        excel_columns = list(df.columns)

        ckan_fields = {
            "id": "CKAN Field Name (id)",
            "info.label": "Label (info.label)",
            "info.notes": "Description (info.notes)",
            "info.units": "Units (info.units)",
            "info.media_type": "Media Type (info.media_type)",
            "info.result_value_type": "Result Value Type (info.result_value_type)",
            "info.statistic_applied": "Statistic Applied (info.statistic_applied)"
        }

        # Auto-detection rules (lowercase partial matches)
        auto_map_rules = {
            "id": ["name in file", "original header"],
            "info.label": ["common"],
            "info.notes": ["description"],
            "info.units": ["units"],
            "info.media_type": ["media"],
            "info.result_value_type": ["result value type"],
            "info.statistic_applied": ["statistic applied"]
        }

        # Initialize mapping if not present
        if "column_mapping" not in st.session_state:
            st.session_state["column_mapping"] = {}

        # Auto-select columns based on partial matches
        for ckan_key, patterns in auto_map_rules.items():
            selected = "-- None --"
            for col in excel_columns:
                col_l = col.lower()
                if any(p in col_l for p in patterns):
                    selected = col
                    break
            st.session_state["column_mapping"][ckan_key] = selected

                
        for ckan_key, label in ckan_fields.items():
            st.session_state["column_mapping"][ckan_key] = st.selectbox(
                f"Select Excel column for **{label}**",
                ["-- None --"] + excel_columns,
                index=(["-- None --"] + excel_columns).index(st.session_state["column_mapping"][ckan_key]),
                key=f"map_{ckan_key}"
            )


        st.info("""
        **Important:**  
        The CKAN `id` field must match the column names in the uploaded data file.  
        This is how CKAN knows which metadata belongs to which variable.
        """)

        # Step 2: User clicks "Map Columns"
        if st.button("Map Columns"):
            mapped = map_excel_to_ckan(df, st.session_state["column_mapping"])
            st.session_state["mapped"] = mapped

            st.subheader("Mapped CKAN Fields")
            st.json(mapped)

        # Step 3: Upload to CKAN
        if st.button("Upload to CKAN"):
            if "mapped" not in st.session_state or st.session_state["mapped"] is None:
                st.error("Please map the columns first.")
            else:
                result = upload_data_dictionary(resource_id, st.session_state["mapped"], api_key)

                # ERROR: Missing required CKAN fields
                if result["status"] == "error":
                    st.error("Your Excel file is missing required CKAN fields:")
                    st.write(result["missing_fields"])
                    st.stop()

                # SUCCESS
                st.success("Data dictionary uploaded successfully!")

                # Show ignored fields
                if result["ignored_fields"]:
                    st.warning("The following Excel rows were ignored because they are not CKAN fields:")
                    st.write(result["ignored_fields"])

                # Show updated fields
                st.info("Updated metadata for the following CKAN fields:")
                st.write(result["updated_fields"])

                # Show CKAN response
                st.json(result["ckan_response"])

# --- Delete all resources ---
with tab12:
    st.markdown("### Remove All Resources from Dataset")
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

    st.markdown("### Search by Date Created")
    st.markdown("Great for end‑of‑year reporting, onboarding, and curator audits 😎")

    # ---------------------------------------------------------
    # Ensure session state key exists (prevents attribute errors)
    # ---------------------------------------------------------
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

    # ---------------------------------------------------------
    # 1. Load all native organizations (id + title)
    #    get_native_orgs() returns: [(org_id, org_title), ...]
    # ---------------------------------------------------------

    org_list = get_native_orgs()

    # Build UI labels (titles only)
    org_titles = [title for oid, title in org_list]

    # Map title → id for backend filtering
    org_lookup = {title: oid for oid, title in org_list}

    # ---------------------------------------------------------
    # 2. Organization multiselect (titles only)
    # ---------------------------------------------------------
    st.markdown(" ")
    selected_org_titles = st.multiselect(
        "Select organizations (All CanWIN hosted orgs selected by default)",
        options=org_titles,
        default=org_titles,   # Default = all native orgs
        key="t13_orgs"
    )

    # Convert selected titles → IDs for backend
    selected_org_ids = [org_lookup[t] for t in selected_org_titles]

    # ---------------------------------------------------------
    # 3. Type multiselect
    # ---------------------------------------------------------
    st.markdown(" ")
    selected_types = st.multiselect(
        "Select record types:",
        options=["dataset", "project", "publication"],
        default=["dataset", "project", "publication"],
        key="t13_types"
    )

    # ---------------------------------------------------------
    # 4. Date range selection
    # ---------------------------------------------------------
    default_start = datetime.date(2022, 1, 1)
    default_end = datetime.date.today()

    st.markdown(" ")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=default_start, key="t13_start")
    with col2:
        end_date = st.date_input("End date", value=default_end, key="t13_end")

    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()

    # ---------------------------------------------------------
    # 5. Search button — uses cached backend search
    # ---------------------------------------------------------
    if st.button("Search", key="t13_search"):
        with st.spinner("Searching cached CKAN records…"):
            st.session_state.search_results = search_datasets_by_date(
                start_date,
                end_date,
                allowed_orgs=selected_org_ids,
                allowed_types=selected_types
            )

            if not st.session_state.search_results:
                st.warning("No public native records found within this date range.")

    # ---------------------------------------------------------
    # 6. Render results (if any)
    # ---------------------------------------------------------
    if st.session_state.search_results:

        results = st.session_state.search_results

        # Keep only items marked in_range by backend
        active_results = [d for d in results if d.get("in_range", False)]

        st.success(f"Found {len(active_results)} record(s) within the selected date window")
        st.caption(f"Total public native records (before date filtering): {len(results)}")

        # ---------------------------------------------------------
        # TABLE 1 — Detailed results
        # ---------------------------------------------------------
        table_rows = []
        for d in active_results:
            name = d.get("name")
            d_type = d.get("type", "unknown").lower()
            created_date = d.get("display_date_clean", "Unknown")
            org_title = d.get("organization", {}).get("title", "(No org)")

            # URL rule: datasets + projects use /dataset/
            base_path = "dataset" if d_type in ["dataset", "project"] else d_type
            url = f"https://canwin-datahub.ad.umanitoba.ca/data/{base_path}/{name}"

            table_rows.append({
                "Title": d.get("title") or "(No title)",
                "Organization": org_title,
                "Type": d_type.capitalize(),
                "Created": created_date,
                "URL": url
            })

        st.markdown(" ")
        st.markdown("#### Detailed Results")
        st.dataframe(table_rows, use_container_width=True)

        # ---------------------------------------------------------
        # TABLE 2 — Summary by year
        # ---------------------------------------------------------
        st.markdown("#### Summary: Total Count by Year")

        year_counts = {}
        for d in active_results:
            year = d.get("extracted_year")
            if year != "Unknown":
                year_counts[year] = year_counts.get(year, 0) + 1

        if year_counts:
            summary_rows = [
                {"Year": str(yr), "Total Count": year_counts[yr]}
                for yr in sorted(year_counts.keys())
            ]
            st.dataframe(summary_rows, use_container_width=True)
        else:
            st.info("No valid year information available.")

        # ---------------------------------------------------------
        # TABLE 3 — Total count
        # ---------------------------------------------------------
        st.markdown("#### Total Count")
        st.metric("Records in selected period", len(active_results))
