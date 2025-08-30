#!/usr/bin/env python3
"""
Clean merged data files by removing empty rows and fixing data quality issues
"""

import pandas as pd
import os

def clean_merged_data(input_file, output_file=None):
    """
    Clean a merged data file by removing empty rows and fixing data issues
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path for the output cleaned CSV file (optional)
    """
    print(f"🧹 Cleaning data file: {input_file}")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    original_count = len(df)
    print(f"📊 Original records: {original_count}")
    
    # Remove rows where all columns are NaN
    df_cleaned = df.dropna(how='all')
    print(f"🗑️ Removed {original_count - len(df_cleaned)} completely empty rows")
    
    # Remove rows where key columns are NaN
    key_columns = ['Age', 'Gender', 'Principal Diagnosis']
    df_cleaned = df_cleaned.dropna(subset=key_columns, how='all')
    print(f"🗑️ Removed {len(df) - len(df_cleaned)} rows with missing key data")
    
    # Remove rows with invalid dates
    df_cleaned['Schedule Date'] = pd.to_datetime(df_cleaned['Schedule Date'], errors='coerce')
    invalid_dates = df_cleaned['Schedule Date'].isna()
    invalid_date_count = invalid_dates.sum()
    df_cleaned = df_cleaned[~invalid_dates]
    print(f"🗑️ Removed {invalid_date_count} rows with invalid dates")
    
    # Remove rows where Age is NaN or contains invalid values
    invalid_age_patterns = ['DIETERAPY', 'DIABETIC CLINIC', 'INJECTION', 'ACCIDENT', 'SURGICAL', 'GENERAL', 'OPD', 'DM Med Refill']
    age_mask = df_cleaned['Age'].isna() | df_cleaned['Age'].astype(str).str.contains('|'.join(invalid_age_patterns), case=False, na=False)
    invalid_age_count = age_mask.sum()
    df_cleaned = df_cleaned[~age_mask]
    print(f"🗑️ Removed {invalid_age_count} rows with invalid age values")
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_cleaned.csv"
    
    # Save cleaned data
    df_cleaned.to_csv(output_file, index=False)
    
    print(f"✅ Cleaned data saved to: {output_file}")
    print(f"📊 Final records: {len(df_cleaned)}")
    print(f"📈 Data retention: {len(df_cleaned)/original_count*100:.1f}%")
    
    return output_file

def clean_all_merged_data():
    """Clean all merged data files"""
    print("🚀 Cleaning all merged data files...")
    
    # Files to clean
    files_to_clean = [
        'src/artifacts/merged_data/weija_diabetes_merged.csv',
        'src/artifacts/merged_data/weija_malaria_merged.csv'
    ]
    
    cleaned_files = []
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            cleaned_file = clean_merged_data(file_path)
            cleaned_files.append(cleaned_file)
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print(f"\n🎉 Cleaning completed!")
    print(f"✅ Cleaned {len(cleaned_files)} files")
    
    return cleaned_files

def analyze_data_quality(file_path):
    """Analyze data quality of a CSV file"""
    print(f"🔍 Analyzing data quality: {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"📊 Total records: {len(df)}")
    
    # Check for empty rows
    empty_rows = df.isna().all(axis=1).sum()
    print(f"📋 Completely empty rows: {empty_rows}")
    
    # Check for missing key data
    key_columns = ['Age', 'Gender', 'Principal Diagnosis']
    missing_key_data = df[key_columns].isna().all(axis=1).sum()
    print(f"📋 Rows missing key data: {missing_key_data}")
    
    # Check for invalid age values
    invalid_age_patterns = ['DIETERAPY', 'DIABETIC CLINIC', 'INJECTION', 'ACCIDENT', 'SURGICAL', 'GENERAL', 'OPD']
    invalid_ages = df[df['Age'].isna() | df['Age'].astype(str).str.contains('|'.join(invalid_age_patterns), case=False, na=False)]
    print(f"📋 Invalid age values: {len(invalid_ages)}")
    
    if len(invalid_ages) > 0:
        print("📋 Sample invalid age values:")
        print(invalid_ages['Age'].value_counts().head(5))
    
    return df

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analyze specific file
        file_path = sys.argv[1]
        analyze_data_quality(file_path)
    else:
        # Clean all merged data files
        print("Analyzing data quality before cleaning...")
        
        # Analyze diabetes data
        print("\n" + "="*50)
        analyze_data_quality('src/artifacts/merged_data/weija_diabetes_merged.csv')
        
        # Analyze malaria data
        print("\n" + "="*50)
        analyze_data_quality('src/artifacts/merged_data/weija_malaria_merged.csv')
        
        # Ask if user wants to clean the data
        response = input("\nDo you want to clean these files? (y/n): ")
        if response.lower() in ['y', 'yes']:
            clean_all_merged_data() 