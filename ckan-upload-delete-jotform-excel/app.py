import streamlit as st
import pandas as pd

# Import pure Python logic from core/
from core.dataset_builder import create_dataset_dict
from core.ckan import upload_metadata, delete_dataset

# Page Setup
st.set_page_config(page_title="CKAN Dataset Upload & Delete", layout="centered")
st.title("📦 CKAN Dataset Upload & Delete")
st.info(''' 
    This app uploads or deletes a dataset to/from CKAN, using an excel submissions file generated from Jotform.
    Please see the **submissions_new.xlsx** file as an example of what the fields look like. 
    ''')

# Password Protection
APP_PASSWORD = "C3osE&Gdm"
if "pwdSuccess" not in st.session_state:
    st.session_state.pwdSuccess = False

with st.sidebar:
    st.header("🕵🏻‍♀️ Enter Password")
    password = st.text_input("Password", type="password")
    if password == APP_PASSWORD:
        st.session_state.pwdSuccess = True
        st.success("Welcome you beautiful Data Legend!! 😎")
        st.markdown(" ")
        st.markdown("# 🔐 CKAN API Authentication")
        ckan_api_key = st.text_input("Enter your CKAN API Key", type="password", key="apiKey")
        ckan_base_url = st.text_input("Enter CKAN Base URL (e.g., https://data.example.com)",key= "baseURL", value="https://canwin-datahub.ad.umanitoba.ca/data")

    elif password:
        st.error("Incorrect password ❌")

# Tabs
st.markdown(" ")
tab1, lilSpace, tab2 = st.tabs(["⬆️ **Upload Dataset**", ' ', "❌ **Delete Dataset**"])

