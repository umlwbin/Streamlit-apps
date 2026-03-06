import streamlit as st
import pandas as pd

def render_add_rvqs_summary(summary, summary_df=None):
    """
    Renderer for RVQ tasks.

    summary: dict of {variable: {rvq_code: count}}
    summary_df: optional long-form detection-limit table
    """

    st.success("Applied RVQ Rules")

    # Variables processed
    variables = list(summary.keys())
    if variables:
        st.write("**Variables processed:** " + ", ".join(variables))
    else:
        st.write("**Variables processed:** None")

    # RVQ counts
    st.write("### RVQ Code Summary")

    rows = []
    for var, rvqs in summary.items():
        for rvq_code, count in rvqs.items():
            rows.append({"Variable": var, "RVQ Code": rvq_code, "Count": count})

    if rows:
        df_basic = pd.DataFrame(rows).sort_values(["Variable", "RVQ Code"])
        st.dataframe(df_basic, use_container_width=True)
    else:
        st.info("No RVQs were applied.")

    # Detection limits
    st.write("### Detection Limits Extracted")

    if summary_df is not None and not summary_df.empty:
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.write("None detected")
