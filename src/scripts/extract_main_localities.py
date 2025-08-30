#!/usr/bin/env python3
"""
Extract Main Localities Script
Extracts main locality names from merged data and creates a clean CSV
"""

import pandas as pd
import re
import json
from collections import Counter

def extract_main_locality(locality_name):
    """Extract main locality name from variations"""
    if not locality_name or pd.isna(locality_name):
        return None
    
    locality_str = str(locality_name).strip().upper()
    
    # Remove quotes and extra spaces
    locality_str = re.sub(r'["\']', '', locality_str)
    locality_str = re.sub(r'\s+', ' ', locality_str)
    
    # Common patterns to extract main locality
    patterns = [
        r'^([A-Z]+)',  # Start with uppercase letters (ABLEKUMA, ABEKA, etc.)
        r'^([A-Z]+)\s+',  # Main name followed by space
        r'^([A-Z]+)[\-\s]',  # Main name followed by dash or space
        r'^([A-Z]+),',  # Main name followed by comma
    ]
    
    for pattern in patterns:
        match = re.match(pattern, locality_str)
        if match:
            main_name = match.group(1)
            # Filter out very short names and common words
            if len(main_name) >= 3 and main_name not in ['THE', 'AND', 'FOR', 'NEW', 'OLD']:
                return main_name
    
    return None

def analyze_localities():
    """Analyze localities in the merged data"""
    print("Loading merged data...")
    
    # Load merged data
    diabetes_path = 'src/artifacts/merged_data/weija_diabetes_merged.csv'
    malaria_path = 'src/artifacts/merged_data/weija_malaria_merged.csv'
    
    diabetes_df = pd.read_csv(diabetes_path)
    malaria_df = pd.read_csv(malaria_path)
    
    # Combine datasets
    combined_df = pd.concat([diabetes_df, malaria_df], ignore_index=True)
    
    print(f"Total records: {len(combined_df)}")
    
    # Extract all unique localities
    all_localities = combined_df['Locality'].dropna().unique()
    print(f"Unique localities found: {len(all_localities)}")
    
    # Extract main localities
    main_localities = []
    locality_mapping = {}
    
    for locality in all_localities:
        main_locality = extract_main_locality(locality)
        if main_locality:
            main_localities.append(main_locality)
            locality_mapping[locality] = main_locality
    
    # Count occurrences
    locality_counts = Counter(main_localities)
    
    print(f"\nMain localities found: {len(locality_counts)}")
    print("\nTop 20 main localities:")
    for locality, count in locality_counts.most_common(20):
        print(f"  {locality}: {count} records")
    
    # Create clean CSV with main localities
    main_localities_df = pd.DataFrame([
        {'locality': locality, 'orgname': 'weija', 'count': count}
        for locality, count in locality_counts.items()
    ])
    
    # Sort by count (most frequent first)
    main_localities_df = main_localities_df.sort_values('count', ascending=False)
    
    # Save to CSV
    output_file = 'main_localities.csv'
    main_localities_df.to_csv(output_file, index=False)
    print(f"\nSaved main localities to: {output_file}")
    
    # Save mapping for reference
    mapping_file = 'locality_to_main_mapping.json'
    with open(mapping_file, 'w') as f:
        json.dump(locality_mapping, f, indent=2)
    print(f"Saved locality mapping to: {mapping_file}")
    
    return main_localities_df, locality_mapping

def create_clean_localities_csv():
    """Create a clean CSV with just the main localities for database insertion"""
    main_localities_df, _ = analyze_localities()
    
    # Create clean CSV for database insertion
    clean_localities = main_localities_df[['locality', 'orgname']].copy()
    clean_localities['created_at'] = pd.Timestamp.now()
    clean_localities['updated_at'] = pd.Timestamp.now()
    
    output_file = 'clean_localities_for_db.csv'
    clean_localities.to_csv(output_file, index=False)
    print(f"\nCreated clean localities CSV for database: {output_file}")
    print(f"Total main localities: {len(clean_localities)}")
    
    return clean_localities

if __name__ == "__main__":
    print("Extracting main localities from merged data...")
    clean_localities = create_clean_localities_csv()
    
    print("\nSample of clean localities:")
    print(clean_localities.head(10).to_string(index=False)) 