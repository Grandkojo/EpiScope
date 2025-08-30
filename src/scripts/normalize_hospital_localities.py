#!/usr/bin/env python3
"""
Data Normalization Script for Hospital Localities
Cleans up locality names by:
- Removing extra descriptions and details
- Standardizing spelling variations
- Normalizing formatting (spaces, punctuation)
- Grouping similar localities
"""

import pandas as pd
import re
import json
from collections import defaultdict
import os

def normalize_locality_name(locality):
    """
    Normalize locality names by cleaning formatting and removing extra details
    """
    if pd.isna(locality) or locality == '':
        return ''
    
    # Convert to string and strip whitespace
    locality = str(locality).strip()
    
    # Remove newlines and extra whitespace
    locality = re.sub(r'\s+', ' ', locality)
    locality = re.sub(r'\n+', ' ', locality)
    
    # Remove common extra descriptions and details
    patterns_to_remove = [
        r'\s*NEAR\s+THE\s+.*$',  # Remove "NEAR THE..." descriptions
        r'\s*CQ\s+\d+.*$',       # Remove "CQ 16" type codes
        r'\s*ESTATE.*$',          # Remove "ESTATE" suffix
        r'\s*JUNCTION.*$',        # Remove "JUNCTION" suffix
        r'\s*CHURCH.*$',          # Remove "CHURCH" suffix
        r'\s*FIRST\s+LIGHT.*$',   # Remove "FIRST LIGHT" suffix
        r'\s*PRAYER\s+CAMP.*$',   # Remove "PRAYER CAMP" suffix
        r'\s*ACADAMY.*$',         # Remove "ACADAMY" suffix (misspelled)
        r'\s*ACADEMY.*$',         # Remove "ACADEMY" suffix
        r'\s*ROYAL.*$',           # Remove "ROYAL" suffix
        r'\s*CANADA.*$',          # Remove "CANADA" suffix
        r'\s*GALILEA.*$',         # Remove "GALILEA" suffix
        r'\s*PALADAS.*$',         # Remove "PALADAS" suffix
        r'\s*ANTIE\s+AKU.*$',     # Remove "ANTIE AKU" suffix
        r'\s*MASALACHI.*$',       # Remove "MASALACHI" suffix
    ]
    
    for pattern in patterns_to_remove:
        locality = re.sub(pattern, '', locality, flags=re.IGNORECASE)
    
    # Clean up punctuation and spacing
    locality = re.sub(r'\s*[,\-]\s*', ' ', locality)  # Replace commas and hyphens with spaces
    locality = re.sub(r'\s+', ' ', locality)  # Normalize multiple spaces
    locality = locality.strip()
    
    # Standardize common spelling variations
    spelling_fixes = {
        'ABLEKUMAH': 'ABLEKUMA',
        'ABLEKUMAN': 'ABLEKUMA',
        'FUN MILK': 'FAN MILK',
        'FUNMILK': 'FAN MILK',
        'FANMILK': 'FAN MILK',
        'OLABU': 'OLEBU',
        'VURVE': 'CURVE',
        'ODUMA': 'ODUMASE',
        'MANHIA': 'MANHEAN',
        'JOMA': 'GOMA',
        'NIC': 'NSAKINA',
        'CP': 'CURVE',
        'ABASE': 'ABEASE',
        'ACADAMY': 'ACADEMY',
        'ODUMASE': 'ODUMASE',  # Keep as is
    }
    
    # Apply spelling fixes
    for wrong, correct in spelling_fixes.items():
        if locality.upper() == wrong:
            locality = correct
        elif locality.upper().startswith(wrong + ' '):
            locality = correct + locality[len(wrong):]
    
    return locality

def create_locality_mapping():
    """
    Create a mapping of original localities to normalized names
    """
    # Read the original CSV
    csv_path = 'src/artifacts/csv/hospital_localities.csv'
    if not os.path.exists(csv_path):
        csv_path = 'hospital_localities.csv'
    
    df = pd.read_csv(csv_path)
    
    # Create mapping
    mapping = {}
    normalized_counts = defaultdict(int)
    
    print("🔍 Analyzing locality names for normalization...")
    print("=" * 60)
    
    for idx, row in df.iterrows():
        original = str(row['locality']).strip()
        normalized = normalize_locality_name(original)
        
        if original != normalized:
            mapping[original] = normalized
            normalized_counts[normalized] += 1
    
    # Show normalization statistics
    print(f"📊 Normalization Statistics:")
    print(f"   Total original localities: {len(df)}")
    print(f"   Unique original localities: {df['locality'].nunique()}")
    print(f"   Normalizations needed: {len(mapping)}")
    print(f"   Unique normalized localities: {len(set(mapping.values()))}")
    
    # Show top normalizations
    print(f"\n🔄 Top Normalizations:")
    normalized_groups = defaultdict(list)
    for original, normalized in mapping.items():
        normalized_groups[normalized].append(original)
    
    for normalized, originals in sorted(normalized_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"   '{normalized}' ← {len(originals)} variations:")
        for original in originals[:3]:  # Show first 3
            print(f"     • {original}")
        if len(originals) > 3:
            print(f"     • ... and {len(originals) - 3} more")
    
    return mapping, df

