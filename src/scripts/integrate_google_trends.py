import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_and_prepare_data():
    """Load all relevant datasets and prepare for integration"""
    
    # Load Google Trends data
    trends_df = pd.read_csv('src/artifacts/time_series/google_trends_time_series.csv')
    
    # Load health data
    diabetes_health = pd.read_csv('src/artifacts/csv/health_data_eams_diabetes.csv')
    malaria_health = pd.read_csv('src/artifacts/csv/health_data_eams_malaria.csv')
    
    # Load time-stamped data if available
    try:
        diabetes_timestamped = pd.read_csv('src/artifacts/time_series/health_data_eams_diabetes_time_stamped.csv')
        malaria_timestamped = pd.read_csv('src/artifacts/time_series/health_data_eams_malaria_time_stamped.csv')
    except FileNotFoundError:
        print("Time-stamped data not found. Creating it...")
        diabetes_timestamped = create_time_stamped_data(diabetes_health, 'diabetes')
        malaria_timestamped = create_time_stamped_data(malaria_health, 'malaria')
    
    return trends_df, diabetes_timestamped, malaria_timestamped

def create_time_stamped_data(df, disease_type):
    """Create time-stamped data based on row ranges"""
    # Define time periods based on your existing logic
    time_periods = [
        ('2022-03', 0, 170),
        ('2022-06', 170, 278),
        ('2022-09', 278, 380),
        ('2022-10', 380, 513),
        ('2023-03', 513, 573),
        ('2023-06', 573, 621),
        ('2023-09', 621, 673),
        ('2023-10', 673, 740),
        ('2024-03', 740, 794),
        ('2024-06', 794, 836),
        ('2024-09', 836, 886),
        ('2024-10', 886, len(df))
    ]
    
    df_copy = df.copy()
    df_copy['Month'] = 'Unknown'
    
    for period, start, end in time_periods:
        if start < len(df_copy):
            end = min(end, len(df_copy))
            df_copy.loc[start:end-1, 'Month'] = period
    
    return df_copy

def aggregate_health_data_by_month(df, disease_type):
    """Aggregate health data by month to match trends data"""
    monthly_stats = df.groupby('Month').agg({
        'Age': ['count', 'mean', 'std'],
        'Sex': 'mean',  # Proportion of females
        'NHIA Patient': 'mean',  # Proportion of NHIA patients
        'Pregnant Patient': 'mean'  # Proportion of pregnant patients
    }).round(2)
    
    # Flatten column names
    monthly_stats.columns = [f'{col[0]}_{col[1]}' if col[1] else col[0] 
                            for col in monthly_stats.columns]
    
    monthly_stats = monthly_stats.reset_index()
    monthly_stats['disease_type'] = disease_type
    
    return monthly_stats

def merge_trends_with_health_data(trends_df, diabetes_monthly, malaria_monthly):
    """Merge Google Trends data with health data statistics"""
    
    # Merge diabetes data
    diabetes_merged = trends_df.merge(
        diabetes_monthly, 
        left_on='Month', 
        right_on='Month', 
        how='left'
    )
    
    # Merge malaria data
    malaria_merged = trends_df.merge(
        malaria_monthly, 
        left_on='Month', 
        right_on='Month', 
        how='left'
    )
    
    # Create combined dataset
    combined_data = pd.concat([
        diabetes_merged.assign(disease='diabetes'),
        malaria_merged.assign(disease='malaria')
    ], ignore_index=True)
    
    return combined_data

def create_enhanced_features(combined_data):
    """Create enhanced features for analysis"""
    
    # Create lag features for trends
    combined_data['diabetes_trend_lag1'] = combined_data.groupby('disease')['diabetes_trend'].shift(1)
    combined_data['malaria_trend_lag1'] = combined_data.groupby('disease')['malaria_trend'].shift(1)
    
    # Create trend ratios
    combined_data['diabetes_malaria_ratio'] = combined_data['diabetes_trend'] / combined_data['malaria_trend']
    
    # Create seasonal features
    combined_data['Month'] = pd.to_datetime(combined_data['Month'] + '-01')
    combined_data['quarter'] = combined_data['Month'].dt.quarter
    combined_data['year'] = combined_data['Month'].dt.year
    
    # Create interaction features
    combined_data['trend_case_interaction'] = combined_data['diabetes_trend'] * combined_data['Age_count']
    
    return combined_data

def save_integrated_data(combined_data, output_dir='src/artifacts/integrated'):
    """Save the integrated dataset"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save full integrated dataset
    combined_data.to_csv(f'{output_dir}/integrated_disease_trends_data.csv', index=False)
    
    # Save separate datasets for each disease
    diabetes_data = combined_data[combined_data['disease'] == 'diabetes']
    malaria_data = combined_data[combined_data['disease'] == 'malaria']
    
    diabetes_data.to_csv(f'{output_dir}/diabetes_with_trends.csv', index=False)
    malaria_data.to_csv(f'{output_dir}/malaria_with_trends.csv', index=False)
    
    print(f"Integrated data saved to {output_dir}/")
    return combined_data

def main():
    """Main function to integrate Google Trends data with health data"""
    print("Loading and preparing data...")
    trends_df, diabetes_timestamped, malaria_timestamped = load_and_prepare_data()
    
    print("Aggregating health data by month...")
    diabetes_monthly = aggregate_health_data_by_month(diabetes_timestamped, 'diabetes')
    malaria_monthly = aggregate_health_data_by_month(malaria_timestamped, 'malaria')
    
    print("Merging trends with health data...")
    combined_data = merge_trends_with_health_data(trends_df, diabetes_monthly, malaria_monthly)
    
    print("Creating enhanced features...")
    enhanced_data = create_enhanced_features(combined_data)
    
    print("Saving integrated data...")
    final_data = save_integrated_data(enhanced_data)
    
    print("Integration complete!")
    print(f"Final dataset shape: {final_data.shape}")
    print(f"Columns: {list(final_data.columns)}")
    
    return final_data

if __name__ == "__main__":
    main() 