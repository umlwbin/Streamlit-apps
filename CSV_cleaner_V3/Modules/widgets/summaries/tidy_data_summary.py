import streamlit as st
import pandas as pd

def render_tidy_data_summary(summary, filename=None):
    """
    Summary renderer for the 'tidy_data' task.

    The summary is a merged dictionary containing:
        - empty column/row removal
        - NaN standardization
        - whitespace trimming
        - duplicate column detection/fixing
        - mixed-type detection
        - header-row detection
        - scientific header cleaning summary
        - warnings (soft validation)
    """

    st.success("Tidy Data Cleaning Pipeline")

    # ---------------------------------------------------------
    # Warnings
    # ---------------------------------------------------------
    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    # ---------------------------------------------------------
    # Empty columns removed
    # ---------------------------------------------------------
    empty_cols = summary.get("empty_columns_removed", [])
    if empty_cols:
        st.write("**Empty columns removed:** " + ", ".join(empty_cols))
    else:
        st.write("**Empty columns removed:** None")

    # ---------------------------------------------------------
    # Empty rows removed
    # ---------------------------------------------------------
    empty_rows = summary.get("empty_rows_removed", 0)
    st.write(f"**Empty rows removed:** {empty_rows}")

    # ---------------------------------------------------------
    # NaN standardization
    # ---------------------------------------------------------
    nan_count = summary.get("nans_replaced", 0)
    st.write(f"**NaN-like values standardized:** {nan_count}")

    # ---------------------------------------------------------
    # Whitespace trimming
    # ---------------------------------------------------------
    if summary.get("whitespace_trimmed"):
        st.write("**Whitespace trimmed:** Yes")

    # ---------------------------------------------------------
    # Duplicate column handling
    # ---------------------------------------------------------
    duplicates = summary.get("duplicate_columns_found", [])
    if duplicates:
        st.warning("Duplicate column names detected: " + ", ".join(duplicates))

    if summary.get("duplicate_columns_fixed"):
        new_cols = summary.get("new_column_names", [])
        st.write("### Duplicate Columns Fixed")
        df_new = pd.DataFrame({"Column Names": new_cols})
        st.dataframe(df_new, use_container_width=True)

    # ---------------------------------------------------------
    # Mixed-type detection
    # ---------------------------------------------------------
    mixed = summary.get("mixed_type_columns", {})
    mixed_count = summary.get("mixed_type_count", 0)

    if mixed_count > 0:
        st.warning(f"Columns with mixed data types: {mixed_count}")
        df_mixed = pd.DataFrame(
            [{"Column": col, "Types": str(types)} for col, types in mixed.items()]
        )
        st.dataframe(df_mixed, use_container_width=True)
    else:
        st.write("**Mixed-type columns detected:** None")

    # ---------------------------------------------------------
    # Header-like row detection
    # ---------------------------------------------------------
    header_rows = summary.get("header_rows_detected", [])
    if header_rows:
        st.warning("Header-like rows detected at indices: " + ", ".join(map(str, header_rows)))
    else:
        st.write("**Header-like rows detected:** None")

    # ---------------------------------------------------------
    # Scientific header cleaning summary
    # ---------------------------------------------------------
    if "header_metadata" in summary:
        st.write("### Cleaned Headers")

        changed = summary.get("changed", {})
        unchanged = summary.get("unchanged", [])

        # Renamed columns
        if changed:
            st.write("**Renamed columns:**")
            df_changed = pd.DataFrame(
                [(old, new) for old, new in changed.items()],
                columns=["Original", "Cleaned"]
            )
            st.dataframe(df_changed, use_container_width=True)

        # Unchanged columns
        if unchanged:
            st.write("**Unchanged columns:** " + ", ".join(unchanged))

        # Metadata table
        metadata = summary.get("header_metadata", {})
        if metadata:
            rows = []
            for original, meta in metadata.items():
                rows.append({
                    "Original Header": original,
                    "Variable": meta.get("variable"),
                    "Units": meta.get("units"),
                    "Additional Notes": meta.get("additional_notes"),
                    "Cleaned Header": meta.get("cleaned_header"),
                })
            df_meta = pd.DataFrame(rows)
            st.write("**Extracted header metadata:**")
            st.dataframe(df_meta, use_container_width=True)
