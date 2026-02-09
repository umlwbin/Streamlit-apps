import streamlit as st
import pandas as pd


def show_summary(summary, title="Task Summary", filename=None):
    """
    Display a structured summary returned by a processing function.
    Groups related summaries into logical sections for clarity.
    """

    if not summary:
        return

    label = f"{title}" if filename is None else f"{title} - {filename}"

    with st.expander(label, expanded=False):

        # =========================================================
        # RVQ SUMMARY (handled separately)
        # =========================================================
        if summary.get("_rvq_task", False):
            _show_rvq_summary(summary)
            return

        # =========================================================
        # HEADER CLEANING (standalone or nested)
        # =========================================================
        if "changed" in summary or "header_metadata" in summary or "header_cleaning" in summary:
            with st.expander("🔤 Header Cleaning", expanded=False):
                _show_header_cleaning(summary)

        # =========================================================
        # COLUMN OPERATIONS
        # =========================================================
        if any(k in summary for k in [
            "columns_added", "removed_columns", "requested_order",
            "final_order", "duplicate_columns_found"
        ]):
            with st.expander("🧩 Column Operations", expanded=False):
                _show_column_operations(summary)

        # =========================================================
        # DATE & TIME OPERATIONS
        # =========================================================
        if any(k in summary for k in [
            "merged_rows", "converted_rows", "parsed_rows",
            "unparsed_dates", "unparsed_times", "ambiguous_rows",
            "new_column", "new_columns"
        ]):
            with st.expander("⏱️ Date & Time Operations", expanded=False):
                _show_datetime_operations(summary)

        # =========================================================
        # RESHAPE / MERGE OPERATIONS
        # =========================================================
        if any(k in summary for k in [
            "operation", "merged_files", "added_source_column"
        ]):
            with st.expander("🔁 Reshape / Merge Operations", expanded=False):
                _show_reshape_operations(summary)

        # =========================================================
        # DATA TYPE ASSIGNMENT
        # =========================================================
        if any(k in summary for k in ["converted", "failed", "skipped"]):
            with st.expander("🔢 Data Type Assignment", expanded=False):
                _show_dtype_assignment(summary)

        # =========================================================
        # TIDY DATA STRUCTURAL CHECKS
        # =========================================================
        if any(k in summary for k in [
            "empty_columns_removed", "empty_rows_removed",
            "nans_replaced", "whitespace_trimmed",
            "mixed_type_columns", "header_rows_detected"
        ]):
            with st.expander("🧹 Tidy Data Structural Checks", expanded=False):
                _show_tidy_checks(summary)


# =========================================================
# SECTION HELPERS
# =========================================================

def _show_rvq_summary(summary):
    st.success("🧪 RVQ Summary")

    rows = []
    for variable, rvqs in summary.items():
        if variable in ("_rvq_task", "detection_limits"):
            continue
        if isinstance(rvqs, dict):
            for rvq_code, count in rvqs.items():
                rows.append({
                    "Variable": variable,
                    "RVQ Code": rvq_code,
                    "Count": count
                })

    if rows:
        rvq_df = pd.DataFrame(rows).sort_values(["Variable", "RVQ Code"])
        st.dataframe(rvq_df, use_container_width=True)
    else:
        st.info("No RVQs were applied.")

    if "detection_limits" in summary:
        st.success("📉 Detection Limit Breakdown")
        det_rows = []
        for variable, rvq_dict in summary["detection_limits"].items():
            for rvq_code, limits in rvq_dict.items():
                for limit, count in limits.items():
                    det_rows.append({
                        "Variable": variable,
                        "RVQ Code": rvq_code,
                        "Detection Limit": limit,
                        "Count": count
                    })
        if det_rows:
            det_df = pd.DataFrame(det_rows).sort_values(
                ["Variable", "RVQ Code", "Detection Limit"]
            )
            st.dataframe(det_df, use_container_width=True)
        else:
            st.info("No detection limits extracted.")

    st.markdown("---")
    st.caption("End of summary")


def _show_header_cleaning(summary):
    # Standalone header cleaning
    if "changed" in summary:
        changed = summary.get("changed", {})
        unchanged = summary.get("unchanged", [])

        if changed:
            st.write("**Renamed columns:**")
            for old, new in changed.items():
                st.write(f"• {old} → {new}")
        else:
            st.info("No column names were changed.")

        if unchanged:
            st.write("**Unchanged columns:**")
            st.write(", ".join(unchanged))

    # Nested header cleaning (Tidy Data)
    if "header_cleaning" in summary:
        hc = summary["header_cleaning"]
        changed = hc.get("changed", {})
        unchanged = hc.get("unchanged", [])

        if changed:
            st.write("**Renamed columns:**")
            for old, new in changed.items():
                st.write(f"• {old} → {new}")
        if unchanged:
            st.write("**Unchanged columns:**")
            st.write(", ".join(unchanged))

        if "header_metadata" in hc:
            _show_header_metadata(hc["header_metadata"])

    # Standalone metadata
    if "header_metadata" in summary:
        _show_header_metadata(summary["header_metadata"])


