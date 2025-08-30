#!/usr/bin/env python3
"""
Simple analysis of zero patterns in diabetes data
"""

import pandas as pd
import numpy as np

def simple_zero_analysis():
    # Load the data
    df = pd.read_csv('src/artifacts/cleaned_data/weija_diabetes_cleaned.csv')
    df['Schedule Date'] = pd.to_datetime(df['Schedule Date'])
    
    print("📊 Diabetes Zero Pattern Analysis")
    print("=" * 50)
    
    # Original data
    print("Original Data:")
    print(f"Date range: {df['Schedule Date'].min()} to {df['Schedule Date'].max()}")
    print(f"Total records: {len(df)}")
    print(f"Unique dates: {df['Schedule Date'].nunique()}")
    
    # Create daily case counts
    daily_cases = df.groupby('Schedule Date').size().reset_index(name='daily_cases')
    daily_cases = daily_cases.set_index('Schedule Date')
    
    # Check for missing dates
    date_range = pd.date_range(start=daily_cases.index.min(), 
                              end=daily_cases.index.max(), 
                              freq='D')
    missing_dates = date_range.difference(daily_cases.index)
    
    print(f"\nMissing Dates:")
    print(f"Total days in range: {len(date_range)}")
    print(f"Days with data: {len(daily_cases)}")
    print(f"Missing dates: {len(missing_dates)}")
    print(f"Missing date percentage: {(len(missing_dates) / len(date_range) * 100):.1f}%")
    
    # Create complete time series with zeros
    complete_series = daily_cases.reindex(date_range, fill_value=0)
    
    print(f"\nComplete Time Series:")
    print(f"Total days: {len(complete_series)}")
    print(f"Days with zero cases: {(complete_series['daily_cases'] == 0).sum()}")
    print(f"Days with cases: {(complete_series['daily_cases'] > 0).sum()}")
    print(f"Zero case percentage: {((complete_series['daily_cases'] == 0).sum() / len(complete_series) * 100):.1f}%")
    
    # Find consecutive zero streaks
    zero_mask = (complete_series['daily_cases'] == 0)
    streak_lengths = []
    current_streak = 0
    
    for is_zero in zero_mask:
        if is_zero:
            current_streak += 1
        else:
            if current_streak > 0:
                streak_lengths.append(current_streak)
                current_streak = 0
    
    if current_streak > 0:
        streak_lengths.append(current_streak)
    
    if streak_lengths:
        print(f"\nZero Streak Analysis:")
        print(f"Number of zero streaks: {len(streak_lengths)}")
        print(f"Longest zero streak: {max(streak_lengths)} days")
        print(f"Average zero streak: {np.mean(streak_lengths):.1f} days")
        
        # Find the longest streak period
        max_streak = max(streak_lengths)
        current_streak = 0
        streak_start = None
        
        for i, is_zero in enumerate(zero_mask):
            if is_zero:
                if current_streak == 0:
                    streak_start = complete_series.index[i]
                current_streak += 1
            else:
                if current_streak == max_streak:
                    streak_end = complete_series.index[i-1]
                    print(f"\nLongest zero streak ({max_streak} days):")
                    print(f"  Start: {streak_start}")
                    print(f"  End: {streak_end}")
                    break
                current_streak = 0
    
    # Monthly analysis
    print(f"\nMonthly Zero Analysis:")
    monthly_zeros = complete_series.groupby(complete_series.index.to_period('M')).apply(
        lambda x: (x['daily_cases'] == 0).sum()
    )
    monthly_total = complete_series.groupby(complete_series.index.to_period('M')).size()
    monthly_percentage = (monthly_zeros / monthly_total * 100).round(1)
    
    # Show months with highest zero percentages
    high_zero_months = monthly_percentage[monthly_percentage > 30].sort_values(ascending=False)
    if len(high_zero_months) > 0:
        print(f"Months with >30% zero days:")
        for period, percentage in high_zero_months.head(10).items():
            print(f"  {period}: {percentage}% zero days")
    
    # Test set analysis (last 5 months of 2024)
    test_start = pd.Timestamp('2024-08-01')
    test_data = complete_series[complete_series.index >= test_start]
    
    print(f"\nTest Set Analysis (Aug-Dec 2024):")
    print(f"Test period: {test_data.index.min()} to {test_data.index.max()}")
    print(f"Test days: {len(test_data)}")
    print(f"Test zero days: {(test_data['daily_cases'] == 0).sum()}")
    print(f"Test zero percentage: {((test_data['daily_cases'] == 0).sum() / len(test_data) * 100):.1f}%")
    
    # Find consecutive zeros in test set
    test_zero_mask = (test_data['daily_cases'] == 0)
    test_streak_lengths = []
    current_streak = 0
    
    for is_zero in test_zero_mask:
        if is_zero:
            current_streak += 1
        else:
            if current_streak > 0:
                test_streak_lengths.append(current_streak)
                current_streak = 0
    
    if current_streak > 0:
        test_streak_lengths.append(current_streak)
    
    if test_streak_lengths:
        print(f"Test set zero streaks: {test_streak_lengths}")
        print(f"Longest test zero streak: {max(test_streak_lengths)} days")
    
    return complete_series

if __name__ == "__main__":
    complete_series = simple_zero_analysis() 