import pandas as pd
import requests
from io import StringIO
from config import SHEET_URL

def load_vocab_sheet() -> pd.DataFrame:
    response = requests.get(SHEET_URL)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))

