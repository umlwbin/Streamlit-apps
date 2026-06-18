import streamlit as st
from state import advance_step, go_to_step, reset_castaway_workflow
from processing.processing import build_final_dataframe

# Import parsing helpers
from processing.parsing_file import extract_metadata_and_data
from ui_utils import big_caption

# ---------------------------------------------------------
# INTRO SECTION
# ---------------------------------------------------------
def workflow_intro():
    """
    Display the introduction in the sidebar.
    This gives curators context about what the Castaway CTD workflow does,
    and shows an example file so they know what to upload.
    """

    st.markdown("## Castaway CTD Workflow ⛴️")

    # --- Start Over button ---
    if st.button("🔄 Start Over", key="dg_start_over"):
        reset_castaway_workflow()
        st.rerun()

    # --- Progress bar ---
    total_steps = 7
    
    # If no files uploaded yet, show progress as 0
    if not st.session_state.castaway_files:
        current_step = 0
    else:
        current_step = st.session_state.castaway_step

    progress = current_step / total_steps
    with st.container(border=True):
        st.markdown("##### Workflow Progress")
        st.progress(progress)
        st.caption(f"Step {current_step} of {total_steps}")

    st.markdown('')

    with st.sidebar:
        st.title("Castaway CTD Curation ⛴️")
        big_caption(
            "A guided workflow for cleaning Castaway CTD CSV files. "
            "This workflow extracts metadata, normalizes headers, "
            "adds optional variables, and prepares your files for analysis."
        )

        with st.expander("See an example of a Castaway CTD file format"):
            big_caption(
                "Your uploaded file should look similar to this example. "
                "Castaway CTD files typically contain a metadata block at the top, "
                "followed by a data table with depth, temperature, salinity, and other measurements."
            )

            st.image("img/castaway_file_example.png")
        st.markdown("---")

        st.image('img/UM-EarthObservationScience-cmyk-left.png',width=200)

# ---------------------------------------------------------
# STEP 1 - UPLOAD FILES
# ---------------------------------------------------------

def upload_step():
    """
    Step 1: Upload one or more Castaway CTD CSV files.

    This step is simple:
    - When active, it shows a file uploader.
    - When completed, it shows a summary and a button to redo the step.
    """

    st.markdown("######")
    st.markdown("##### 1. Upload Castaway CTD Files")

    active = (st.session_state.castaway_step == 1)

    if not active:
        # Show a summary when the step is already completed
        if st.session_state.castaway_files:
            st.success(f"{len(st.session_state.castaway_files)} file(s) uploaded.")
            if st.button("Change Uploads"):
                go_to_step(1)
        else:
            st.info("Waiting for upload…")
        return

    # ACTIVE STEP
    files = st.file_uploader("Upload one or more Castaway CTD CSV files", type="csv",accept_multiple_files=True)
    
    if files:
        st.session_state.castaway_files = files
        st.session_state.castaway_custom_names = None

    if st.button("Next", key="next_upload"):
        if st.session_state.castaway_files:
            advance_step()


# ---------------------------------------------------------
# STEP 2 - EXTRACT METADATA + DATA
# ---------------------------------------------------------

def extract_step():
    """
    Step 2: Extract metadata and data tables from each uploaded file.

    This step:
    - Reads each file
    - Splits metadata (top block) from the data table
    - Stores both in session_state for later steps
    """

    st.markdown("######")
    st.markdown("##### 2. Extract Metadata and Data")

    active = (st.session_state.castaway_step == 2)

    if not active:
        if st.session_state.castaway_metadata:
            st.success("Metadata extracted.")
            if st.button("Re-extract"):
                go_to_step(2)
        else:
            st.info("Waiting for extraction…")
        return

    # ACTIVE STEP
    metadata_list, data_list = extract_metadata_and_data(st.session_state.castaway_files)

    st.session_state.castaway_metadata = metadata_list
    st.session_state.castaway_data = data_list

    st.markdown("**Metadata Preview**")
    st.dataframe(metadata_list[0].head(15))

    st.markdown("**Data Preview**")
    st.dataframe(data_list[0].head())

    if st.button("Next", key="next_extract"):
        advance_step()


