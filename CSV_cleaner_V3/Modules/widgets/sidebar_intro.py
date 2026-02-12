import streamlit as st
from Modules.ui_utils import big_caption

def sidebar():

    # --- Brand Header Block ---
    st.markdown("""
        <div style="
            padding-bottom: 0.6rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        ">
            <h2 style="
                margin: 0;
                font-weight: 700;
                font-size: 1.5rem;
                line-height: 1.3;
            ">
                Welcome to the CSV Curation Studio!
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Caption under the title
    big_caption(
        "A dedicated workspace for cleaning, reshaping, and preparing CSV datasets.",
        size="1.05rem",
        color="#6c757d"
    )

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    # --- Intro Paragraph ---
    st.markdown("""
        <div style="font-size: 1rem; line-height: 1.45; color: #444;">
            This tool helps you clean and prepare CSV files for analysis or database ingestion.
            Upload one or more files, apply step‑by‑step cleaning tasks, and preview changes
            in real time. Every transformation is tracked so you always know what was applied.
            <br><br>
            The Studio also includes specialized tools for <strong>provincial chemistry datasets</strong>,
            which often contain multi‑row headers, Units/VMV metadata, and variable/value structures
            that require careful reshaping.
        </div>
    """, unsafe_allow_html=True)

    # --- Workflow Section ---
    with st.expander("Recommended Workflow"):
        st.markdown("""
            ### Recommended workflow

            **1. Start with _Tidy Data_**  
            This performs a general cleanup:
            - removes empty rows/columns  
            - standardizes NaN values  
            - trims whitespace  
            - fixes duplicate column names  
            - normalizes case  
            - detects header rows and mixed types  
            - cleans scientific headers

            **2. Apply additional tasks**  
            Use the tools on the right to reshape, rename, merge, or further refine your data.

            **3. Download your cleaned files**  
            Scroll to the bottom of the page to export CSV or Excel versions.

            **4. Need to start over?**  
            Use **Reset All Files** at the top of the page to restore your original uploads.
        """)

    # --- Provincial Chemistry Section ---
    with st.expander("🧪 Working with Provincial Chemistry Data"):
        st.markdown("""
        Provincial chemistry datasets have a **unique structure** that differs from regular tidy data tables.
        To help you choose the right tool, here’s how the provincial‑specific options differ from the standard reshape tools.

        ### Why provincial chemistry files are different
        These files often contain:
        - a **Variable/Parameter** column  
        - a **Value** column  
        - optional metadata rows such as **Units**, **VMV codes**, or **Variable codes**  
        - header information spread across multiple rows  
        - repeated measurements for the same site/date/parameter  

        This structure requires specialized reshaping.

        ---

        ### ↘️ Regular Pivot Wide → Long (Melt)
        Use this when:
        - your measurement columns are already separate (e.g., `Temp1`, `Temp2`, `Temp3`)
        - you want to stack many columns into two columns (`Variable`, `Value`)
        - your headers are already clean and in a single row

        **Not suitable** for provincial chemistry files because their variables are *already* in a column.

        ---

        ### ↗️ Regular Pivot Long → Wide
        Use this when:
        - you have a `Variable` column and a `Value` column
        - you want each variable to become its own column
        - your headers are already clean and do not contain Units/VMV rows

        **Works**, but does **not** handle:
        - Units rows  
        - VMV code rows  
        - multi‑row headers  
        - merging metadata into column names  

        ---

        ### 🧪 Provincial Chemistry Pivot (Recommended)
        This tool is designed specifically for provincial chemistry datasets.

        It:
        - pivots the `Variable` column into separate columns  
        - merges **Units**, **VMV**, and **Variable codes** into the final column names  
        - handles multi‑row headers  
        - ensures tidy, wide output ready for analysis or database ingestion  

        ---

        ### Merge Header Rows (Units + VMV)
        Use this when:
        - your file has **Units** in row 2  
        - **VMV codes** in row 3  
        - and the actual column names in row 1  

        This tool merges those rows into a single clean header before pivoting.
        """)

    # --- Logo ---
    st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

    logo = (
        "https://cwincloud.cc.umanitoba.ca/canwin_public/datamanagement/"
        "-/raw/master/images/apps_images/UM-EarthObservationScience-cmyk-left.png?ref_type=heads"
    )
    st.image(logo, width=180)
