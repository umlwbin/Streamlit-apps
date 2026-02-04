"""
widgets.py — UI Layer for the Idronaut CTD Workflow
---------------------------------------------------

This file contains all Streamlit UI code for the Idronaut workflow.
If you're new to the project, this is the best place to understand
how the user interacts with each step of the cleaning process.

Understanding the step pattern
------------------------------
Every step function in this file follows the same structure:

    1. Show a header (e.g., "#### 2. Select Downcast Rows")
    2. Determine whether the step is active:
           active = (st.session_state.idronaut_step == STEP_NUMBER)
    3. If NOT active:
           • Show a summary of what the user previously entered
           • Provide a button to reopen the step
           • Return early
    4. If active:
           • Load or prepare any required data
           • Render UI controls (plots, inputs, buttons)
           • Save user inputs to session_state
           • Move to the next step with go_to_step()

How session_state is used
-------------------------
The workflow stores all user inputs in session_state, including:
    • Uploaded files
    • Downcast row selections
    • Metadata (lat/lon/site)
    • Cleaned DataFrames
    • The currently loaded DataFrame (current_df)
    • The current workflow step

Each step reads from and writes to these values.

Step 2 has detailed comments, use this step as a guide for the overall UI structure of each step.
Step 5, the cleaning step also has detailed comments, explaining the workflow mechanics.
"""



import streamlit as st

from state import (
    go_to_step,
    reset_idronaut_workflow,
    reset_for_next_file,
)

from processing.processing import (
    read_idronaut_file,
    clean_idronaut_file,
    subset_downcast,
)

from processing.plotting import plot_pressure_vs_row, plot_temp_vs_pressure

from ui_utils import big_caption

# ---------------------------------------------------------
# INTRO (always shown)
# ---------------------------------------------------------
def idronaut_intro():
    
    with st.sidebar:
        st.title("Idronaut CTD Data Processor 🌊 ")

        big_caption(
            "A guided workflow for cleaning Idronaut CTD files. "
            "This workflow helps you identify the downcast, crop the data, "
            "add required metadata, and curate the file to CanWIN best practices."
        )
        st.markdown("---")
        st.image('img/UM-EarthObservationScience-cmyk-left.png',width=200)


    st.markdown("## Idronaut Curation Workflow 🌊")
    
    # --- Start Over button ---
    if st.button("🔄 Start Over", key="dg_start_over"):
        reset_idronaut_workflow()
        st.rerun()

    # --- Progress bar ---
    total_steps = 7
    
    # If no files uploaded yet, show progress as 0
    if not st.session_state.idronaut_files:
        current_step = 0
    else:
        current_step = st.session_state.idronaut_step

    progress = current_step / total_steps
    with st.container(border=True):
        st.markdown("##### Workflow Progress")
        st.progress(progress)
        st.caption(f"Step {current_step} of {total_steps}")
    st.markdown('')


# ---------------------------------------------------------
# STEP 1 — UPLOAD
# ---------------------------------------------------------
def upload_step():
    st.markdown("#### 1. Upload Idronaut Files")

    active = (st.session_state.idronaut_step == 1)

    if not active:
        if st.session_state.idronaut_files:
            st.success(f"{len(st.session_state.idronaut_files)} file(s) uploaded.")
            if st.button("Change Uploads", key="idronaut_change_uploads"):
                reset_idronaut_workflow()
                st.rerun()
        else:
            st.info("Waiting for upload…")
        return

    # ACTIVE STEP
    files = st.file_uploader(
        "Upload one or more Idronaut CSV/TXT files",
        type=["csv", "txt"],
        accept_multiple_files=True,
        key="idronaut_upload",
    )

    if files:
        st.session_state.idronaut_files = files

    if st.button("Next", key="idronaut_next_1"):
        if st.session_state.idronaut_files:
            go_to_step(2)