# ---------------------------------------------------------
# STEP 3 - SELECT METADATA VARIABLES
# ---------------------------------------------------------

from processing.normalizing_headers import clean_metadata_name

def select_metadata_step():
    """
    Step 3: Let the user choose which metadata variables to extract.

    - Cleans metadata variable names (removes leading %, symbols, etc.)
    - Automatically pre-selects common Castaway metadata fields:
        Cast time (UTC)
        Start latitude
        Start longitude
        File name
    """

    st.markdown("######")
    st.markdown("##### 3. Select Metadata Variables to Extract")

    active = (st.session_state.castaway_step == 3)

    if not active:
        if st.session_state.castaway_selected_vars:
            st.success("Selected: " + ", ".join(st.session_state.castaway_selected_vars))
            if st.button("Change Metadata Selection"):
                st.session_state.castaway_custom_names = None
                go_to_step(3)
        else:
            st.info("Waiting for selection…")
        return

    # ACTIVE STEP
    metadata_df = st.session_state.castaway_metadata[0]

    # Clean the metadata variable names
    raw_vars = metadata_df["Variable"].astype(str).tolist()
    cleaned_vars = [clean_metadata_name(v) for v in raw_vars]

    # Default variables you want pre-selected
    default_vars = [
        "Cast time UTC",
        "Start latitude",
        "Start longitude",
        "File name"
    ]

    # Only pre-select those that actually exist in the file
    defaults_present = [v for v in default_vars if v in cleaned_vars]

    selected = st.multiselect(
        "Choose variables to extract",
        options=cleaned_vars,
        default=defaults_present,
        placeholder="Select metadata variables..."
    )

    st.info(
        "If you extract **Cast time UTC**, **Start latitude**, or **Start longitude**, "
        "they will be automatically renamed to their required ODV names:\n\n"
        "- yyyy-mm-ddThh:mm:ss.sss\n"
        "- Latitude [degrees_north]\n"
        "- Longitude [degrees_east]\n\n"
        "These variables are ODV‑required and will not appear in the rename table in step 6."
    )
    

    if st.button("Next", key="next_select"):
        st.session_state.castaway_selected_vars = selected
        advance_step()


# ---------------------------------------------------------
# STEP 4- ADD NEW VARIABLES
# ---------------------------------------------------------
def add_new_vars_step():
    """
    Step 4: Allow the curator to add new variables manually.
    - Cruise, Station, Type are always present
    """

    st.markdown("######")
    st.markdown("##### 4. Add New Variables")

    active = (st.session_state.castaway_step == 4)

    if not active:
        if st.session_state.castaway_new_vars is not None:
            if st.session_state.castaway_new_vars:
                st.success(
                    "Added variables: " +
                    ", ".join(st.session_state.castaway_new_vars.keys())
                )
            else:
                st.info("No new variables added.")
            if st.button("Change New Variables"):
                go_to_step(4)
        else:
            st.info("Waiting for new variables to add…")
        return

    # ---------------------------------------------------------
    # 1. Ensure Cruise / Station / Type exist by default
    # ---------------------------------------------------------
    required = {"Cruise": "", "Station": "", "Type": ""}

    if st.session_state.castaway_new_vars is None:
        st.session_state.castaway_new_vars = required.copy()
    else:
        # Ensure required keys exist even if user revisits the step
        for k, v in required.items():
            st.session_state.castaway_new_vars.setdefault(k, v)

    vars_dict = st.session_state.castaway_new_vars.copy()

    st.markdown(" ")
    st.markdown("**Required ODV Variables**")
    st.info("These **must** be present for ODV compatibility. \n\n**Bot.Depth [m]** is automatically extracted from the last value in the Depth column.")


    # ---------------------------------------------------------
    # 2.  Show Required variables
    # ---------------------------------------------------------
    for key in ["Cruise", "Station", "Type"]:
        val = vars_dict.get(key, "")

        st.markdown(f"**{key}**")
        vars_dict[key] = st.text_input(f"Enter **{key}** value", value=val,)
        st.markdown(" ")


    # ---------------------------------------------------------
    # 3. Validation warnings
    # ---------------------------------------------------------
    missing_required = [k for k in required if vars_dict.get(k, "").strip() == ""]

    if missing_required:
        st.warning(
            "⚠️ The following required ODV variables are blank: "
            + ", ".join(missing_required)
        )

    # Detect misspellings (user renamed them incorrectly)
    # Required keys MUST be exactly Cruise, Station, Type
    user_keys = set(vars_dict.keys())
    required_keys = set(required.keys())

    misspelled = [
        k for k in user_keys
        if any(req.lower() in k.lower() and k not in required_keys for req in required_keys)
    ]

    if misspelled:
        st.error(
            "❌ These variables look like misspellings of required ODV fields: "
            + ", ".join(misspelled)
        )
        st.info("Required names must be: Cruise, Station, Type")

    # ---------------------------------------------------------
    # 4. Ask whether the user wants to add more variables
    # ---------------------------------------------------------
    st.markdown("---")
    add = st.radio("Add additional variables?", ["Yes", "No"], index=None)

    if add is None:
        return

    if add == "No":
        st.session_state.castaway_new_vars = vars_dict
        advance_step()
        return

    # ---------------------------------------------------------
    # 5. Add additional variables
    # ---------------------------------------------------------
    num = st.number_input("How many additional variables?", min_value=1, value=1)

    for i in range(num):
        col1, col2 = st.columns(2)
        name = col1.text_input(f"Variable {i+1} name")
        value = col2.text_input(f"Variable {i+1} value")
        if name:
            vars_dict[name] = value

    if st.button("Next", key="next_newvars"):
        st.session_state.castaway_new_vars = vars_dict
        advance_step()





