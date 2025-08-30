from data_preprocessing_v2 import clean_dataset
import pandas as pd

diabetes_data = pd.read_csv('src/artifacts/merged_data/weija_diabetes_merged.csv')
malaria_data = pd.read_csv('src/artifacts/merged_data/weija_malaria_merged.csv')

diabetes_clean = clean_dataset(diabetes_data, 'diabetes')
malaria_clean = clean_dataset(malaria_data, 'malaria')

diabetes_clean.to_csv('src/artifacts/cleaned_data/weija_diabetes_cleaned.csv', index=False)
malaria_clean.to_csv('src/artifacts/cleaned_data/weija_malaria_cleaned.csv', index=False)