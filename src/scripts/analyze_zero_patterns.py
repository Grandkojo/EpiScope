#!/usr/bin/env python3
"""
Analyze zero patterns in diabetes data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_zero_patterns():
    # Load the data
    df = pd.read_csv('src/artifacts/cleaned_data/weija_diabetes_cleaned.csv')
    df['Schedule Date'] = pd.to_datetime(df['Schedule Date'])
    
    print("📊 Diabetes Data Analysis")
    print("=" * 50)
    
    # Original data analysis
    print("Original Data:")
    print(f"Date range: {df['Schedule Date'].min()} to {df['Schedule Date'].max()}")
    print(f"Total records: {len(df)}")
    print(f"Unique dates: {df['Schedule Date'].nunique()}")
    
    # Create daily case counts
    daily_cases = df.groupby('Schedule Date').size().reset_index(name='daily_cases')
    daily_cases = daily_cases.set_index('Schedule Date')
    
    print(f"\nDaily Cases Summary:")
    print(f"Days with data: {len(daily_cases)}")
    print(f"Min cases per day: {daily_cases['daily_cases'].min()}")
    print(f"Max cases per day: {daily_cases['daily_cases'].max()}")
    print(f"Mean cases per day: {daily_cases['daily_cases'].mean():.2f}")
    
    # Check for missing dates
    date_range = pd.date_range(start=daily_cases.index.min(), 
                              end=daily_cases.index.max(), 
                              freq='D')
    missing_dates = date_range.difference(daily_cases.index)
    
    print(f"\nMissing Dates Analysis:")
    print(f"Total days in range: {len(date_range)}")
    print(f"Days with data: {len(daily_cases)}")
    print(f"Missing dates: {len(missing_dates)}")
    
    if len(missing_dates) > 0:
        print(f"Missing date percentage: {(len(missing_dates) / len(date_range) * 100):.1f}%")
        print(f"First 10 missing dates: {missing_dates[:10].tolist()}")
        print(f"Last 10 missing dates: {missing_dates[-10:].tolist()}")
    
    # Create complete time series with zeros for missing dates
    complete_series = daily_cases.reindex(date_range, fill_value=0)
    
    print(f"\nComplete Time Series (with zeros for missing dates):")
    print(f"Total days: {len(complete_series)}")
    print(f"Days with zero cases: {(complete_series['daily_cases'] == 0).sum()}")
    print(f"Days with cases: {(complete_series['daily_cases'] > 0).sum()}")
    print(f"Zero case percentage: {((complete_series['daily_cases'] == 0).sum() / len(complete_series) * 100):.1f}%")
    
    # Find consecutive zero streaks
    print(f"\nConsecutive Zero Analysis:")
    zero_streaks = (complete_series['daily_cases'] == 0).astype(int).groupby(
        (complete_series['daily_cases'] != 0).astype(int).cumsum()
    ).sum()
    
    print(f"Number of zero streaks: {len(zero_streaks)}")
    print(f"Longest zero streak: {zero_streaks.max()} days")
    print(f"Average zero streak: {zero_streaks.mean():.1f} days")
    
    # Find the longest zero streak period
    max_streak = zero_streaks.max()
    if max_streak > 0:
        # Find where this streak occurs
        zero_mask = (complete_series['daily_cases'] == 0)
        streak_groups = zero_mask.groupby((~zero_mask).cumsum())
        
        for i, (group_id, group) in enumerate(streak_groups):
            if group.sum() == max_streak:
                start_idx = group.index[0]
                end_idx = group.index[-1]
                start_date = complete_series.index[start_idx]
                end_date = complete_series.index[end_idx]
                print(f"\nLongest zero streak ({max_streak} days):")
                print(f"  Start: {start_date}")
                print(f"  End: {end_date}")
                print(f"  Duration: {(end_date - start_date).days + 1} days")
                break
    
    # Monthly analysis
    print(f"\nMonthly Analysis:")
    monthly_cases = complete_series.groupby(complete_series.index.to_period('M')).agg({
        'daily_cases': ['sum', 'mean', 'count', lambda x: (x == 0).sum()]
    })
    monthly_cases.columns = ['total_cases', 'avg_cases', 'total_days', 'zero_days']
    monthly_cases['zero_percentage'] = (monthly_cases['zero_days'] / monthly_cases['total_days'] * 100).round(1)
    
    # Show months with highest zero percentages
    high_zero_months = monthly_cases[monthly_cases['zero_percentage'] > 50].sort_values('zero_percentage', ascending=False)
    if len(high_zero_months) > 0:
        print(f"Months with >50% zero days:")
        for period, row in high_zero_months.head(10).iterrows():
            print(f"  {period}: {row['zero_percentage']}% zero days ({row['zero_days']}/{row['total_days']} days)")
    
    # Yearly analysis
    print(f"\nYearly Analysis:")
    yearly_cases = complete_series.groupby(complete_series.index.year).agg({
        'daily_cases': ['sum', 'mean', 'count', lambda x: (x == 0).sum()]
    })
    yearly_cases.columns = ['total_cases', 'avg_cases', 'total_days', 'zero_days']
    yearly_cases['zero_percentage'] = (yearly_cases['zero_days'] / yearly_cases['total_days'] * 100).round(1)
    
    for year, row in yearly_cases.iterrows():
        print(f"  {year}: {row['zero_percentage']}% zero days ({row['zero_days']}/{row['total_days']} days)")
    
    # Test set analysis (last 5 months of 2024)
    test_start = pd.Timestamp('2024-08-01')
    test_data = complete_series[complete_series.index >= test_start]
    
    print(f"\nTest Set Analysis (Aug-Dec 2024):")
    print(f"Test period: {test_data.index.min()} to {test_data.index.max()}")
    print(f"Test days: {len(test_data)}")
    print(f"Test zero days: {(test_data['daily_cases'] == 0).sum()}")
    print(f"Test zero percentage: {((test_data['daily_cases'] == 0).sum() / len(test_data) * 100):.1f}%")
    
    # Find consecutive zeros in test set
    test_zero_streaks = (test_data['daily_cases'] == 0).astype(int).groupby(
        (test_data['daily_cases'] != 0).astype(int).cumsum()
    ).sum()
    
    if len(test_zero_streaks) > 0:
        print(f"Test set zero streaks: {test_zero_streaks.tolist()}")
        print(f"Longest test zero streak: {test_zero_streaks.max()} days")
    
    return complete_series

if __name__ == "__main__":
    complete_series = analyze_zero_patterns() 