# ---------------------------------------------------------
# STEP 5- OMIT VARIABLES
# ---------------------------------------------------------
def omit_vars_step():
    """
    Step 5: Let the curator remove unwanted columns from the data table.
    """

    st.markdown("######")
    st.markdown("##### 5. Omit Unnecessary Variables")

    active = (st.session_state.castaway_step == 5)

    if not active:
        if st.session_state.castaway_omit_vars is not None:
            st.success(
                "Omitted: " + ", ".join(st.session_state.castaway_omit_vars)
                if st.session_state.castaway_omit_vars else "No variables omitted."
            )
            if st.button("Change Omitted Variables"):
                go_to_step(5)
        else:
            st.info("Waiting to omit unneeded variables...")
        return

    # ACTIVE STEP
    df = st.session_state.castaway_data[0]
    cols = df.columns.tolist()

    omit = st.multiselect(
        "Select columns to remove",
        cols,
        default=[c for c in cols if "Sound velocity" in c or "Density" in c]
    )

    if st.button("Next", key="next_omit"):
        st.session_state.castaway_omit_vars = omit
        advance_step()




# ---------------------------------------------------------
# STEP 6 - RENAME VARIABLES
# ---------------------------------------------------------
from processing.normalizing_headers import clean_metadata_name
from processing.helpers import safe_insert_column

