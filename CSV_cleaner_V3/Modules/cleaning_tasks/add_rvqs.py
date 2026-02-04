import pandas as pd
import re

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

IGNORE_PATTERNS = [
    "date", "time", "year", "month", "day",
    "lat", "lattit", "lon", "long", "id", 
]

# IMPORTANT: "nan" REMOVED so pandas stringified NaN is not treated as missing
MISSING_REGEX = re.compile(
    r"^(na|n/a|none|null|missing|\.{1,3}|-+)?$",
    re.IGNORECASE
)


# ---------------------------------------------------------
# NUMERIC-MAJORITY DETECTOR
# ---------------------------------------------------------

def detect_numeric_majority_columns(df, threshold=0.8):
    """
    Detect columns that are mostly numeric, excluding:
    - blank/whitespace
    - NaN
    - 'NA', 'N/A', 'none', 'missing', '.', '..', '...', '-', '--'
    - columns whose names match ignore patterns
    """
    numeric_cols = []
    ignore_regex = re.compile("|".join(IGNORE_PATTERNS), re.IGNORECASE)

    for col in df.columns:

        # Skip metadata columns
        if ignore_regex.search(col):
            continue

        # Convert to string and strip whitespace
        series = df[col].astype(str).str.strip()

        # Identify missing values using robust regex
        missing_mask = series.apply(lambda x: bool(MISSING_REGEX.match(x)))

        # Treat actual NaN as missing too
        missing_mask |= df[col].isna()

        non_missing = series[~missing_mask]

        if len(non_missing) == 0:
            continue

        # Compute numeric ratio on non-missing values
        numeric_mask = pd.to_numeric(non_missing, errors="coerce").notna()
        numeric_ratio = numeric_mask.mean()

        if numeric_ratio >= threshold:
            numeric_cols.append(col)

    return numeric_cols


# ---------------------------------------------------------
# MAIN RVQ LOGIC (WITH DETECTION LIMIT EXTRACTION)
# ---------------------------------------------------------

def apply_rvq_rules(
    df,
    columns,
    rules,
    keep_original=True,
    negative_rule_enabled=False,
    negative_rvq_code=None,
    negative_exceptions=None,
    remove_empty_rvq_cols=False
):
    """
    Apply RVQ rules to selected columns.

    Returns:
        df_out        → cleaned DataFrame
        summary_dict  → {column: {rvq_code: count}}
        summary_df    → long-form summary table for download
                        (includes detection limits)
    """

    df_out = df.copy()
    summary_dict = {}
    detection_limits = {}   # {variable: {rvq_code: {limit: count}}}

    if negative_exceptions is None:
        negative_exceptions = []

    # ---------------------------------------------------------
    # APPLY CUSTOM RULES
    # ---------------------------------------------------------

    for col in columns:
        rvq_col = f"{col}_RVQ"

        # Remove existing RVQ column if present
        if rvq_col in df_out.columns:
            df_out = df_out.drop(columns=[rvq_col])

        # Insert fresh RVQ column beside the variable
        col_pos = df_out.columns.get_loc(col)
        df_out.insert(col_pos + 1, rvq_col, "")

        summary_dict[col] = {}
        detection_limits[col] = {}

        series = df_out[col].astype(str)

        # -----------------------------
        # Apply user-defined rules
        # -----------------------------
        for rule in rules:
            code = rule["data_code"]
            rvq = rule["rvq_code"]
            match = rule["match_type"]

            if match == "full":
                mask = series == code
            elif match == "prefix":
                mask = series.str.startswith(code)
            elif match == "suffix":
                mask = series.str.endswith(code)
            elif match == "contains":
                mask = series.str.contains(code, na=False)
            else:
                mask = False

            if mask.any():
                df_out.loc[mask, rvq_col] = rvq
                summary_dict[col][rvq] = summary_dict[col].get(rvq, 0) + mask.sum()

                # Extract detection limits for prefix rules
                if match == "prefix":
                    extracted = series[mask].str.extract(
                        rf"^{re.escape(code)}([0-9]*\.?[0-9]+)"
                    )[0]

                    for val in extracted.dropna():
                        limit = float(val)
                        detection_limits[col].setdefault(rvq, {})
                        detection_limits[col][rvq][limit] = (
                            detection_limits[col][rvq].get(limit, 0) + 1
                        )

                if not keep_original:
                    df_out.loc[mask, col] = ""

        # -----------------------------
        # Apply negative-number rule
        # -----------------------------
        if negative_rule_enabled and col not in negative_exceptions:
            numeric = pd.to_numeric(df_out[col], errors="coerce")
            neg_mask = numeric < 0

            if neg_mask.any():
                df_out.loc[neg_mask, rvq_col] = negative_rvq_code
                summary_dict[col][negative_rvq_code] = (
                    summary_dict[col].get(negative_rvq_code, 0) + neg_mask.sum()
                )

                # Extract detection limits from negative values
                for val in numeric[neg_mask].dropna():
                    limit = abs(float(val))
                    detection_limits[col].setdefault(negative_rvq_code, {})
                    detection_limits[col][negative_rvq_code][limit] = (
                        detection_limits[col][negative_rvq_code].get(limit, 0) + 1
                    )

                if not keep_original:
                    df_out.loc[neg_mask, col] = ""

    # ---------------------------------------------------------
    # REMOVE EMPTY RVQ COLUMNS (optional)
    # ---------------------------------------------------------

    if remove_empty_rvq_cols:
        to_drop = []
        for col in df_out.columns:
            if col.endswith("_RVQ"):
                if df_out[col].replace("", pd.NA).isna().all():
                    to_drop.append(col)

        if to_drop:
            df_out = df_out.drop(columns=to_drop)

    # ---------------------------------------------------------
    # BUILD SUMMARY DATAFRAME (RVQs + detection limits)
    # ---------------------------------------------------------

    summary_rows = []

    for col, rvqs in summary_dict.items():
        for rvq_code, count in rvqs.items():

            # If detection limits exist for this RVQ
            if rvq_code in detection_limits[col]:
                for limit, limit_count in detection_limits[col][rvq_code].items():
                    summary_rows.append({
                        "Variable": col,
                        "RVQ Code": rvq_code,
                        "Detection Limit": limit,
                        "Count": limit_count
                    })
            else:
                # RVQ with no detection limit (e.g., NC, ND)
                summary_rows.append({
                    "Variable": col,
                    "RVQ Code": rvq_code,
                    "Detection Limit": None,
                    "Count": count
                })

    summary_df = pd.DataFrame(summary_rows)

    summary_dict["_rvq_task"] = True
    return df_out, summary_dict, summary_df