def apply_normalization_and_save():
    """
    Apply normalization and save cleaned data
    """
    mapping, df = create_locality_mapping()
    
    print(f"\n🧹 Applying normalizations...")
    
    # Apply normalization
    df['normalized_locality'] = df['locality'].apply(normalize_locality_name)
    
    # Remove duplicates based on normalized locality and orgname
    df_cleaned = df.drop_duplicates(subset=['normalized_locality', 'orgname'])
    
    # Sort by normalized locality and orgname
    df_cleaned = df_cleaned.sort_values(['normalized_locality', 'orgname']).reset_index(drop=True)
    
    # Update ID column
    df_cleaned['id'] = range(1, len(df_cleaned) + 1)
    
    # Save normalized data
    output_file = 'hospital_localities_normalized.csv'
    df_cleaned.to_csv(output_file, index=False)
    
    # Save mapping for reference
    mapping_file = 'locality_normalization_mapping.json'
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n✅ Normalization completed!")
    print(f"📁 Files created:")
    print(f"   • {output_file} - Cleaned data")
    print(f"   • {mapping_file} - Normalization mapping")
    
    # Show results
    print(f"\n📈 Results:")
    print(f"   Original records: {len(df)}")
    print(f"   After normalization: {len(df_cleaned)}")
    print(f"   Duplicates removed: {len(df) - len(df_cleaned)}")
    print(f"   Reduction: {((len(df) - len(df_cleaned)) / len(df) * 100):.1f}%")
    
    # Show sample of cleaned data
    print(f"\n📊 Sample Cleaned Data:")
    print("-" * 60)
    sample_data = df_cleaned[['id', 'normalized_locality', 'orgname']].head(15)
    for _, row in sample_data.iterrows():
        print(f"   {row['id']:3d}. {row['normalized_locality']:<30} | {row['orgname']}")
    
    # Show statistics by hospital
    print(f"\n🏥 Statistics by Hospital:")
    hospital_stats = df_cleaned.groupby('orgname').agg({
        'normalized_locality': ['count', 'nunique']
    }).round(0)
    hospital_stats.columns = ['Total Combinations', 'Unique Localities']
    print(hospital_stats)
    
    return df_cleaned, mapping

def create_normalization_report():
    """
    Create a detailed report of the normalization process
    """
    df_cleaned, mapping = apply_normalization_and_save()
    
    print(f"\n📋 Normalization Report")
    print("=" * 60)
    
    # Most common normalizations
    print(f"\n🔄 Most Common Normalizations:")
    normalization_counts = defaultdict(int)
    for original, normalized in mapping.items():
        normalization_counts[normalized] += 1
    
    for normalized, count in sorted(normalization_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   '{normalized}' ← {count} variations")
    
    # Show examples of each major normalization
    print(f"\n📝 Examples of Major Normalizations:")
    for normalized, count in sorted(normalization_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        if count > 1:
            originals = [orig for orig, norm in mapping.items() if norm == normalized]
            print(f"\n   '{normalized}' ({count} variations):")
            for original in originals[:5]:
                print(f"     • {original}")
            if len(originals) > 5:
                print(f"     • ... and {len(originals) - 5} more")
    
    return df_cleaned, mapping

def main():
    """Main function"""
    print("🚀 Hospital Localities Data Normalization")
    print("=" * 80)
    print("This script will clean up locality names by:")
    print("• Removing extra descriptions and details")
    print("• Standardizing spelling variations")
    print("• Normalizing formatting (spaces, punctuation)")
    print("• Grouping similar localities")
    print()
    
    try:
        df_cleaned, mapping = create_normalization_report()
        
        print(f"\n🎉 Normalization completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Original records: {len(pd.read_csv('src/artifacts/csv/hospital_localities.csv'))}")
        print(f"   • Cleaned records: {len(df_cleaned)}")
        print(f"   • Normalizations applied: {len(mapping)}")
        print(f"   • Files created: hospital_localities_normalized.csv, locality_normalization_mapping.json")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Review the normalized data in 'hospital_localities_normalized.csv'")
        print(f"   2. Use the normalized CSV for seeding: python manage.py seed_hospital_localities --csv-file hospital_localities_normalized.csv")
        print(f"   3. Check the mapping file 'locality_normalization_mapping.json' for reference")
        
    except Exception as e:
        print(f"❌ Error during normalization: {e}")
        raise

if __name__ == "__main__":
    main() 