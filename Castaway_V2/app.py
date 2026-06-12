import streamlit as st

from widgets import (
    workflow_intro,
    upload_step,
    extract_step,
    select_metadata_step,
    normalize_variables_step,
    add_new_vars_step,
    omit_vars_step,
    download_step,
)

from state import init_castaway_state

# ---------------------------------------------------------
# Increase the size of widget labels
# ---------------------------------------------------------
st.html("""
<style>
    /* All widget labels */
    [data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
    }

    /* All markdown text */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdown"] p,
    .stMarkdown p {
        font-size: 18px !important;
    }
</style>
""")


def main():
    init_castaway_state()
    workflow_intro()
    upload_step()
    extract_step()
    select_metadata_step()
    add_new_vars_step()
    omit_vars_step()   
    normalize_variables_step()
    download_step()


if __name__ == "__main__":
    main()
