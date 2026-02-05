#!/bin/bash

# Navigate to the repo folder
cd /Users/yaniquecampbell/Git/Streamlit-apps/CKAN_dashboard_example/

# Pull latest changes to avoid conflicts
git pull origin main --rebase

# Run the Python script (updates data.csv)
/opt/anaconda3/bin/python3 update_csv.py

# Stage the updated CSV
git add 2022_ctd.csv

# Commit with timestamp
git commit -m "Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
git push origin main

