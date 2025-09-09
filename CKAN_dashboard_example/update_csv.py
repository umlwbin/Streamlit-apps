import pandas as pd
import datetime
import os


input_path=os.path.abspath(os.curdir)

# Step 1: Set up timestamped folder
today = datetime.date.today().strftime('%Y-%m-%d')
output_dir = f"{input_path}/output/{today}"


#Read File
df = pd.read_csv('2022_ctd.csv')
df.iat[0, 0] = df.iat[0, 0] + 5
df.to_csv('2022_ctd.csv', index=False)

