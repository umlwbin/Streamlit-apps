import streamlit as st

# Always use relative imports inside the app package
from state import init_state
from widgets import (
    workflow_intro,
    step_1_upload_files,
    step_2_preview_raw,
    step_3_wind_units,
    step_4_clean_files,
    step_5_preview_cleaned,
    step_6_compile,
    step_7_download,
)


def main():
    init_state()
    workflow_intro()

    # Render each step
    step_1_upload_files()
    step_2_preview_raw()
    step_3_wind_units()
    step_4_clean_files()
    step_5_preview_cleaned()

    step_6_compile()
    step_7_download()



if __name__ == "__main__":
    main()