def normalize_variables_step():
    """
    Step 6: Allow the User to manually rename variables using an editable table.
    """

    st.markdown("######")
    st.markdown("##### 6. Rename Variables")

    active = (st.session_state.castaway_step == 6)

    if not active:
        if st.session_state.castaway_custom_names is not None:
            st.success("Custom variable names saved.")
            if st.button("Change Variable Names"):
                go_to_step(6)
        else:
            st.info("Waiting for normalization choice…")
        return

    # ---------------------------------------------------------
    # Build the dataframe exactly as it will appear BEFORE renaming
    # ---------------------------------------------------------
    df = st.session_state.castaway_data[0].copy()

    # Insert selected metadata variables
    meta = st.session_state.castaway_metadata[0]
    for var in st.session_state.castaway_selected_vars:
        var_clean = clean_metadata_name(var)
        row = meta[meta["Variable"].astype(str).str.contains(var, regex=False)]
        if not row.empty:
            value = row["Value"].iloc[0]
            safe_insert_column(df, var_clean, value)

    # Insert required ODV variables (Cruise, Station, Type only)
    required = {"Cruise": "", "Station": "", "Type": ""}
    for k, v in required.items():
        safe_insert_column(df, k, v)

    # Insert user-added variables
    if st.session_state.castaway_new_vars:
        for name, value in st.session_state.castaway_new_vars.items():
            safe_insert_column(df, name, value)

    # Remove omitted variables
    if st.session_state.castaway_omit_vars:
        df = df.drop(columns=st.session_state.castaway_omit_vars, errors="ignore")

    # ---------------------------------------------------------
    # Extract columns for rename table
    # ---------------------------------------------------------
    original_cols = df.columns.tolist()

    # ODV-required variables (remove anything that will be auto-standardized)
    def is_non_editable(name):
        n = name.lower()
        return (
            "cruise" in n or
            "station" in n or
            "type" in n or
            "cast time" in n or
            n == "yyyy-mm-ddthh:mm:ss.sss" or
            "longitude" in n or
            "latitude" in n or
            n == "bot. depth [m]"
        )

    editable_cols = [c for c in original_cols if not is_non_editable(c)]


    # ---------------------------------------------------------
    # Build editable table
    # ---------------------------------------------------------
    import pandas as pd
    table_df = pd.DataFrame({
        "Original Name": editable_cols,
        "New Name": editable_cols.copy()
    })


    st.info("**You can rename any variable in the table below**. \n\nODV-required variables are not editable and have been excluded from the table. \n" 
    "These variables will appear in your final dataset exactly as shown:\n\n"
    "- Cruise\n"
    "- Station\n"
    "- Type\n"
    "- yyyy-mm-ddThh:mm:ss.sss\n"
    "- Longitude [degrees_east]\n"
    "- Latitude [degrees_north]\n"
    "- Bot. Depth [m]\n\n"
    "Note: **Bot. Depth [m]** is automatically extracted as the last "
        "non-missing value in the **Depth** column."
        )

    edited = st.data_editor(
        table_df,
        num_rows="dynamic",
        use_container_width=True,
        key="castaway_name_editor"
    )


    # ---------------------------------------------------------
    # Save and continue
    # ---------------------------------------------------------
    if st.button("Next", key="next_normalize"):
        st.session_state.castaway_custom_names = {
            row["Original Name"]: row["New Name"]
            for _, row in edited.iterrows()
        }
        advance_step()


# ---------------------------------------------------------
# STEP 7 - DOWNLOAD CLEANED DATA
# ---------------------------------------------------------

def download_step():
    """
    Step 7: Build the final cleaned dataset and provide a download button.

    This step:
    - Combines all cleaned files
    - Applies metadata selections
    - Applies normalization
    - Applies new variables and omissions
    - Shows a preview
    - Lets the curator download the final CSV
    """

    st.markdown("######")
    st.markdown("##### 7. Download Cleaned Data")

    active = (st.session_state.castaway_step == 7)
    if not active:
        return

    # ---------------------------------------------------------
    # Build final dataframe using all previous choices
    # ---------------------------------------------------------
    final_df = build_final_dataframe(
        st.session_state.castaway_data,
        st.session_state.castaway_metadata,
        st.session_state.castaway_selected_vars,
        st.session_state.castaway_new_vars,
        st.session_state.castaway_omit_vars,
        st.session_state.castaway_custom_names    
    )

    num_files = len(st.session_state.castaway_data)

    st.success(
        f"All done! 🎉🎉\n\nYour cleaned Castaway CTD file is ready.\n\n"
        f"**{num_files} file(s) were merged successfully.**"
    )

    st.info(
        "The variable **Bot. Depth [m]** was automatically extracted as the last "
        "non-missing value in the **Depth** column for each file."
    )

    # ---------------------------------------------------------
    # Final preview
    # ---------------------------------------------------------
    st.markdown(" ")
    st.markdown("**Final Preview**")
    st.dataframe(final_df.head(50), use_container_width=True)

    # ---------------------------------------------------------
    # Download button
    # ---------------------------------------------------------
    st.download_button(
        "⬇️ Download Cleaned CSV",
        final_df.to_csv(index=False).encode("utf-8"),
        file_name="castaway_cleaned.csv",
        mime="text/csv",
        key="download_button"
    )
