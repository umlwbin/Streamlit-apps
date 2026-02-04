import streamlit as st

import streamlit as st

# ---------------------------------------------------------
# STATE INITIALIZATION
# ---------------------------------------------------------

def init_castaway_state():
    """
    Initialize all state variables used in the Castaway workflow.

    This function is called once at the start of the app.
    It ensures that every step has the data it needs and that
    the workflow always starts in a clean, predictable state.
    """
    defaults = {
        "castaway_step": 1,                 # Current step in the workflow
        "castaway_files": None,             # Uploaded files
        "castaway_metadata": None,          # Extracted metadata tables
        "castaway_data": None,              # Extracted data tables
        "castaway_selected_vars": None,     # Metadata variables chosen by the curator
        "castaway_normalization": None,     # Naming convention choice
        "castaway_new_vars": None,          # User‑added variables
        "castaway_omit_vars": None,         # Columns to remove
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------
# STEP NAVIGATION HELPERS
# ---------------------------------------------------------

def go_to_step(n: int):
    """
    Jump directly to a specific step.

    This is used when the curator clicks:
    - “Change Uploads”
    - “Re-extract”
    - “Change Metadata Selection”
    - etc.

    It allows the workflow to be fully reversible.
    """
    st.session_state.castaway_step = n


def advance_step():
    """
    Move forward to the next step in the workflow.

    This is called when the curator clicks “Next”.
    """
    st.session_state.castaway_step += 1


# ---------------------------------------------------------
# FULL WORKFLOW RESET
# ---------------------------------------------------------

def reset_castaway_workflow():
    """
    Reset the entire workflow back to Step 1.

    This is used when the curator clicks “Start Over” at the end.
    It clears all stored data so the workflow behaves exactly
    like a fresh launch.
    """
    keys_to_reset = [
        "castaway_step",
        "castaway_files",
        "castaway_metadata",
        "castaway_data",
        "castaway_selected_vars",
        "castaway_normalization",
        "castaway_new_vars",
        "castaway_omit_vars",
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    # Reinitialize clean defaults
    init_castaway_state()
