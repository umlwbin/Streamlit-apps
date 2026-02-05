import streamlit as st


# ---------------------------------------------------------
# Initialize workflow state
# ---------------------------------------------------------

def init_state():
    """
    Initializes all workflow state variables.
    Should be called once at the start of the workflow.
    """

    defaults = {
        "step": 1,
        "files_raw": [],
        "files_cleaned": [],
        "compiled": None,

        # Workflow options
        "remove_metadata": True,
        "wind_units_choice": None,   # old variable (can remove later)
        "wind_raw_units": "km/h (recommended)",   # NEW default
        "wind_convert_choice": "No (keep original units)",   # NEW default
        "wind_settings_done": False,
        "raw_preview_done": False,
    }


    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------
# Step navigation helpers
# ---------------------------------------------------------

def advance_step():
    """Move to the next workflow step."""
    st.session_state.step += 1


def go_to_step(n: int):
    """Jump to a specific workflow step."""
    st.session_state.step = n


def reset_workflow():
    """Reset the entire workflow to its initial state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()
