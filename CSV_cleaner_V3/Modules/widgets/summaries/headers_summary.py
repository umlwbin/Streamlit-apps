import streamlit as st
import pandas as pd

def render_clean_headers_summary(summary):
    """
    Summary renderer for the 'clean_headers' task.

    Expected summary keys:
        - task_name: "clean_headers"
        - changed: {original: cleaned}
        - unchanged: [original, ...]
        - header_metadata: {
              original: {
                  "variable": ...,
                  "units": ...,
                  "additional_notes": ...,
                  "cleaned_header": ...
              }
          }
    """

    st.success("Header Cleaning")

    # ---------------------------------------------------------
    # Renamed columns
    # ---------------------------------------------------------
    changed = summary.get("changed", {})
    if changed:
        st.write("**Renamed columns:**")
        df_changed = pd.DataFrame(
            [(old, new) for old, new in changed.items()],
            columns=["Original", "Cleaned"]
        )
        st.dataframe(df_changed, use_container_width=True)
    else:
        st.info("No column names were changed.")

    # ---------------------------------------------------------
    # Unchanged columns
    # ---------------------------------------------------------
    unchanged = summary.get("unchanged", [])
    if unchanged:
        st.write("**Unchanged columns:**")
        st.write(", ".join(unchanged))

    # ---------------------------------------------------------
    # Metadata table
    # ---------------------------------------------------------
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

        # Only show if at least one row has meaningful metadata
        if not df_meta.drop(columns=["Original Header", "Cleaned Header"]).isna().all().all():
            st.write("**Extracted Metadata:**")
            st.dataframe(df_meta, use_container_width=True)
