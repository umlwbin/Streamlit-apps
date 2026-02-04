import streamlit as st
from Modules.ui_utils import big_caption



def tidy_data_widgets():
    big_caption("These settings will be applied to all uploaded files.")

    st.markdown("##### Column Name Case Normalization")
    case_mode = st.radio(
        "Normalize column name case?",
        ["none", "lower", "upper", "title"],
        horizontal=True
    )

    st.markdown("##### NaN Check")
    st.markdown('Are there any NaN representations in your file(s) that are not in the following list?')
    st.markdown('**NA**, **?**, **N/A**, **" "**, **np.nan**, **None**, **Nan**, **NaN**')
    st.markdown('If yes, enter additional NaN representation(s) below (comma‑separated):')

    nan_tokens = st.text_input("")

    nans = [t.strip() for t in nan_tokens.split(",") if t.strip()]

    if st.button("Continue", type="primary", key="cleanupContinue"):
        return {
            "nans": nans,
            "case_mode": case_mode
        }