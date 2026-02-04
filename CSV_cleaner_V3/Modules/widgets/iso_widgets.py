import streamlit as st
import pandas as pd

def iso_widgets(df):
    st.markdown("##### Choose the date-time column")

    cols = df.columns.tolist()
    col1, col2 = st.columns(2)

    date_time_col = col1.selectbox(
        "Column",
        options=cols,
        index=None,
        key="iso_col_select"
    )

    # Ambiguous date handling options
    st.markdown(" ")
    st.markdown("##### How should ambiguous dates be handled?")
    ambiguous_mode = st.radio(
        "If a date can be interpreted in more than one valid way:",
        [
            "Flag ambiguous rows only",
            "Assume month-first (MM/DD/YYYY)",
            "Assume day-first (DD/MM/YYYY)"
        ],
        key="iso_ambiguous_mode"
    )

    # Preview ambiguous/unparsed rows BEFORE conversion
    if date_time_col:
        st.markdown(" ")
        st.markdown("##### Preview of ambiguous or unparsed rows")

        preview_df = df[[date_time_col]].copy()
        preview_df["value"] = preview_df[date_time_col].astype(str)

        ambiguous_rows = []
        unparsed_rows = []

        for idx, value in preview_df["value"].items():
            try:
                d1 = pd.to_datetime(value, errors="coerce", dayfirst=True)
                d2 = pd.to_datetime(value, errors="coerce", dayfirst=False)
            except Exception:
                unparsed_rows.append((idx, value))
                continue

            if pd.isna(d1) and pd.isna(d2):
                unparsed_rows.append((idx, value))
            elif not pd.isna(d1) and not pd.isna(d2) and d1 != d2:
                ambiguous_rows.append((idx, value))

        if ambiguous_rows:
            st.warning(f"{len(ambiguous_rows)} ambiguous rows detected.")
            st.dataframe(
                pd.DataFrame(ambiguous_rows, columns=["Row", "Value"]),
                use_container_width=True
            )
        else:
            st.info("No ambiguous rows detected.")

        if unparsed_rows:
            st.error(f"{len(unparsed_rows)} unparsed rows detected.")
            st.dataframe(
                pd.DataFrame(unparsed_rows, columns=["Row", "Value"]),
                use_container_width=True
            )
        else:
            st.info("No unparsed rows detected.")

    # One-shot trigger
    if st.button("Next", type="primary", key="iso_next"):
        st.session_state.iso_trigger = True

    triggered = st.session_state.get("iso_trigger", False)
    st.session_state.iso_trigger = False

    if triggered:

        if not date_time_col:
            st.error("Please select a date-time column.", icon="🚨")
            return None

        return {
            "date_time_col": date_time_col,
            "ambiguous_mode": ambiguous_mode
        }

    return None