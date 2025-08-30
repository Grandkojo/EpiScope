#!/usr/bin/env python3
"""
Script to extract localities and orgnames from HospitalHealthData table
and save them to a CSV file for use in filters.
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import HospitalHealthData

def extract_hospital_localities():
    """
    Extract unique combinations of locality and orgname from HospitalHealthData
    """
    print("🏥 Extracting Hospital Localities from Database...")
    print("=" * 60)
    
    try:
        # Get all unique combinations of locality and orgname
        localities_data = HospitalHealthData.objects.values(
            'address_locality', 
            'orgname'
        ).distinct().order_by('address_locality', 'orgname')
        
        # Convert to list of dictionaries
        data_list = []
        for item in localities_data:
            if item['address_locality'] and item['orgname']:  # Skip empty values
                data_list.append({
                    'locality': item['address_locality'].strip(),
                    'orgname': item['orgname'].strip(),
                    'created_at': datetime.now().isoformat()
                })
        
        print(f"✅ Found {len(data_list)} unique locality-orgname combinations")
        
        # Create DataFrame
        df = pd.DataFrame(data_list)
        
        # Sort by locality and orgname
        df = df.sort_values(['locality', 'orgname']).reset_index(drop=True)
        
        # Add an ID column
        df.insert(0, 'id', range(1, len(df) + 1))
        
        # Save to CSV
        csv_filename = 'hospital_localities.csv'
        df.to_csv(csv_filename, index=False)
        
        print(f"✅ Saved {len(df)} records to {csv_filename}")
        
        # Display sample data
        print("\n📊 Sample Data:")
        print("-" * 60)
        print(df.head(10).to_string(index=False))
        
        # Show statistics
        print(f"\n📈 Statistics:")
        print(f"   Total unique localities: {df['locality'].nunique()}")
        print(f"   Total unique hospitals: {df['orgname'].nunique()}")
        print(f"   Total combinations: {len(df)}")
        
        # Show top localities
        print(f"\n🏘️  Top 10 Localities:")
        locality_counts = df['locality'].value_counts().head(10)
        for locality, count in locality_counts.items():
            print(f"   {locality}: {count} hospitals")
        
        # Show top hospitals
        print(f"\n🏥 Top 10 Hospitals:")
        hospital_counts = df['orgname'].value_counts().head(10)
        for hospital, count in hospital_counts.items():
            print(f"   {hospital}: {count} localities")
        
        return df, csv_filename
        
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        return None, None

def validate_data(df):
    """
    Validate the extracted data
    """
    print("\n🔍 Data Validation:")
    print("-" * 40)
    
    # Check for empty values
    empty_localities = df[df['locality'].isna() | (df['locality'] == '')]
    empty_hospitals = df[df['orgname'].isna() | (df['orgname'] == '')]
    
    print(f"   Empty localities: {len(empty_localities)}")
    print(f"   Empty hospitals: {len(empty_hospitals)}")
    
    # Check for duplicates
    duplicates = df.duplicated(subset=['locality', 'orgname']).sum()
    print(f"   Duplicate combinations: {duplicates}")
    
    # Check data types
    print(f"   Data types:")
    print(f"     - locality: {df['locality'].dtype}")
    print(f"     - orgname: {df['orgname'].dtype}")
    
    return len(empty_localities) == 0 and len(empty_hospitals) == 0 and duplicates == 0

def main():
    """Main function"""
    print("🚀 Hospital Localities Extraction Tool")
    print("=" * 60)
    
    # Extract data
    df, csv_filename = extract_hospital_localities()
    
    if df is not None:
        # Validate data
        is_valid = validate_data(df)
        
        if is_valid:
            print(f"\n✅ Data extraction completed successfully!")
            print(f"📁 CSV file: {csv_filename}")
            print(f"📊 Total records: {len(df)}")
            
            # Show file size
            file_size = os.path.getsize(csv_filename)
            print(f"💾 File size: {file_size / 1024:.2f} KB")
            
        else:
            print(f"\n⚠️  Data validation failed. Please check the data.")
    else:
        print(f"\n❌ Failed to extract data.")

if __name__ == "__main__":
    main() 