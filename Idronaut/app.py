import streamlit as st

# Import the UI steps that make up the workflow.
# Each of these functions is responsible for:
#   - Checking whether it is the active step
#   - Rendering its UI if active
#   - Showing a summary if not active
#   - Moving the workflow forward when the user clicks "Next"
#
# app.py does NOT contain UI logic — it simply calls these steps in order.
from widgets import (
    idronaut_intro,
    upload_step,
    select_downcast_step,
    preview_downcast_step,
    enter_metadata_step,
    clean_file_step,
    download_step,
)

# Import the state initializer.
# This sets up all session_state variables the workflow needs.
from state import init_idronaut_state


def main():
    """
    The main orchestrator for the Idronaut CTD workflow.

    This file is intentionally simple.
    It does not clean data, manage per‑file logic, or render UI details.
    Instead, it acts as the "table of contents" for the entire workflow.

    New contributors:
      - If you're trying to understand how the workflow fits together,
        this is the best file to start with.
      - Each step function below is self‑contained and follows the same pattern.
      - app.py simply calls them in order, every time the app reruns.

    Streamlit reruns this script on every interaction (button click, input change).
    Because of that, app.py must be:
      - predictable
      - declarative
      - free of side effects
    """

    # -----------------------------------------------------
    # 1. Initialize workflow state
    # -----------------------------------------------------
    # This ensures all required session_state variables exist.
    # It only sets defaults if they are missing, so it never overwrites progress.
    init_idronaut_state()

    # -----------------------------------------------------
    # 2. Show the persistent intro section
    # -----------------------------------------------------
    # The intro is always visible at the top of the page.
    # It includes:
    #   - Workflow title
    #   - Description
    #   - "Processing file X of Y" banner
    idronaut_intro()

    # -----------------------------------------------------
    # 3. Render each workflow step
    # -----------------------------------------------------
    # Each step function internally checks:
    #   - "Am I the active step?"
    #   - If yes → show full UI
    #   - If no → show a collapsed summary
    #
    # This pattern keeps the workflow tidy and predictable.
    upload_step()
    select_downcast_step()
    preview_downcast_step()
    enter_metadata_step()
    clean_file_step()
    download_step()


# ---------------------------------------------------------
# Run the app
# ---------------------------------------------------------
# This allows the file to be run directly with:
#     streamlit run app.py
#
# When Streamlit executes the script, it calls main().
if __name__ == "__main__":
    main()