with tab1:

    # ---------------------------------------------------------
    # 0. ACCESS CHECK
    # ---------------------------------------------------------
    if st.session_state.pwdSuccess and st.session_state.get("apiKey") and st.session_state.get("baseURL"):

        st.header("📦 CKAN Dataset Uploader")
        st.write("Upload one or more datasets to CKAN.")

        # ---------------------------------------------------------
        # 1. FILE UPLOAD SECTION
        # ---------------------------------------------------------
        st.subheader("Upload Your Excel File")

        user_resource_type = st.text_input("Optional: Enter a specific Resource Type (e.g., KuKa Data)",
            value=""
        )

        uploaded_file = st.file_uploader("Upload an Excel file containing metadata for one or more datasets.",
            type=["xlsx"]
        )

        # ---------------------------------------------------------
        # 1A. CLEAR SCREEN WHEN FILE IS REMOVED OR REPLACED
        # ---------------------------------------------------------
        if "last_uploaded_filename" not in st.session_state:
            st.session_state["last_uploaded_filename"] = None

        current_filename = uploaded_file.name if uploaded_file else None

        # If the file changed OR was removed ---> clear all processing state
        if current_filename != st.session_state["last_uploaded_filename"]:
            st.session_state["last_uploaded_filename"] = current_filename

            # Clear everything related to processing
            st.session_state["dataset_dicts"] = None
            st.session_state["current_index"] = 0
            st.session_state["missing_fields"] = None
            st.session_state["failed_dataset"] = None

            # Clear any leftover missing-field text inputs
            for key in list(st.session_state.keys()):
                if key.startswith("missing_"):
                    del st.session_state[key]

            # Force a clean UI refresh
            st.rerun()

        # ---------------------------------------------------------
        # 2. PROCESS FILE ---> BUILD DATASET DICTS
        # ---------------------------------------------------------
        if uploaded_file and st.button("Process Upload"):

            df = pd.read_excel(uploaded_file)
            normalized_cols = [col.strip() for col in df.columns]
            df.columns = normalized_cols

            resource_type_arg = user_resource_type if user_resource_type.strip() else None

            st.session_state["dataset_dicts"] = create_dataset_dict(
                df,
                normalized_cols,
                resource_type=resource_type_arg
            )

            st.session_state["current_index"] = 0
            st.session_state["missing_fields"] = None
            st.session_state["failed_dataset"] = None

            st.success("File processed successfully. Ready to begin uploading datasets.")

        # ---------------------------------------------------------
        # 3. UPLOAD LOOP - ONLY RUN IF NOT FIXING MISSING FIELDS
        # ---------------------------------------------------------
        if (
            "dataset_dicts" in st.session_state
            and st.session_state["dataset_dicts"]
            and st.session_state["current_index"] < len(st.session_state["dataset_dicts"])
            and not st.session_state.get("missing_fields")
        ):

            st.subheader("Uploading Datasets to CKAN")

            dataset_dict = st.session_state["dataset_dicts"][st.session_state["current_index"]]
            st.info(f"Uploading dataset **{dataset_dict['name']}**...")

            response = upload_metadata(
                dataset_dict,
                st.session_state.apiKey,
                st.session_state.baseURL
            )

            # ---------------------------------------------------------
            # CASE A - CKAN SUCCESS
            # ---------------------------------------------------------
            if response.get("success"):
                st.success(f"✅ Successfully uploaded: {dataset_dict['name']}")
                st.json(response)

                st.session_state["current_index"] += 1

            # ---------------------------------------------------------
            # CASE B - CKAN FAILURE
            # ---------------------------------------------------------
            else:
                st.error(f"❌ Upload failed for: {dataset_dict['name']}")
                st.write(response)

                error_obj = response.get("error", {})

                # Only treat as missing fields if CKAN actually rejected the dataset
                if error_obj.get("__type") == "Validation Error":

                    # Filter out CKAN's noisy "Unknown field" messages
                    missing = [
                        field for field, msg in error_obj.items()
                        if field != "__type" and "Unknown field" not in str(msg)
                    ]

                    if missing:
                        st.session_state["missing_fields"] = missing
                        st.session_state["failed_dataset"] = dataset_dict
                    else:
                        st.warning("⚠ CKAN returned a validation error, but no required fields were identified.")
                        st.write(error_obj)

        # ---------------------------------------------------------
        # 4. MISSING FIELDS UI + RETRY
        # ---------------------------------------------------------
        if st.session_state.get("missing_fields"):

            st.subheader("🛠 Fix Missing Required Fields")
            st.warning("Some required fields are missing. Please fill them below:")

            for field in st.session_state["missing_fields"]:
                default_val = st.session_state.get(field, "")
                st.session_state[field] = st.text_input(
                    f"Enter value for {field}",
                    value=default_val,
                    key=f"missing_{field}"
                )

            if st.button("Retry Upload"):
                failed_dataset = st.session_state["failed_dataset"]

                # Update only the missing fields
                for field in st.session_state["missing_fields"]:
                    failed_dataset[field] = st.session_state[field]

                retry_response = upload_metadata(
                    failed_dataset,
                    st.session_state.apiKey,
                    st.session_state.baseURL
                )

                if retry_response.get("success"):
                    st.success(f"✅ Successfully uploaded after fixing fields: {failed_dataset['name']}")
                    st.json(retry_response)

                    # Clear state
                    st.session_state["missing_fields"] = None
                    st.session_state["failed_dataset"] = None

                    # Move to next dataset
                    st.session_state["current_index"] += 1

                else:
                    st.error("❌ Retry failed")
                    st.write(retry_response)



with tab2:
    if st.session_state.pwdSuccess and st.session_state.get("apiKey") and st.session_state.get("baseURL"):
        st.subheader("🗑️ Delete Dataset")
        dataset_id = st.text_input("Enter Dataset ID")
        if st.button("Delete Dataset"):
            response = delete_dataset(dataset_id, st.session_state.apiKey, st.session_state.baseURL)
            if response.get("success"):
                st.success(f"✅ Dataset {dataset_id} deleted successfully!")
                st.json(response)
            else:
                st.error("❌ Failed to delete dataset")
                st.write(response)