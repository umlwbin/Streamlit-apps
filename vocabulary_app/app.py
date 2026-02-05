import streamlit as st
from config import LOGO_PATH
from data_loader import load_vocab_sheet
from vocab_parser import build_vocab_dict

st.set_page_config(page_title="CanWIN Vocabulary", page_icon="📖", layout="wide")

# -----------------------------
# Page Title + Intro
# -----------------------------
st.sidebar.title("CanWIN Standardized Vocabulary 📖")
st.sidebar.markdown(
    """
    ## How to use this tool

    This app helps you find **standardized variable names** for common arctic, marine, and freshwater measurements. 
    Using standardized vocabularies makes your datasets more interoperable, reusable, and aligned with international standards such as **BODC** and **CF**.

    ### Steps
    1. Select a **variable category** from the dropdown.
    2. Browse the list of **standardized variable names** under that category.
    3. Choose the term whose **definition** best matches your variable.
    4. Add the **Source Link** to your data dictionary.
    5. All done 🎉
    """
)
st.sidebar.image(LOGO_PATH, width=250)

df = load_vocab_sheet()
var_dict = build_vocab_dict(df)
categories = list(var_dict.keys())

# -----------------------------
# Dropdown 1: Category
# -----------------------------
st.markdown("#### 👩🏽‍🔬 Choose a variable category")
var_selection = st.selectbox("Select an option", categories)

selected_category = var_dict[var_selection]
canwin_names = selected_category["canwin_names"]

st.markdown("---")

# -----------------------------
# Dropdown 2: Standardized Name
# -----------------------------
st.markdown(f"#### Standardized names under **{var_selection}**")
stan_selection = st.selectbox("Select an option", canwin_names)

idx = canwin_names.index(stan_selection)
st.markdown(" ")

# -----------------------------
# Definition Card Styling
# -----------------------------
st.markdown(
    """
    <style>
    .definition-box {
        background-color: #f7f9fc;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e4ea;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    .definition-box h3 {
        margin-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Definition Card
# -----------------------------
st.markdown(
    f"""
    <div class="definition-box">
        <h4>Definition for {stan_selection}</h4>
        <p>{selected_category["descriptions"][idx]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Source Vocabulary
# -----------------------------
vocab_source = selected_category["vocab_sources"][idx]
source_label = (
    "British Oceanographic Data Centre (BODC) vocabulary"
    if vocab_source == "BODC"
    else "Climate and Forecast (CF) vocabulary"
)

st.markdown("#### 📚 Source vocabulary")
st.write(source_label)

st.markdown("#### 🏷️ Preferred label")
st.write(selected_category["source_names"][idx])

st.markdown("#### 🔗 Source link")
st.write(selected_category["links"][idx])

st.markdown("---")

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<p style='text-align:center; color:#888;'>Built by CanWIN • University of Manitoba</p>",
    unsafe_allow_html=True
)