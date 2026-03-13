import streamlit as st
import pandas as pd


def show_summary(summary, renderer=None, title="Task Summary", filename=None):
    """
    Display a task summary using the renderer provided by the Task object.

    - renderer: a function that knows how to render this task's summary
    - summary: the summary dictionary returned by the task
    - filename: the file the task was applied to
    """

    if not summary:
        return

    label = f"{title}" if filename is None else f"{title} - {filename}"

    with st.expander(label, expanded=False):

        # ---------------------------------------------------------
        # ERROR HANDLING (always shown first)
        # ---------------------------------------------------------
        if "errors" in summary:
            st.markdown("##### ❌ Errors")

            for err in summary["errors"]:

                # Case 1: error is a dict
                if isinstance(err, dict):
                    etype = err.get("error_type", "Error")
                    msg = err.get("message", "")
                    details = err.get("details")

                # Case 2: error is a plain string
                else:
                    etype = "Error"
                    msg = str(err)
                    details = None

                st.error(f"**{etype}**: {msg}")

                if details:
                    with st.expander("Details"):
                        st.write(details)

            return  # stop after showing errors

        # ---------------------------------------------------------
        # TASK-SPECIFIC SUMMARY RENDERING
        # ---------------------------------------------------------
        if renderer:
            try:
                renderer(summary, filename)
                return
            except Exception as e:
                st.error(f"Summary renderer failed: {e}")

        # ---------------------------------------------------------
        # FALLBACK: raw summary
        # ---------------------------------------------------------
        st.warning("No summary renderer provided for this task.")
        st.json(summary)
