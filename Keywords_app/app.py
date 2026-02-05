import streamlit as st
from keywords import load_keywords, group_columns, build_dropdown_options
from rapidfuzz import process

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Load and prepare data ---
# Load the cleaned DataFrame from Google Sheets
df = load_keywords()

# Group columns into blocks of 3 letters (e.g. A–C, D–F, etc.)
groups = group_columns(df, chunk_size=3)

# Build dropdown options (not currently used in this version,
# but available if you want a flat selectbox with headings)
dropdown_options = build_dropdown_options(df)

# --- App Title ---
st.title("🔍 CanWIN Keyword Explorer")


# --- Word Cloud View ---
st.subheader("🌥️ Keyword Cloud")
all_keywords = sum([sum(group.values(), []) for group in groups.values()], [])
text = " ".join(all_keywords)

wc = WordCloud(width=800, height=400, background_color="white").generate(text)

fig, ax = plt.subplots()
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

st.markdown("---")


# --- Predictive search across all keywords ---
# Flatten all keywords from all groups into a single list
all_keywords = sum([sum(group.values(), []) for group in groups.values()], [])

# Text input for search
search_term = st.text_input("Search keywords:")

# If user types something, filter keywords dynamically
if search_term:
    # Use fuzzy matching to get best matches (limit to top 10)
    matches = process.extract(search_term, all_keywords, limit=10)

    if matches:
        # matches is a list of tuples: (keyword, score, index)
        # We only need the keyword part
        match_keywords = [m[0] for m in matches]
        selected = st.selectbox("Did you mean:", match_keywords)
        st.success(f"You selected: {selected}")
    else:
        st.warning("No matches found.")

st.markdown("---")

# --- Grouped blocks with letter headings ---

for label, col_dict in groups.items():
    with st.expander(f"🏷️ Keywords {label}"):
        for letter, kws in col_dict.items():
            if kws:
                st.markdown(f"**{letter}**")  # heading
                # Grid layout: 3 cards per row
                cols = st.columns(3)
                for i, kw in enumerate(kws):
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div style="padding:10px; margin:5px; border:1px solid #ccc; 
                                    border-radius:8px; text-align:center; background-color:#f9f9f9;">
                            {kw}
                        </div>
                        """, unsafe_allow_html=True)