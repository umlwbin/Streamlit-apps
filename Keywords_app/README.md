# CanWIN Keyword Explorer (Streamlit App)

This project provides a user‑friendly way to explore keywords stored in CanWIN’s Google Sheet.  
The app groups keywords into blocks of letters (e.g. A–C, D–F) and displays them in expandable sections.  
It also includes a predictive search bar, with optional fuzzy matching for typo tolerance.

---

## Project Structure:

- app.py → Streamlit UI code
- keywords.py → Pure Python logic (data loading, cleaning, grouping)
- requirements.txt → Dependencies
- README.md → Documentation

---

## Installation:

1. Clone the repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

---

## Usage with Streamlit:
Run the app locally:

```
streamlit run app.py
```
Open the provided local URL (usually http://localhost:8501) in your browser.

---

## Usage without Streamlit (pure Python):
You can run the keyword logic directly to test data loading and grouping without the UI:

```
python -i keywords.py
```
This will load the functions into an interactive Python shell.  
For example:

```python
from keywords import load_keywords, group_columns

df = load_keywords()
groups = group_columns(df, chunk_size=3)

print(groups["A – C"])
```
This prints the grouped keywords directly in the terminal, without Streamlit.

---

## Configuration:

- Chunk size: Adjust grouping in `group_columns(df, chunk_size=3)` to change block size.
- Fuzzy search threshold: In `app.py`, filter fuzzy matches by score (e.g. `score > 70`) to reduce noise.

---

## Packages

- **streamlit** → runs the app and provides UI components (expanders, columns, buttons, etc.).
- **pandas** → loads and cleans the Google Sheet CSV data.
- **rapidfuzz** → enables fuzzy search/typo tolerance.
- **wordcloud** → generates the keyword cloud visualization.
- **matplotlib** → renders the word cloud image inside Streamlit.
