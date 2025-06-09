import pandas as pd

# Load your dataset
df = pd.read_csv("artifacts/csv/health_data_eams_diabetes.csv")

# Assign collection month based on row index ranges (adjust as needed)
df.loc[0:99, 'CollectionMonth'] = '2022-03'
df.loc[100:199, 'CollectionMonth'] = '2022-06'
df.loc[200:299, 'CollectionMonth'] = '2022-09'
df.loc[300:, 'CollectionMonth'] = '2022-12'

# Save updated dataset
df.to_csv("artifacts/csv/health_data_eams_diabetes_time_stamped.csv", index=False)
