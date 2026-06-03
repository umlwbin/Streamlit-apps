import pandas as pd
import re


def apply_rvq_rules(
    df: pd.DataFrame,
    *,
    filename=None,
    columns,
    rules,
    keep_original=True,
    negative_rule_enabled=False,
    negative_rvq_code=None,
    negative_exceptions=None,
    **kwargs
):
    """
    Apply RVQ (Result Value Qualifier) rules to selected columns.

    RVQs flag values that may be unusual, missing or above/below detection limits.
      Rules can match:
        - exact values ("full")
        - prefixes (e.g., "<", "<0.5")
        - suffixes
        - substrings ("contains")

    This task:
        • creates a new <column>_RVQ column beside each selected variable
        • applies user‑defined RVQ rules
        • optionally applies a negative‑value rule
        • extracts detection limits from prefix and negative rules
        • optionally removes empty RVQ columns
        • stores a long‑form detection‑limit table in
        st.session_state.supplementary_outputs
        • returns only the cleaned DataFrame and a summary dictionary

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    columns : list[str]
        Columns to which RVQ rules should be applied.

    rules : list[dict]
        Each rule must contain:
            {
                "data_code": str,
                "rvq_code": str,
                "match_type": {"full", "prefix", "suffix", "contains"}
            }

    negative_rule_enabled : bool, optional
        If True, negative numeric values are flagged with `negative_rvq_code`.

    negative_rvq_code : str or None, optional
        RVQ code to apply to negative values.

    negative_exceptions : list[str] or None, optional
        Columns exempt from the negative‑value rule.

    keep_original : bool, optional
        If False, matched values are replaced with empty strings.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        DataFrame with RVQ columns added and values optionally cleaned.

    rvq_metadata_df : pandas.DataFrame
        Long-form table describing RVQ assignments and detection limits.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if not isinstance(columns, list):
        raise ValueError("columns must be a list of column names.")

    if not isinstance(rules, list):
        raise ValueError("rules must be a list of rule dictionaries.")

    for rule in rules:
        if not all(k in rule for k in ["data_code", "rvq_code", "match_type"]):
            raise ValueError("Each rule must contain data_code, rvq_code, and match_type.")
        if rule["match_type"] not in {"full", "prefix", "suffix", "contains"}:
            raise ValueError(f"Invalid match_type '{rule['match_type']}'.")

    if negative_exceptions is not None and not isinstance(negative_exceptions, list):
        raise ValueError("negative_exceptions must be a list or None.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. PREP - Remove missing columns (widget handles soft validation)
    # -----------------------------------------------------
    columns = [c for c in columns if c in cleaned_df.columns]

    if negative_exceptions is None:
        negative_exceptions = []

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    rvq_counts = {}          # {column: {rvq_code: count}}
    detection_limits = {}    # {column: {rvq_code: {limit: count}}}

    for col in columns:

        rvq_col = f"{col}_RVQ"

        # Remove existing RVQ column if present
        if rvq_col in cleaned_df.columns:
            cleaned_df = cleaned_df.drop(columns=[rvq_col])

        # Insert RVQ column beside the data column
        col_pos = cleaned_df.columns.get_loc(col)
        cleaned_df.insert(col_pos + 1, rvq_col, "")

        rvq_counts[col] = {}
        detection_limits[col] = {}

        series = cleaned_df[col].astype(str)

        # -------------------------------------------------
        # 3A. APPLY USER-DEFINED RVQ RULES
        # -------------------------------------------------
        for rule in rules:
            code = rule["data_code"]
            rvq = rule["rvq_code"]
            match = rule["match_type"]

            # Determine matching rows
            if match == "full":
                mask = series == code

            elif match == "contains":
                if code.lower() == "nan":
                    mask = (
                        series.str.contains("nan", case=False, na=False)
                        | (series.str.strip() == "")
                        | (series == "nan")
                        | (series == "NaN")
                        | (series == "NAN")
                    )
                else:
                    mask = series.str.contains(re.escape(code), na=False)

            else:
                mask = False

            if not mask.any():
                continue

            # Assign RVQ code
            cleaned_df.loc[mask, rvq_col] = rvq
            rvq_counts[col][rvq] = rvq_counts[col].get(rvq, 0) + mask.sum()

            # -------------------------------------------------
            # Extract detection limits (FULL MATCH)
            # -------------------------------------------------
            if match == "full":
                nums = re.findall(r"([0-9]*\.?[0-9]+)", code)
                if nums:
                    limit = float(nums[0])
                    detection_limits[col].setdefault(rvq, {})
                    detection_limits[col][rvq][limit] = (
                        detection_limits[col][rvq].get(limit, 0) + mask.sum()
                    )

                    cleaned_df.loc[mask, rvq_col] = cleaned_df.loc[mask, rvq_col].apply(
                        lambda x: f"{rvq} [{limit}]" if x == rvq else x
                    )

            # -------------------------------------------------
            # Extract detection limits (CONTAINS)
            # -------------------------------------------------
            if match == "contains":
                number_lists = series[mask].str.findall(r"([0-9]*\.?[0-9]+)")

                for idx, nums in zip(series[mask].index, number_lists):
                    if nums:
                        limit = float(nums[0])
                        detection_limits[col].setdefault(rvq, {})
                        detection_limits[col][rvq][limit] = (
                            detection_limits[col][rvq].get(limit, 0) + 1
                        )

                        if cleaned_df.at[idx, rvq_col] == rvq:
                            cleaned_df.at[idx, rvq_col] = f"{rvq} [{limit}]"

            # Optionally remove original data code
            if not keep_original:
                cleaned_df.loc[mask, col] = ""

        # -----------------------------------------------------
        # 3B. NEGATIVE VALUE RULE
        # -----------------------------------------------------
        if negative_rule_enabled and col not in negative_exceptions and negative_rvq_code:

            numeric = pd.to_numeric(cleaned_df[col], errors="coerce")
            neg_mask = (numeric < 0) & (cleaned_df[rvq_col] == "")

            if neg_mask.any():

                cleaned_df.loc[neg_mask, rvq_col] = cleaned_df.loc[neg_mask].apply(
                    lambda row: f"{negative_rvq_code} [{abs(float(row[col]))}]",
                    axis=1
                )

                rvq_counts[col][negative_rvq_code] = (
                    rvq_counts[col].get(negative_rvq_code, 0) + neg_mask.sum()
                )

                for val in numeric[neg_mask].dropna():
                    limit = abs(float(val))
                    detection_limits[col].setdefault(negative_rvq_code, {})
                    detection_limits[col][negative_rvq_code][limit] = (
                        detection_limits[col][negative_rvq_code].get(limit, 0) + 1
                    )

                if not keep_original:
                    cleaned_df.loc[neg_mask, col] = ""

    # -----------------------------------------------------
    # 4. BUILD METADATA TABLE
    # -----------------------------------------------------
    rows = []

    for col, rvqs in rvq_counts.items():
        for rvq_code, count in rvqs.items():

            if rvq_code in detection_limits[col]:
                for limit, limit_count in detection_limits[col][rvq_code].items():
                    rows.append({
                        "Variable": col,
                        "RVQ Code": rvq_code,
                        "Detection Limit": limit,
                        "Count": limit_count,
                    })
            else:
                rows.append({
                    "Variable": col,
                    "RVQ Code": rvq_code,
                    "Detection Limit": None,
                    "Count": count,
                })

    rvq_metadata_df = pd.DataFrame(rows)

    # -----------------------------------------------------
    # 5. RETURN
    # -----------------------------------------------------
    return cleaned_df, rvq_metadata_df
