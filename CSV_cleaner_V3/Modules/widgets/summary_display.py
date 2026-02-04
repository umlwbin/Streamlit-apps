import streamlit as st
import pandas as pd


def show_summary(summary, title="Task Summary", filename=None):
    """
    Display a structured summary returned by a processing function.
    Cleanly separates RVQ summaries from all other task summaries.
    Hides the expander entirely if no summary exists.
    """

    # ---------------------------------------------------------
    # If no summary, show nothing
    # ---------------------------------------------------------
    if not summary:
        return

    label = f"{title}" if filename is None else f"{title} — {filename}"

    with st.expander(label, expanded=False):

        # ---------------------------------------------------------
        # Detect RVQ task
        # ---------------------------------------------------------
        is_rvq = summary.get("_rvq_task", False)

        # ---------------------------------------------------------
        # RVQ SUMMARY BRANCH
        # ---------------------------------------------------------
        if is_rvq:

            # -----------------------------
            # High-level RVQ Summary
            # -----------------------------
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
                st.info("No RVQs were applied to the selected variables.")

            # -----------------------------
            # Detection Limit Breakdown
            # -----------------------------
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
                    st.info("No detection limits were extracted.")

            st.markdown("---")
            st.caption("End of summary")
            return  # RVQ summary complete — exit early

        # ---------------------------------------------------------
        # GENERAL SUMMARY BRANCH (non-RVQ tasks)
        # ---------------------------------------------------------

        # ---------------------------------------------------------
        # ADD COLUMNS SUMMARY
        # ---------------------------------------------------------
        if "columns_added" in summary:
            st.success("🧩 Columns Added")
            added = summary["columns_added"]

            if isinstance(added, (list, tuple)):
                if len(added) > 0:
                    st.write(", ".join(str(a) for a in added))
                else:
                    st.info("No columns were added.")
            else:
                st.write(str(added))


        # ---------------------------------------------------------
        # REORDER COLUMNS SUMMARY
        # ---------------------------------------------------------
        if "requested_order" in summary and "final_order" in summary:

            st.success("🔃 Column Order Updated")

            req = summary.get("requested_order", [])
            final = summary.get("final_order", [])
            missing = summary.get("missing_columns", [])
            changed = summary.get("changed", False)

            st.write("**Requested order:**")
            st.write(", ".join(str(c) for c in req))

            st.write("**Final order applied:**")
            st.write(", ".join(str(c) for c in final))

            if missing:
                st.warning(f"Missing columns (not found in file): {', '.join(missing)}")

            if not changed:
                st.info("Column order was already correct.")


        # ---------------------------------------------------------
        # REMOVE COLUMNS SUMMARY
        # ---------------------------------------------------------
        if "removed_columns" in summary:

            st.success("🗑️ Columns Removed")

            removed = summary.get("removed_columns", [])
            remaining = summary.get("remaining_columns", [])
            removed_count = summary.get("removed_count", 0)
            remaining_count = summary.get("remaining_count", 0)

            if removed:
                st.write(f"**Removed ({removed_count}):** " + ", ".join(str(c) for c in removed))
            else:
                st.info("No columns were removed.")

            st.write(f"**Remaining ({remaining_count}):** " + ", ".join(str(c) for c in remaining))


        # ---------------------------------------------------------
        # CLEAN HEADERS SUMMARY
        # ---------------------------------------------------------
        if "changed" in summary:

            st.success("🔤 Header Names Cleaned")

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
                st.write(", ".join(str(c) for c in unchanged))


        # ---------------------------------------------------------
        # RENAME COLUMNS SUMMARY
        # ---------------------------------------------------------
        if "renamed" in summary:

            if not summary["renamed"]:
                st.warning("⚠️ Column renaming was skipped due to a mismatch in column count.")
                st.markdown("---")
            else:
                st.success("✏️ Columns Renamed")

                old = summary.get("old_names", [])
                new = summary.get("new_names", [])
                changed_count = summary.get("changed_count", 0)

                if changed_count == 0:
                    st.info("No column names were changed.")
                else:
                    st.write(f"**Columns changed ({changed_count}):**")
                    for o, n in zip(old, new):
                        if o != n:
                            st.write(f"• **{o}** → **{n}**")

        # ---------------------------------------------------------
        # MERGE DATE + TIME SUMMARY
        # ---------------------------------------------------------
        if "merged_rows" in summary and "new_column" in summary:

            st.success("⏱️ Date + Time Columns Merged")

            merged = summary.get("merged_rows", 0)
            new_col = summary.get("new_column", "Date_Time")

            st.write(f"**New column created:** {new_col}")
            st.write(f"**Successfully merged rows:** {merged}")

            # Unparsed dates
            unparsed_dates = summary.get("unparsed_dates", [])
            if unparsed_dates:
                st.error(f"❌ Unparsed dates: {len(unparsed_dates)}")
                st.dataframe(
                    pd.DataFrame(unparsed_dates, columns=["Row", "Value"]),
                    use_container_width=True
                )

            # Unparsed times
            unparsed_times = summary.get("unparsed_times", [])
            if unparsed_times:
                st.error(f"❌ Unparsed times: {len(unparsed_times)}")
                st.dataframe(
                    pd.DataFrame(unparsed_times, columns=["Row", "Value"]),
                    use_container_width=True
                )


        # ---------------------------------------------------------
        # ISO DATETIME CONVERSION SUMMARY
        # ---------------------------------------------------------
        if "converted_rows" in summary and "new_column" in summary:

            st.success("📅 ISO 8601 Conversion Complete")

            new_col = summary.get("new_column", "")
            converted = summary.get("converted_rows", 0)
            ambiguous_mode = summary.get("ambiguous_mode", "")

            st.write(f"**New column created:** {new_col}")
            st.write(f"**Successfully converted rows:** {converted}")
            st.write(f"**Ambiguity handling mode:** {ambiguous_mode}")

            # Ambiguous rows
            ambiguous = summary.get("ambiguous_rows", [])
            if ambiguous:
                st.warning(f"⚠️ Ambiguous date values: {len(ambiguous)}")
                st.dataframe(
                    pd.DataFrame(ambiguous, columns=["Row", "Value"]),
                    use_container_width=True
                )

            # Unparsed rows
            unparsed = summary.get("unparsed_rows", [])
            if unparsed:
                st.error(f"❌ Unparsed values: {len(unparsed)}")
                st.dataframe(
                    pd.DataFrame(unparsed, columns=["Row", "Value"]),
                    use_container_width=True
                )


        # ---------------------------------------------------------
        # PARSE DATES SUMMARY
        # ---------------------------------------------------------
        if "parsed_rows" in summary and "new_columns" in summary:

            st.success("📆 Date Parsing Complete")

            parsed = summary.get("parsed_rows", 0)
            new_cols = summary.get("new_columns", [])

            st.write(f"**Successfully parsed rows:** {parsed}")
            st.write(f"**New columns created:** {', '.join(new_cols)}")

            # Unparsed rows
            unparsed = summary.get("unparsed_rows", [])
            if unparsed:
                st.error(f"❌ Unparsed date/time values: {len(unparsed)}")
                st.dataframe(
                    pd.DataFrame(unparsed, columns=["Row", "Value"]),
                    use_container_width=True
                )


        # ---------------------------------------------------------
        # PROVINCIAL PIVOT SUMMARY
        # ---------------------------------------------------------
        if "variables_processed" in summary and "variable_names" in summary:

            st.success("🧪 Provincial Chemistry Pivot Complete")

            count = summary.get("variables_processed", 0)
            names = summary.get("variable_names", [])
            metadata = summary.get("metadata_used", [])
            details = summary.get("details", [])

            st.write(f"**Variables processed:** {count}")
            st.write("**Variable names:** " + ", ".join(str(v) for v in names))

            if metadata:
                st.write("**Metadata merged into headers:** " + ", ".join(metadata))
            else:
                st.write("**Metadata merged into headers:** None")

            # Detailed breakdown
            if details:
                st.markdown("#### Variable Details")
                det_df = pd.DataFrame(details)
                st.dataframe(det_df, use_container_width=True)

        # ---------------------------------------------------------
        # MERGE HEADER ROWS SUMMARY
        # ---------------------------------------------------------
        if "vmv_row_used" in summary or "unit_row_used" in summary:

            st.success("🧩 Header Rows Merged")

            vmv = summary.get("vmv_row_used", None)
            unit = summary.get("unit_row_used", None)
            new_headers = summary.get("new_headers", [])

            if vmv is not None:
                st.write(f"**VMV row merged:** {vmv}")
            else:
                st.write("**VMV row merged:** None")

            if unit is not None:
                st.write(f"**Unit row merged:** {unit}")
            else:
                st.write("**Unit row merged:** None")

            # Show new headers
            if new_headers:
                st.markdown("**New header names:**")
                st.write(", ".join(str(h) for h in new_headers))



        # ---------------------------------------------------------
        # ASSIGN DATATYPE SUMMARY
        # ---------------------------------------------------------
        if "converted" in summary or "failed" in summary or "skipped" in summary:

            st.success("🔢 Data Type Assignment")

            # Converted columns
            converted = summary.get("converted", [])
            if converted:
                st.write("**Converted Columns:**")
                conv_df = pd.DataFrame(converted, columns=["Column", "Assigned Type"])
                st.dataframe(conv_df, use_container_width=True)
            else:
                st.info("No columns were converted.")

            # Failed conversions
            failed = summary.get("failed", {})
            if failed:
                st.error("❌ Failed Conversions")
                fail_df = pd.DataFrame(
                    [(col, err) for col, err in failed.items()],
                    columns=["Column", "Error"]
                )
                st.dataframe(fail_df, use_container_width=True)

            # Skipped columns
            skipped = summary.get("skipped", [])
            if skipped:
                st.warning("⚠️ Skipped Columns")
                st.write(", ".join(skipped))


        # ---------------------------------------------------------
        # High-level merge/reshape/etc.
        if "merged_rows" in summary:
            st.success(f"✅ Merged rows: **{summary['merged_rows']}**")

        if "converted_rows" in summary:
            st.success(f"✅ Successfully converted rows: **{summary['converted_rows']}**")

        if "new_column" in summary:
            st.info(f"🆕 New column created: **{summary['new_column']}**")

        if "ambiguous_mode" in summary:
            st.info(f"⚙️ Ambiguous date handling: **{summary['ambiguous_mode']}**")

        if "merged_files" in summary:
            st.success(f"📎 Files merged: **{len(summary['merged_files'])}**")
            with st.expander("View merged file list", expanded=False):
                for f in summary["merged_files"]:
                    st.write(f"• {f}")

        if "added_source_column" in summary:
            if summary["added_source_column"]:
                st.info("🧩 Source filename column added to merged output")
            else:
                st.info("ℹ️ Source filename column not added")

        if "operation" in summary:
            op = summary["operation"]

            if op == "transpose":
                st.success("🔁 Operation: **Transpose**")
                st.write(f"Rows: **{summary.get('rows', '?')}**, Columns: **{summary.get('columns', '?')}**")

            elif op == "wide_to_long":
                if not summary["id_cols"]:
                    st.info("No ID columns were selected — all columns were melted.")
                st.success("↘️ Operation: **Pivot wide → long**")
                st.write(f"ID columns: **{summary.get('id_cols', [])}**")
                st.write(f"Value columns: **{summary.get('value_cols', [])}**")
                st.write(f"New columns: **{summary.get('new_columns', [])}**")
                st.write(f"Rows: **{summary.get('rows', '?')}**, Columns: **{summary.get('columns', '?')}**")

            elif op == "long_to_wide":
                st.success("↗️ Operation: **Pivot long → wide**")
                st.write(f"Variable column: **{summary.get('variable_col', '')}**")
                st.write(f"Value column: **{summary.get('value_col', '')}**")
                st.write(f"ID columns: **{summary.get('id_cols', [])}**")
                st.write(f"Rows: **{summary.get('rows', '?')}**, Columns: **{summary.get('columns', '?')}**")

        # Unparsed / ambiguous values
        if "unparsed_dates" in summary and summary["unparsed_dates"]:
            st.error(f"❌ Unparsed dates: {len(summary['unparsed_dates'])}")
            st.dataframe(
                pd.DataFrame(summary["unparsed_dates"], columns=["Row", "Value"]),
                use_container_width=True
            )

        if "unparsed_times" in summary and summary["unparsed_times"]:
            st.error(f"❌ Unparsed times: {len(summary['unparsed_times'])}")
            st.dataframe(
                pd.DataFrame(summary["unparsed_times"], columns=["Row", "Value"]),
                use_container_width=True
            )

        if "ambiguous_rows" in summary and summary["ambiguous_rows"]:
            st.warning(f"⚠️ Ambiguous date values: {len(summary['ambiguous_rows'])}")
            st.dataframe(
                pd.DataFrame(summary["ambiguous_rows"], columns=["Row", "Value"]),
                use_container_width=True
            )

        if "unparsed_rows" in summary and summary["unparsed_rows"]:
            st.error(f"❌ Unparsed values: {len(summary['unparsed_rows'])}")
            st.dataframe(
                pd.DataFrame(summary["unparsed_rows"], columns=["Row", "Value"]),
                use_container_width=True
            )

        # Tidy data checker
        if "empty_columns_removed" in summary:
            removed = summary["empty_columns_removed"]
            if removed:
                st.warning(f"🗑️ Empty columns removed: {removed}")
            else:
                st.info("No empty columns removed.")

        if "empty_rows_removed" in summary:
            st.info(f"🧹 Empty rows removed: **{summary['empty_rows_removed']}**")

        if "nans_replaced" in summary:
            st.info(f"🔄 NaN-like values standardized: **{summary['nans_replaced']}**")

        if "whitespace_trimmed" in summary:
            st.info("✂️ Whitespace trimmed from column names and string cells.")

        if "duplicate_columns_found" in summary:
            dups = summary["duplicate_columns_found"]
            if dups:
                st.warning(f"⚠️ Duplicate column names fixed: {dups}")

        if "case_normalization" in summary:
            mode = summary["case_normalization"]
            st.info(f"🔤 Column name case normalization: **{mode}**")

        if "mixed_type_columns" in summary:
            mixed = summary["mixed_type_columns"]
            if mixed:
                st.warning("⚠️ Mixed data types detected:")
                st.json(mixed)

        if "header_rows_detected" in summary:
            hdrs = summary["header_rows_detected"]
            if hdrs:
                st.warning(f"⚠️ Header-like rows detected at indices: {hdrs}")
