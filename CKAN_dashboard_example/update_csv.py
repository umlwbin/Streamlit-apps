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



# os.makedirs(output_dir, exist_ok=True)

# # Step 2: Simulate or download data
# # Replace this with your actual data source (API, database, etc.)
# data = pd.DataFrame({
#     'hour': range(24),
#     'value': [abs(50 + 10 * (i % 5) - i) for i in range(24)]
# })

# # Save data as CSV
# data_path = os.path.join(output_dir, 'daily_data.csv')
# data.to_csv(data_path, index=False)

# # Step 3: Generate image (e.g., line plot)
# plt.figure(figsize=(10, 6))
# plt.plot(data['hour'], data['value'], marker='o')
# plt.title(f'Daily Value Trend - {today}')
# plt.xlabel('Hour')
# plt.ylabel('Value')
# plt.grid(True)

# # Save image
# image_path = os.path.join(output_dir, 'daily_plot.png')
# plt.savefig(image_path)
# plt.close()

# print(f"✅ Data and image saved to: {output_dir}")
