import streamlit as st
from state import advance_step, go_to_step, reset_workflow
from processing import processing
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

    st.title("Data Garrison Data Cleaner 🌨️")

    # --- Start Over button ---
    if st.button("🔄 Start Over", key="dg_start_over"):
        reset_workflow()
        st.rerun()

    # --- Progress bar ---
    total_steps = 7
    
    # If no files uploaded yet, show progress as 0
    if not st.session_state.files_raw:
        current_step = 0
    else:
        current_step = st.session_state.step

    progress = current_step / total_steps

    with st.container(border=True):
        st.markdown("### Workflow Progress")
        st.progress(progress)
        st.caption(f"Step {current_step} of {total_steps}")
    st.markdown('')

    with st.sidebar:
        st.title("Data Garrison Weather Data Curation")
        big_caption(
            "A guided workflow for cleaning Data Garrison files. "
            "Data is owned by the Manitoba Metis Federation (MMF) "
            "as part of the Weather Keeper Program, in collaboration with the Centre for Earth Observation Science (CEOS)."
        )

        st.image('img/mmf.png',width=200)




# ---------------------------------------------------------
# Step 1 — Upload Raw Files
# ---------------------------------------------------------
def step_1_upload_files():
    st.markdown("#### 1. Upload Raw DataGarrison Files")

    active = (st.session_state.step == 1)

    # ---------------------------------------------------------
    # COMPLETED STEP (user already uploaded files earlier)
    # ---------------------------------------------------------
    if not active:
        if st.session_state.files_raw:
            count = len(st.session_state.files_raw)
            st.success(f"{count} raw file(s) uploaded.")

            st.write(
                "Metadata removal is "
                + ("enabled." if st.session_state.remove_metadata else "disabled.")
            )

            # Allow user to restart the workflow and upload new files
            if st.button("Change Uploads", key="dg_change_uploads"):
                reset_workflow()
                st.rerun()
                return
        else:
            st.info("Waiting for uploads…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (user is currently uploading files)
    # ---------------------------------------------------------

    # This checkbox lets the user decide whether the workflow should
    # automatically remove metadata rows before the header.
    st.session_state.remove_metadata = st.checkbox(
        "These files contain metadata rows before the header (auto-detect and remove)",
        value=True
    )

    # Streamlit's file_uploader returns a list of UploadedFile objects.
    # These objects behave like file handles — you must call .read() to get the bytes.
    uploaded = st.file_uploader(
        "Upload one or more DataGarrison .csv or .txt files",
        type=["csv", "txt"],
        accept_multiple_files=True
    )

    # IMPORTANT:
    # UploadedFile objects can only be read ONCE.
    # So we immediately convert each file into a dictionary containing:
    #   - the file name
    #   - the raw bytes (f.read())
    if uploaded:
        st.session_state.files_raw = [
            {"name": f.name, "bytes": f.read()}
            for f in uploaded
        ]

    # Move to the next step only if files were uploaded
    if st.button("Next", key="dg_next_upload"):
        if st.session_state.files_raw:
            advance_step()




# ---------------------------------------------------------
# Step 2 — Preview Raw Files
# ---------------------------------------------------------
def step_2_preview_raw():
    st.markdown("#### 2. Preview Raw Data")

    active = (st.session_state.step == 2)

    # ---------------------------------------------------------
    # COMPLETED STEP (user already previewed earlier)
    # ---------------------------------------------------------
    if not active:
        if st.session_state.get("raw_preview_done"):
            st.success("Raw data previewed.")
            if st.button("Re-preview Raw Data", key="dg_repreview_raw"):
                go_to_step(2)
        else:
            st.info("Waiting to preview raw data…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (user is previewing files now)
    # ---------------------------------------------------------

    if not st.session_state.files_raw:
        st.warning("No files uploaded.")
        return

    # The selectbox shows the list of uploaded files.
    # Each entry is a dictionary with:
    #   {"name": "...", "bytes": b"..."}
    file_entry = st.selectbox(
        "Select a file to preview",
        st.session_state.files_raw,
        format_func=lambda f: f["name"]
    )

    if file_entry:
        # Extract the raw bytes from the selected file.
        file_bytes = file_entry["bytes"]

        # Convert bytes → text so we can display the first few lines.
        # UTF-8 is the safest default for text files.
        raw_text = file_bytes.decode("utf-8", errors="replace")

        # Split into individual lines for preview.
        raw_lines = raw_text.splitlines()

        st.markdown("##### Raw File (first 10 lines)")
        st.code("\n".join(raw_lines[:10]))

        # ---------------------------------------------------------
        # Detect the header row
        #
        # Datagarrison files often contain metadata rows before the header.
        # We detect the header by searching for the word "temperature"
        # in the first ~20 lines.
        # ---------------------------------------------------------
        header_row = next(
            (i for i, line in enumerate(raw_lines[:20]) if "temperature" in line.lower()),
            None
        )

        if header_row is None:
            st.warning("No header row containing 'Temperature' detected.")
        else:
            st.success(f"Detected header row at line {header_row + 1}")

            # Use the processing function to parse the file into a DataFrame.
            # This uses the same bytes we previewed above.
            df_preview = processing.read_datagarrison_bytes(
                file_bytes,
                remove_metadata=True
            )

            st.markdown("##### Parsed Data Preview")
            st.dataframe(df_preview.head())

    # Mark this step as complete and move on
    if st.button("Next", key="dg_next_preview"):
        st.session_state.raw_preview_done = True
        advance_step()




def step_3_wind_units():
    st.markdown("#### 3. Wind Speed Units")

    active = (st.session_state.step == 3)

    # ---------------------------------------------------------
    # COMPLETED STEP (user already answered these questions)
    # ---------------------------------------------------------
    if not active:
        # We only show the "completed" message if the user has actually
        # finished this step earlier. This is tracked with a flag we set
        # when they click "Next".
        if st.session_state.wind_settings_done:
            st.success(
                f"Raw units: {st.session_state.wind_raw_units} | "
                f"Conversion: {st.session_state.wind_convert_choice}"
            )

            # Allow the user to return and change their answers
            if st.button("Change Wind Unit Settings", key="dg_change_wind_units"):
                go_to_step(3)
        else:
            st.info("Waiting for wind unit confirmation…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (user is answering the wind unit questions now)
    # ---------------------------------------------------------

    st.markdown("##### Confirm Wind Speed Units")

    # ---------------------------------------------------------
    # Q1 — What units are the raw wind speed values in?
    #
    # Why we ask this:
    # Datagarrison files usually store wind speed in km/h, but not always.
    # The cleaning pipeline needs to know the original units so it can
    # convert them correctly (or leave them unchanged).
    #
    # st.radio() creates a set of radio buttons where the user can choose
    # exactly one option.
    # ---------------------------------------------------------
    raw_units = st.radio(
        "What units are the *raw* wind speed and gust values in?",
        ["km/h (recommended)", "m/s", "I'm not sure"],
        index=0,
        key="dg_raw_units"
    )

    # ---------------------------------------------------------
    # Q2 — Should we convert the wind speeds?
    #
    # Why we ask this:
    # Some workflows prefer m/s, others prefer to keep the original units.
    # The user decides what the final cleaned dataset should use.
    # ---------------------------------------------------------
    convert_choice = st.radio(
        "Do you want to convert the wind speeds?",
        ["No (keep original units)", "Convert to m/s"],
        index=0,
        key="dg_convert_units"
    )

    # Store the user's choices in session_state so later steps
    # (especially the cleaning pipeline) can access them.
    st.session_state.wind_raw_units = raw_units
    st.session_state.wind_convert_choice = convert_choice

    # ---------------------------------------------------------
    # Move to the next step
    #
    # When the user clicks "Next", we:
    #   1. Mark this step as completed (wind_settings_done = True)
    #   2. Advance to the next step in the workflow
    # ---------------------------------------------------------
    if st.button("Next", key="dg_next_wind_units"):
        st.session_state.wind_settings_done = True
        advance_step()




# ---------------------------------------------------------
# Step 4 — Clean Files
# ---------------------------------------------------------
def step_4_clean_files():
    st.markdown("#### 4. Clean Files")

    active = (st.session_state.step == 4)

    # ---------------------------------------------------------
    # COMPLETED STEP (user already cleaned files earlier)
    # ---------------------------------------------------------
    if not active:
        # If cleaned files exist, show a success message
        if st.session_state.files_cleaned:
            count = len(st.session_state.files_cleaned)
            st.success(f"{count} cleaned file(s) ready.")

            # Allow user to re-run the cleaning step if needed
            if st.button("Re-clean Files", key="dg_reclean"):
                go_to_step(4)
        else:
            st.info("Waiting to clean files…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (user is cleaning files now)
    # ---------------------------------------------------------

    # If no raw files were uploaded, we cannot clean anything
    if not st.session_state.files_raw:
        st.warning("No raw files found.")
        return

    st.info("Click below to clean all uploaded files.")

    # ---------------------------------------------------------
    # Show a summary of what the cleaning pipeline will do
    #
    # This helps users understand the transformations that will
    # happen to their data. It also builds trust in the workflow.
    # ---------------------------------------------------------
    st.markdown("###### Cleaning Steps That Will Be Applied")

    with st.expander("Show cleaning steps"):
        st.markdown(f"""
    1. Detect and remove metadata rows (if selected)
    2. Detect header row automatically
    3. Drop unnamed or empty columns
    4. Standardize column names using the instrument’s column map
    5. Add qualifier columns (string‑typed)
    6. Wind unit handling: raw = **{st.session_state.get('wind_raw_units', 'km/h')}**, convert = **{st.session_state.get('wind_convert_choice', 'No')}**
    7. Apply QC rules (upper/lower bounds, winter precip, wind consistency)
    8. Parse timestamps into a unified format
    9. Sort rows by timestamp and remove duplicates
    10. Reorder columns into a consistent, database‑friendly structure
    """)

    # ---------------------------------------------------------
    # Run the cleaning pipeline
    #
    # When the user clicks "Run Cleaning Pipeline":
    #   - We loop through each uploaded file
    #   - Pass the raw bytes into processing.clean_file()
    #   - Store the cleaned DataFrames in session_state
    #
    # The processing.clean_file() function handles:
    #   - reading the bytes
    #   - detecting the header
    #   - cleaning the data
    #   - applying QC rules
    #   - formatting the final output
    #
    # This keeps the UI simple and the logic centralized.
    # ---------------------------------------------------------
    if st.button("Run Cleaning Pipeline", key="dg_run_cleaning"):
        cleaned = []

        for f in st.session_state.files_raw:
            df = processing.clean_file_bytes(
                f["bytes"],
                raw_units=st.session_state.wind_raw_units,
                convert_choice=st.session_state.wind_convert_choice,
                remove_metadata=st.session_state.remove_metadata
            )

            cleaned.append(df)

        # Store the cleaned DataFrames so later steps can use them
        st.session_state.files_cleaned = cleaned

        st.success("All files cleaned successfully.")
        advance_step()


# ---------------------------------------------------------
# Step 5 — Preview Cleaned Files
# ---------------------------------------------------------
def step_5_preview_cleaned():
    st.markdown("#### 5. Preview Cleaned Data")

    active = (st.session_state.step == 5)

    # ---------------------------------------------------------
    # COMPLETED STEP (user already previewed cleaned data earlier)
    # ---------------------------------------------------------
    if not active:
        # If cleaned files exist, show a success message
        if st.session_state.files_cleaned:
            st.success("Cleaned data previewed.")

            # Allow the user to return and preview again
            if st.button("Re-preview Cleaned Data", key="dg_repreview_cleaned"):
                go_to_step(5)
        else:
            st.info("Waiting to preview cleaned data…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (user is previewing cleaned files now)
    # ---------------------------------------------------------

    # If no cleaned files exist, something went wrong or the user skipped a step
    if not st.session_state.files_cleaned:
        st.warning("No cleaned files available.")
        return

    # ---------------------------------------------------------
    # Let the user choose which cleaned file to preview
    #
    # st.session_state.files_cleaned is a list of DataFrames.
    # st.session_state.files_raw is a list of dictionaries containing:
    #   {"name": "...", "bytes": b"..."}
    #
    # We use the index of the cleaned file to match it with its original name.
    # ---------------------------------------------------------
    file_index = st.selectbox(
        "Select a cleaned file to preview",
        range(len(st.session_state.files_cleaned)),
        format_func=lambda i: st.session_state.files_raw[i]["name"]
    )

    # Retrieve the selected cleaned DataFrame
    df = st.session_state.files_cleaned[file_index]

    # Show the first few rows so the user can confirm the cleaning worked
    st.dataframe(df.head())

    # ---------------------------------------------------------
    # Move to the next step
    #
    # Once the user clicks "Next", we advance the workflow.
    # ---------------------------------------------------------
    if st.button("Next", key="dg_next_cleaned_preview"):
        advance_step()


# ---------------------------------------------------------
# Step 6 — Compile Files
# ---------------------------------------------------------
def step_6_compile():
    st.markdown("#### 6. Compile Cleaned Files")

    active = (st.session_state.step == 6)

    # ---------------------------------------------------------
    # COMPLETED STEP (user already compiled files earlier)
    # ---------------------------------------------------------
    if not active:
        # If a compiled dataset already exists, show a success message
        if st.session_state.compiled is not None:
            st.success("Compiled dataset ready.")

            # Allow the user to re-run the compile step if needed
            if st.button("Re-compile Files", key="dg_recompile"):
                go_to_step(5)
        else:
            st.info("Waiting to compile files…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (user is compiling files now)
    # ---------------------------------------------------------

    cleaned_files = st.session_state.files_cleaned

    # If no cleaned files exist, the user may have skipped a step
    if not cleaned_files:
        st.warning("No cleaned files to compile.")
        return

    # ---------------------------------------------------------
    # Explain what “compiling” means
    #
    # Compiling simply means:
    #   - If there is more than one cleaned file, combine them
    #     into a single DataFrame.
    #   - If there is only one cleaned file, return it unchanged.
    #
    # This keeps the workflow flexible for both single-file and
    # multi-file uploads.
    # ---------------------------------------------------------
    if len(cleaned_files) == 1:
        st.info(
            "Only one cleaned file detected. "
            "The compile step will simply return that file unchanged."
        )
    else:
        st.info(
            f"{len(cleaned_files)} cleaned files detected. "
            "These will be combined into a single compiled dataset."
        )

    # ---------------------------------------------------------
    # Run the compile step
    #
    # processing.compile_files() handles:
    #   - concatenating multiple DataFrames
    #   - sorting by timestamp (if available)
    #
    # The result is stored in session_state so the next step
    # (downloading) can access it.
    # ---------------------------------------------------------
    if st.button("Compile Files", key="dg_compile"):
        df = processing.compile_files(cleaned_files)
        st.session_state.compiled = df

        st.success("Files compiled successfully.")
        advance_step()



# ---------------------------------------------------------
# Step 7 — Download Outputs
# ---------------------------------------------------------
def step_7_download():
    st.markdown("#### 7. Download Cleaned & Compiled Data")

    active = (st.session_state.step == 7)

    # ---------------------------------------------------------
    # COMPLETED STEP (user already reached the download screen)
    # ---------------------------------------------------------
    if not active:
        if st.session_state.compiled is not None:
            st.success("Download ready.")
        else:
            st.info("Waiting to generate download…")
        return

    # ---------------------------------------------------------
    # ACTIVE STEP (user is downloading the final dataset now)
    # ---------------------------------------------------------

    df = st.session_state.compiled

    # If no compiled dataset exists, the user may have skipped a step
    if df is None:
        st.warning("No compiled dataset available.")
        return

    # ---------------------------------------------------------
    # Convert the compiled DataFrame into a CSV file
    #
    # df.to_csv() turns the DataFrame into a CSV-formatted string.
    # .encode("utf-8") converts that string into bytes, which is the
    # format Streamlit needs for downloading.
    # ---------------------------------------------------------
    csv = df.to_csv(index=False).encode("utf-8")

    # ---------------------------------------------------------
    # Display a styled message box to celebrate completion
    #
    # This uses a small block of HTML/CSS to make the final step feel
    # polished and friendly. Streamlit allows this when we set
    # unsafe_allow_html=True.
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
            <div class="final-download-title">🎉 Your workflow is complete - download your final dataset</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # Provide the download button
    #
    # st.download_button() lets the user download a file directly
    # from the browser. We pass:
    #   - the CSV bytes
    #   - a filename
    #   - the MIME type ("text/csv")
    #
    # When the user clicks the button, the file is saved to their computer.
    # ---------------------------------------------------------
    st.download_button(
        label="⬇️ Download Compiled CSV",
        data=csv,
        file_name="weather_station_compiled.csv",
        mime="text/csv",
        key="dg_download"
    )