# Use step 2 comments as guide for other steps.
# ---------------------------------------------------------
# STEP 2 — SELECT DOWNCAST
# ---------------------------------------------------------
def select_downcast_step():
    # This header is always shown, whether the step is active or collapsed.
    st.markdown("#### 2. Select Downcast Rows")

    # The index of the file we are currently working on.
    idx = st.session_state.idronaut_current_file_index

    # All uploaded files (from Step 1).
    files = st.session_state.idronaut_files

    # If no files exist yet, we cannot proceed.
    if not files or idx >= len(files):
        st.info("Waiting for upload…")
        return

    # Determine whether this step is currently active.
    # Only the active step shows input widgets.
    active = (st.session_state.idronaut_step == 2)

    # The file object for the current file.
    file = files[idx]

    # ---------------------------------------------------------
    # Load the file into a DataFrame (only when entering this step)
    # ---------------------------------------------------------
    # We reset current_df when the user *intentionally* enters Step 2.
    # This ensures the plot always reflects the correct file.
    if active and st.session_state.current_df is not None:
        st.session_state.current_df = None

    # If current_df is empty, load the file using our processing function.
    # This ensures the file is only read once per step.
    if st.session_state.current_df is None:
        df, error = read_idronaut_file(file)

        # If the file has formatting issues, show the error and stop.
        if error:
            st.error(error)
            return

        # Store the loaded DataFrame in session state.
        st.session_state.current_df = df

    # For convenience, assign the DataFrame to a local variable.
    df = st.session_state.current_df

    # ---------------------------------------------------------
    # COLLAPSED STATE (step is not active)
    # ---------------------------------------------------------
    # When the user has already completed this step, we show a summary
    # instead of the full UI. This keeps the workflow tidy.
    if not active:
        if idx in st.session_state.idronaut_downcast_ranges:
            start, end = st.session_state.idronaut_downcast_ranges[idx]

            # Show a friendly summary of what the user selected earlier.
            st.success(f"File {idx+1}: Selected rows {start} to {end}")

            # Allow the user to re-open the step if needed.
            if st.button("Change Downcast Selection", key=f"idronaut_change_downcast_{idx}"):
                go_to_step(2)
        else:
            # If no selection exists yet, show a placeholder message.
            st.info(f"Waiting for File {idx+1} downcast selection…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (full UI shown)
    # ---------------------------------------------------------

    # Show the pressure-vs-row plot to help the curator identify the downcast.
    st.plotly_chart(plot_pressure_vs_row(df))

    # Two number inputs allow the curator to choose the downcast range.
    # Default values (500–1000) are just placeholders.
    start = st.number_input(
        "Start row",
        min_value=0,
        value=500,
        key=f"start_row_{idx}"
    )

    end = st.number_input(
        "End row",
        min_value=0,
        value=1000,
        key=f"end_row_{idx}"
    )

    # When the user clicks Next:
    #   1. Save the selected range in session state
    #   2. Move to Step 3
    if st.button("Next", key=f"idronaut_next_2_{idx}"):
        st.session_state.idronaut_downcast_ranges[idx] = (start, end)
        go_to_step(3)


# ---------------------------------------------------------
# STEP 3 — PREVIEW DOWNCAST
# ---------------------------------------------------------
def preview_downcast_step():
    st.markdown("#### 3. Preview Downcast")

    idx = st.session_state.idronaut_current_file_index
    active = (st.session_state.idronaut_step == 3)

    if not st.session_state.idronaut_files:
        return

    if not active:
        if idx in st.session_state.idronaut_downcast_ranges:
            st.success(f"File {idx+1}: Preview complete.")
            if st.button("Re-preview Downcast", key=f"idronaut_repreview_{idx}"):
                go_to_step(3)
        else:
            st.info(f"Waiting for File {idx+1} preview…")
        return

    # ACTIVE STEP
    big_caption("Plotting Pressure Vs Temperature")
    df = st.session_state.current_df
    start, end = st.session_state.idronaut_downcast_ranges[idx]

    down = subset_downcast(df, start, end)
    st.plotly_chart(plot_temp_vs_pressure(down))

    if st.button("Next", key=f"idronaut_next_3_{idx}"):
        go_to_step(4)


# ---------------------------------------------------------
# STEP 4 — ENTER METADATA
# ---------------------------------------------------------
def enter_metadata_step():
    st.markdown("#### 4. Enter Metadata")

    idx = st.session_state.idronaut_current_file_index
    active = (st.session_state.idronaut_step == 4)

    if not st.session_state.idronaut_files:
        return

    if not active:
        if idx in st.session_state.idronaut_latlon_site:
            meta = st.session_state.idronaut_latlon_site[idx]
            st.success(
                f"File {idx+1}: Metadata — lat={meta['lat']}, lon={meta['lon']}, site={meta['site']}"
            )
            if st.button("Change Metadata", key=f"idronaut_change_metadata_{idx}"):
                go_to_step(4)
        else:
            st.info(f"Waiting for File {idx+1} metadata…")
        return

    # ACTIVE STEP
    lat = st.number_input("Latitude (decimal degrees)", key=f"lat_{idx}")
    lon = st.number_input("Longitude (decimal degrees)", key=f"lon_{idx}")
    site = st.text_input("Site ID", key=f"site_{idx}")

    if st.button("Next", key=f"idronaut_next_4_{idx}"):
        st.session_state.idronaut_latlon_site[idx] = {
            "lat": lat,
            "lon": lon,
            "site": site,
        }
        go_to_step(5)


# ---------------------------------------------------------
# STEP 5 — CLEAN FILE
# ---------------------------------------------------------
def clean_file_step():
    # This header is always shown, whether the step is active or collapsed.
    st.markdown("#### 5. Clean File")

    idx = st.session_state.idronaut_current_file_index
    active = (st.session_state.idronaut_step == 5)

    # If no files exist yet, we cannot proceed.
    if not st.session_state.idronaut_files:
        return

    # Ensure the cleaned_frames list is long enough to store output
    # for the current file index. This allows us to assign directly
    # into the list later.
    while len(st.session_state.idronaut_cleaned_frames) <= idx:
        st.session_state.idronaut_cleaned_frames.append(None)

    # ---------------------------------------------------------
    # COLLAPSED STATE (step is not active)
    # ---------------------------------------------------------
    # When the user has already completed this step for this file,
    # we show a summary instead of the full UI.
    if not active:
        if st.session_state.idronaut_cleaned_frames[idx] is not None:
            st.success(f"File {idx+1} cleaned.")
            # Allow the user to re-open the step if needed.
            if st.button("Re-clean File", key=f"idronaut_reclean_{idx}"):
                go_to_step(5)
        else:
            st.info(f"Waiting for File {idx+1} cleaning…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (full UI shown)
    # ---------------------------------------------------------
        # ---------------------------------------------------------
    # Show the cleaning steps applied to this file
    # ---------------------------------------------------------
    st.markdown("""
    **This cleaning step applies the following transformations:**

    1. **Subset the downcast rows**  
    Only the rows you selected in Step 2 are kept.

    2. **Combine Date + Time into a single Datetime column**  
    Multiple date/time formats are supported and parsed safely.

    3. **Insert metadata**  
    Adds Site ID, Latitude, and Longitude from Step 4.

    4. **Rename columns to CanWIN standard names**  
    Ensures consistent naming across all Idronaut files.

    5. **Add RVQ (Result Value Qualifier) columns**  
    Creates empty RVQ columns for each variable.
    """)

    # The DataFrame for the current file should already be loaded
    # during Step 2. We simply retrieve it here.
    df = st.session_state.current_df

    # Before cleaning, we must ensure the curator has completed
    # the required earlier steps for this file:
    #   - Downcast selection (Step 2)
    #   - Metadata entry (Step 4)
    #
    # If either is missing, we show a warning and stop.
    if idx not in st.session_state.idronaut_downcast_ranges:
        st.warning("Downcast selection missing.")
        return

    if idx not in st.session_state.idronaut_latlon_site:
        st.warning("Metadata missing.")
        return

    # Retrieve the user inputs for this file
    start, end = st.session_state.idronaut_downcast_ranges[idx]
    meta = st.session_state.idronaut_latlon_site[idx]

    # ---------------------------------------------------------
    # 1. Run the full cleaning pipeline
    # ---------------------------------------------------------
    # This calls the pure‑Python cleaning function from processing.py.
    # It performs:
    #   - Downcast subsetting
    #   - Datetime merging
    #   - Metadata insertion
    #   - Column renaming
    #   - RVQ column creation
    cleaned = clean_idronaut_file(
        df,
        start,
        end,
        meta["lat"],
        meta["lon"],
        meta["site"]
    )

    # Store the cleaned DataFrame for this file
    st.session_state.idronaut_cleaned_frames[idx] = cleaned

    # Give the curator a friendly confirmation
    st.success(f"File {idx+1} cleaned successfully!")

    # ---------------------------------------------------------
    # 2. Handle multi‑file transitions
    # ---------------------------------------------------------
    if st.button("Next", key=f"idronaut_next_5_{idx}"):

        # If there are more files to process:
        if idx + 1 < len(st.session_state.idronaut_files):

            # Show a toast notification to guide the curator
            st.toast(f"Starting File {idx+2}… Scroll up to Step 1 to continue.")
            import time
            time.sleep(4)

            # Move to the next file
            st.session_state.idronaut_current_file_index += 1

            # Reset per‑file UI state (but keep cleaned outputs)
            reset_for_next_file()

            # Return to Step 2 for the next file
            go_to_step(2)
            st.rerun()

        # If this was the last file:
        else:
            # Move to the final download step
            go_to_step(6)
            st.rerun()



# ---------------------------------------------------------
# STEP 6 — DOWNLOAD
# ---------------------------------------------------------
def download_step():
    st.markdown("#### 6. Download Cleaned Data")

    active = (st.session_state.idronaut_step == 6)
    if not active:
        return

    import pandas as pd
    final = pd.concat(st.session_state.idronaut_cleaned_frames, ignore_index=True)

    # ---------------------------------------------------------
    # Final celebratory box (same style as Data Garrison)
    # ---------------------------------------------------------
    st.markdown(
        """
        <style>
        .final-download-box {
            background-color: #e6f7ff;
            border: 2px solid #1890ff;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .final-download-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #0050b3;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="final-download-box">
            <div class="final-download-title">🎉 Your Idronaut workflow is complete! Download your curated dataset</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # Download button
    # ---------------------------------------------------------
    # --- BUTTON ROW ---
    col1, col2 = st.columns([1, 1])
    with col1: 
        st.download_button(
            label="⬇️ Download Cleaned Idronaut CSV",
            data=final.to_csv(index=False).encode("utf-8"),
            file_name="idronaut_cleaned.csv",
            mime="text/csv",
            key="idronaut_download"
        )
    with col2:
        # ---------------------------------------------------------
        # Start over
        # ---------------------------------------------------------
        if st.button("🔄 Start Over", key="idronaut_start_over"):
            reset_idronaut_workflow()
            st.rerun()
