import pandas as pd

def build_vocab_dict(df: pd.DataFrame) -> dict:
    var_dict = {}
    current_category = None

    for _, row in df.iterrows():
        category = row["Common Variable Name"]

        # New category
        if pd.notna(category):
            current_category = category
            var_dict[current_category] = {
                "source_names": [],
                "canwin_names": [],
                "descriptions": [],
                "links": [],
                "vocab_sources": [],
            }
            continue

        # Skip blank rows
        if pd.isna(row["Source Standardized Name"]):
            continue

        # Add entries
        var_dict[current_category]["source_names"].append(row["Source Standardized Name"])
        var_dict[current_category]["canwin_names"].append(row["CanWIN Standardized Name"])
        var_dict[current_category]["descriptions"].append(row["Description"])
        var_dict[current_category]["links"].append(row["Link"])
        var_dict[current_category]["vocab_sources"].append(row["Source"])

    return var_dict