def _show_header_metadata(meta):
    # Only treat these fields as "real" metadata
    meaningful_fields = [
        "units",
        "sensor_model",
        "media",
        "calibration_settings",
        "processing_notes"
    ]

    # Determine if any metadata fields contain meaningful content
    has_real_metadata = any(
        any(details.get(field) for field in meaningful_fields)
        for details in meta.values()
    )

    if not has_real_metadata:
        # No meaningful metadata → skip table entirely
        return

    st.success("📘 Extracted Header Metadata")

    rows = []
    for original, details in meta.items():
        rows.append({
            "Original Header": original,
            "Variable": details.get("variable"),  # still shown, but not used for filtering
            "Units": details.get("units"),
            "Media":details.get("media"),
            "Sensor Model": details.get("sensor_model"),
            "Calibration Settings": details.get("calibration_settings"),
            "Processing Notes": details.get("processing_notes"),
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def _show_column_operations(summary):
    if "columns_added" in summary:
        added = summary["columns_added"]
        st.success("🧩 Columns Added")
        st.write(", ".join(added) if added else "No columns added.")

    if "removed_columns" in summary:
        removed = summary["removed_columns"]
        st.success("🗑️ Columns Removed")
        st.write(", ".join(removed) if removed else "No columns removed.")

    if "requested_order" in summary:
        st.success("🔃 Column Order Updated")
        st.write("**Requested:** " + ", ".join(summary["requested_order"]))
        st.write("**Final:** " + ", ".join(summary["final_order"]))

    if "duplicate_columns_found" in summary:
        dups = summary["duplicate_columns_found"]
        if dups:
            st.warning(f"⚠️ Duplicate column names fixed: {dups}")


def _show_datetime_operations(summary):
    if "merged_rows" in summary:
        st.success("⏱️ Date + Time Columns Merged")
        st.write(f"Merged rows: {summary['merged_rows']}")

    if "converted_rows" in summary:
        st.success("📅 ISO 8601 Conversion")
        st.write(f"Converted rows: {summary['converted_rows']}")

    if "parsed_rows" in summary:
        st.success("📆 Date Parsing")
        st.write(f"Parsed rows: {summary['parsed_rows']}")

    for key in ["unparsed_dates", "unparsed_times", "ambiguous_rows", "unparsed_rows"]:
        if key in summary and summary[key]:
            st.error(f"❌ {key.replace('_', ' ').title()}: {len(summary[key])}")
            st.dataframe(pd.DataFrame(summary[key], columns=["Row", "Value"]))


def _show_reshape_operations(summary):
    if "operation" in summary:
        op = summary["operation"]
        st.success(f"🔁 Operation: {op}")

    if "merged_files" in summary:
        files = summary["merged_files"]
        st.write(f"Files merged: {len(files)}")
        with st.expander("View merged file list"):
            for f in files:
                st.write(f"• {f}")

    if "added_source_column" in summary:
        if summary["added_source_column"]:
            st.info("🧩 Source filename column added.")


def _show_dtype_assignment(summary):
    if "converted" in summary:
        converted = summary["converted"]
        if converted:
            st.success("🔢 Converted Columns")
            st.dataframe(pd.DataFrame(converted, columns=["Column", "Assigned Type"]))

    if "failed" in summary and summary["failed"]:
        st.error("❌ Failed Conversions")
        fail_df = pd.DataFrame(
            [(col, err) for col, err in summary["failed"].items()],
            columns=["Column", "Error"]
        )
        st.dataframe(fail_df)

    if "skipped" in summary and summary["skipped"]:
        st.warning("⚠️ Skipped Columns")
        st.write(", ".join(summary["skipped"]))


def _show_tidy_checks(summary):
    if "empty_columns_removed" in summary:
        removed = summary["empty_columns_removed"]
        st.info(f"🗑️ Empty columns removed: {removed or 'None'}")

    if "empty_rows_removed" in summary:
        st.info(f"🧹 Empty rows removed: {summary['empty_rows_removed']}")

    if "nans_replaced" in summary:
        st.info(f"🔄 NaN-like values standardized: {summary['nans_replaced']}")

    if "whitespace_trimmed" in summary:
        st.info("✂️ Whitespace trimmed.")

    if "mixed_type_columns" in summary and summary["mixed_type_columns"]:
        st.warning("⚠️ Mixed data types detected:")
        st.json(summary["mixed_type_columns"])

    if "header_rows_detected" in summary and summary["header_rows_detected"]:
        st.warning(f"⚠️ Header-like rows detected: {summary['header_rows_detected']}")
