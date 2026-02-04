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
    and shows an example file so they know what to expect.
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
            "This workflow extracts metadata, removes header rows, "
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
# STEP 1 — UPLOAD FILES
# ---------------------------------------------------------

def upload_step():
    """
    Step 1: Upload one or more Castaway CTD CSV files.

    This step is simple:
    - When active, it shows a file uploader.
    - When completed, it shows a summary and a button to redo the step.
    """
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

    if st.button("Next", key="next_upload"):
        if st.session_state.castaway_files:
            advance_step()


# ---------------------------------------------------------
# STEP 2 — EXTRACT METADATA + DATA
# ---------------------------------------------------------

def extract_step():
    """
    Step 2: Extract metadata and data tables from each uploaded file.

    This step:
    - Reads each file
    - Splits metadata (top block) from the data table
    - Stores both in session_state for later steps
    """
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
    metadata_list, data_list = extract_metadata_and_data(
        st.session_state.castaway_files
    )

    st.session_state.castaway_metadata = metadata_list
    st.session_state.castaway_data = data_list

    st.markdown("**Metadata Preview**")
    st.dataframe(metadata_list[0].head())

    st.markdown("**Data Preview**")
    st.dataframe(data_list[0].head())

    if st.button("Next", key="next_extract"):
        advance_step()


# ---------------------------------------------------------
# STEP 3 — SELECT METADATA VARIABLES
# ---------------------------------------------------------

def select_metadata_step():
    """
    Step 3: Let the curator choose which metadata variables to extract.

    These selected variables will later be added as new columns
    to the cleaned data table.
    """
    st.markdown("##### 3. Select Metadata Variables to Extract")

    active = (st.session_state.castaway_step == 3)

    if not active:
        if st.session_state.castaway_selected_vars:
            st.success(
                "Selected: " + ", ".join(st.session_state.castaway_selected_vars)
            )
            if st.button("Change Metadata Selection"):
                go_to_step(3)
        else:
            st.info("Waiting for selection…")
        return

    # ACTIVE STEP
    metadata_df = st.session_state.castaway_metadata[0]
    vars_list = metadata_df["Variable"].tolist()

    selected = st.multiselect("Choose variables to extract", vars_list)

    if st.button("Next", key="next_select"):
        st.session_state.castaway_selected_vars = selected
        advance_step()


# ---------------------------------------------------------
# STEP 4 — NORMALIZE VARIABLE NAMES
# ---------------------------------------------------------

def normalize_variables_step():
    """
    Step 4: Choose how column names should be formatted.

    Options:
    - Keep original names
    - snake_case
    - ODV-friendly (UPPERCASE_UNDERSCORES)

    This ensures consistent naming across files.
    """
    st.markdown("##### 4. Normalize Variable Names")

    active = (st.session_state.castaway_step == 4)

    if not active:
        norm = st.session_state.get("castaway_normalization")
        if norm:
            st.success(f"Normalization: {norm}")
            if st.button("Change Normalization"):
                go_to_step(4)
        else:
            st.info("Waiting for normalization choice…")
        return

    # ACTIVE STEP
    choice = st.radio(
        "Choose how variable names should be normalized:",
        [
            "Keep original names",
            "snake_case",
            "ODV-friendly (UPPERCASE_UNDERSCORES)"
        ],
        index=None
    )

    if choice and st.button("Next", key="next_normalize"):
        st.session_state.castaway_normalization = choice
        advance_step()


# ---------------------------------------------------------
# STEP 5 — ADD NEW VARIABLES
# ---------------------------------------------------------

def add_new_vars_step():
    """
    Step 5: Allow the curator to add new variables manually.

    These might include:
    - Site ID
    - Deployment ID
    - Notes
    - Any contextual metadata not present in the file
    """
    st.markdown("##### 5. Add New Variables (Optional)")

    active = (st.session_state.castaway_step == 5)

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
                go_to_step(5)
        else:
            st.info("Waiting for new variables to add…")
        return

    # ACTIVE STEP
    add = st.radio("Add new variables?", ["Yes", "No"], index=None)

    if add is None:
        return

    if add == "No":
        st.session_state.castaway_new_vars = {}
        advance_step()
        return

    num = st.number_input("How many variables?", min_value=1, value=1)

    vars_dict = {}
    for i in range(num):
        col1, col2 = st.columns(2)
        name = col1.text_input(f"Variable {i+1} name")
        value = col2.text_input(f"Variable {i+1} value")
        vars_dict[name] = value

    if st.button("Next", key="next_newvars"):
        st.session_state.castaway_new_vars = vars_dict
        advance_step()


# ---------------------------------------------------------
# STEP 6 — OMIT VARIABLES
# ---------------------------------------------------------

def omit_vars_step():
    """
    Step 6: Let the curator remove unwanted columns from the data table.

    This is useful for:
    - Removing noisy variables
    - Dropping columns not needed for analysis
    - Cleaning up the final dataset
    """
    st.markdown("##### 6. Omit Unnecessary Variables")

    active = (st.session_state.castaway_step == 6)

    if not active:
        if st.session_state.castaway_omit_vars is not None:
            st.success(
                "Omitted: " + ", ".join(st.session_state.castaway_omit_vars)
                if st.session_state.castaway_omit_vars else "No variables omitted."
            )
            if st.button("Change Omitted Variables"):
                go_to_step(6)
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
# STEP 7 — DOWNLOAD CLEANED DATA
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
    st.markdown("##### 7. Download Cleaned Data")

    active = (st.session_state.castaway_step == 7)

    if not active:
        return

    # Build final dataframe using all previous choices
    final_df = build_final_dataframe(
        st.session_state.castaway_data,
        st.session_state.castaway_metadata,
        st.session_state.castaway_selected_vars,
        st.session_state.castaway_new_vars,
        st.session_state.castaway_omit_vars,
    )

    st.success("All done! 🎉 Your cleaned Castaway CTD file is ready.")

    # --- FINAL PREVIEW ---
    st.markdown("**Final Preview**")
    st.dataframe(final_df.head(50), use_container_width=True)

    # --- BUTTON ROW ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.download_button(
            "⬇️ Download Cleaned CSV",
            final_df.to_csv(index=False).encode("utf-8"),
            file_name="castaway_cleaned.csv",
            mime="text/csv",
            key="download_button"
        )

    with col2:
        if st.button("🔄 Start Over", key="start_over_button"):
            reset_castaway_workflow()






