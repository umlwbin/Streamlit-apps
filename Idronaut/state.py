import streamlit as st


# ---------------------------------------------------------
# Default state values
# ---------------------------------------------------------
# This dictionary defines every piece of information the Idronaut
# workflow needs to remember while the user moves through the steps.
#
# Streamlit's session_state acts like a small in‑memory database.
# Each key below stores part of the workflow's "memory":
#
# - Which step the user is on
# - Which file is being processed
# - Per‑file downcast selections
# - Per‑file metadata
# - Cleaned outputs
# - The currently loaded DataFrame
#
# These values persist across button clicks and page reruns.
DEFAULT_IDRONAUT_STATE = {
    "idronaut_step": 1,                 # Current workflow step (1–6)
    "idronaut_files": [],               # Uploaded files from Step 1
    "idronaut_current_file_index": 0,   # Index of the file being processed
    "idronaut_downcast_ranges": {},     # Per‑file downcast selections
    "idronaut_latlon_site": {},         # Per‑file metadata (lat/lon/site)
    "idronaut_cleaned_frames": [],      # List of cleaned DataFrames
    "current_df": None,                 # The DataFrame for the active file
}


# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------
def init_idronaut_state():
    """
    Ensure all Idronaut workflow state variables exist.

    This function is called once at the start of the workflow (in app.py).
    It sets up the initial "memory" of the workflow.

    Why this matters:
      - Streamlit reruns the script on every interaction
      - session_state keeps values persistent between reruns
      - Without initialization, the workflow would lose its place

    This function only sets defaults for keys that do not already exist,
    so it never overwrites user progress.
    """
    for key, value in DEFAULT_IDRONAUT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------
# Step navigation
# ---------------------------------------------------------
def go_to_step(step_number: int):
    """
    Jump directly to a specific workflow step.

    This is how the workflow moves from:
      Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6

    The widgets file calls this function whenever the user clicks "Next"
    or chooses to revisit a previous step.
    """
    st.session_state.idronaut_step = step_number


def advance_step():
    """
    Move to the next workflow step.

    This is a convenience helper used when the workflow always moves
    forward by exactly one step.
    """
    st.session_state.idronaut_step += 1


# ---------------------------------------------------------
# Reset helpers
# ---------------------------------------------------------
def reset_for_next_file():
    """
    Reset per‑file UI state while preserving cleaned outputs.

    The Idronaut workflow processes each file independently.
    After finishing one file, we must clear temporary values so the
    next file starts fresh.

    This function resets:
      - Downcast selection for the current file
      - Metadata for the current file
      - The loaded DataFrame
      - The workflow step (back to Step 2)

    It does NOT reset:
      - Uploaded files
      - Cleaned outputs
      - Progress on previous files
    """

    idx = st.session_state.idronaut_current_file_index

    # Remove stored selections for the file we just finished
    st.session_state.idronaut_downcast_ranges.pop(idx, None)
    st.session_state.idronaut_latlon_site.pop(idx, None)

    # Clear the active DataFrame and return to Step 2
    st.session_state.current_df = None
    st.session_state.idronaut_step = 2  # Step 2 is the first per‑file step


def reset_idronaut_workflow():
    """
    Reset the entire workflow to its initial state.

    This is used when:
      - The user clicks "Change Uploads"
      - The user clicks "Start Over" at the end
      - A curator wants to restart the whole process

    This function clears:
      - Uploaded files
      - Per‑file selections
      - Cleaned outputs
      - Current file index
      - The active DataFrame
      - The current step

    After clearing everything, it reinitializes the default state.
    """

    # Remove all Idronaut-related keys from session_state
    for key in list(st.session_state.keys()):
        if key.startswith("idronaut_") or key == "current_df":
            del st.session_state[key]

    # Reinitialize clean state
    init_idronaut_state()
