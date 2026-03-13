import streamlit as st
import pandas as pd

def render_add_rvqs_summary(summary, filename=None):
    """
    Summary renderer for the RVQ task.
    """

    st.success("Applied RVQ Rules")

    # ---------------------------------------------------------
    # Warnings
    # ---------------------------------------------------------
    warnings = summary.get("warnings")
    if warnings:
        st.write("##### Warnings")
        st.warning(warnings)

    # ---------------------------------------------------------
    # Variables processed
    # ---------------------------------------------------------
    variables = [
        var for var in summary.keys()
        if var not in ("warnings",) and isinstance(summary[var], dict)
    ]

    if variables:
        st.write("**Variables processed:** " + ", ".join(variables))
    else:
        st.write("**Variables processed:** None")

    # ---------------------------------------------------------
    # RVQ Code Summary
    # ---------------------------------------------------------
    st.write("##### RVQ Code Summary")

    rows = []
    for var in variables:
        rvqs = summary.get(var, {})
        for rvq_code, count in rvqs.items():
            rows.append({
                "Variable": var,
                "RVQ Code": rvq_code,
                "Count": count
            })

    if rows:
        df_basic = pd.DataFrame(rows).sort_values(["Variable", "RVQ Code"])
        st.dataframe(df_basic, use_container_width=True)
    else:
        st.info("No RVQs were applied.")

    # ---------------------------------------------------------
    # Detection Limits (from session_state)
    # ---------------------------------------------------------
    st.write("##### Detection Limits Extracted")

    summary_df = None
    if "supplementary_outputs" in st.session_state:
        key = f"{filename}_RVQ_summary.csv"
        summary_df = st.session_state.supplementary_outputs.get(key)

    if summary_df is not None and not summary_df.empty:
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.write("None detected")
