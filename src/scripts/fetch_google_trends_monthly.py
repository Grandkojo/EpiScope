import pandas as pd
from pytrends.request import TrendReq
import time
import os
from datetime import datetime

# Settings
kw_list = ['diabetes', 'malaria']  # Add more diseases as needed
start_year, end_year = 2020, 2025
output_csv = 'src/artifacts/time_series/google_trends_full_monthly.csv'

# Generate all months from Jan 2020 to Dec 2025
months = pd.date_range(f'{start_year}-01-01', f'{end_year}-12-31', freq='MS').strftime('%Y-%m').tolist()

pytrends = TrendReq(hl='en-US', tz=0)
results = []

# Load progress if exists
if os.path.exists(output_csv):
    results = pd.read_csv(output_csv).to_dict('records')
    done_months = set(r['Month'] for r in results)
else:
    done_months = set()

for month in months:
    if month in done_months:
        print(f"Skipping {month}, already fetched.")
        continue
    start = f"{month}-01"
    end = (pd.to_datetime(start) + pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d')
    timeframe = f"{start} {end}"
    try:
        pytrends.build_payload(kw_list, timeframe=timeframe, geo='')
        df = pytrends.interest_over_time()
        row = {'Month': month}
        if not df.empty:
            for kw in kw_list:
                row[f"{kw}_trend"] = df[kw].mean()
        else:
            for kw in kw_list:
                row[f"{kw}_trend"] = None
        results.append(row)
        pd.DataFrame(results).to_csv(output_csv, index=False)
        print(f"Fetched and saved {month}")
    except Exception as e:
        print(f"Error for {month}: {e}")
    time.sleep(60)  # Wait 60 seconds between requests

print("Done. Data saved to", output_csv) 