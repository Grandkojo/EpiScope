#!/usr/bin/env python3
"""
Convert Excel files to CSV format
This script converts Excel files from the src/artifacts/excel directory to CSV format
"""

import pandas as pd
import os
import glob
from pathlib import Path

def convert_excel_to_csv(input_file, output_file=None):
    """
    Convert a single Excel file to CSV
    
    Args:
        input_file (str): Path to the Excel file
        output_file (str): Path for the output CSV file (optional)
    """
    try:
        print(f"📖 Reading Excel file: {input_file}")
        
        # Read Excel file
        df = pd.read_excel(input_file)
        
        # Clean the data
        # Remove unnamed columns
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col) or str(col).strip() == '']
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
            print(f"   🗑️ Dropped {len(unnamed_cols)} unnamed columns")
        
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
        # Generate output filename if not provided
        if output_file is None:
            input_path = Path(input_file)
            output_file = input_path.with_suffix('.csv')
        
        # Save as CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"✅ Converted: {input_file} -> {output_file}")
        print(f"📊 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error converting {input_file}: {str(e)}")
        return None

def convert_diabetes_2024_files():
    """Convert all diabetes 2024 Excel files to CSV"""
    print("🚀 Converting diabetes 2024 Excel files to CSV...")
    
    # Path to diabetes 2024 files
    diabetes_path = "src/artifacts/excel/diabetes/weija"
    
    # Find all 2024 diabetes Excel files
    pattern = os.path.join(diabetes_path, "diabetes_2024_*.xlsx")
    excel_files = glob.glob(pattern)
    
    if not excel_files:
        print(f"❌ No diabetes 2024 Excel files found in {diabetes_path}")
        return
    
    print(f"📁 Found {len(excel_files)} diabetes 2024 Excel files")
    
    # Create output directory
    output_dir = "src/artifacts/csv/diabetes_2024"
    os.makedirs(output_dir, exist_ok=True)
    
    converted_files = []
    
    for excel_file in sorted(excel_files):
        # Generate output filename
        filename = os.path.basename(excel_file)
        csv_filename = filename.replace('.xlsx', '.csv')
        output_file = os.path.join(output_dir, csv_filename)
        
        # Convert file
        result = convert_excel_to_csv(excel_file, output_file)
        if result:
            converted_files.append(result)
    
    print(f"\n🎉 Conversion completed!")
    print(f"✅ Successfully converted {len(converted_files)} files")
    print(f"📁 Output directory: {output_dir}")
    
    return converted_files

def convert_specific_file(input_file, output_file=None):
    """Convert a specific Excel file to CSV"""
    print(f"🚀 Converting specific file: {input_file}")
    
    result = convert_excel_to_csv(input_file, output_file)
    
    if result:
        print(f"✅ Successfully converted: {result}")
    else:
        print(f"❌ Failed to convert: {input_file}")
    
    return result

def convert_all_excel_files():
    """Convert all Excel files in the artifacts directory"""
    print("🚀 Converting all Excel files to CSV...")
    
    # Find all Excel files
    excel_patterns = [
        "src/artifacts/excel/**/*.xlsx",
        "src/artifacts/excel/**/*.xls"
    ]
    
    excel_files = []
    for pattern in excel_patterns:
        excel_files.extend(glob.glob(pattern, recursive=True))
    
    if not excel_files:
        print("❌ No Excel files found")
        return
    
    print(f"📁 Found {len(excel_files)} Excel files")
    
    converted_files = []
    
    for excel_file in sorted(excel_files):
        # Generate output filename
        input_path = Path(excel_file)
        output_file = input_path.with_suffix('.csv')
        
        # Convert file
        result = convert_excel_to_csv(excel_file, output_file)
        if result:
            converted_files.append(result)
    
    print(f"\n🎉 Conversion completed!")
    print(f"✅ Successfully converted {len(converted_files)} files")
    
    return converted_files

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Convert specific file
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        convert_specific_file(input_file, output_file)
    else:
        # Convert diabetes 2024 files by default
        print("Converting diabetes 2024 Excel files to CSV...")
        convert_diabetes_2024_files()
        
        # Ask if user wants to convert all Excel files
        response = input("\nDo you want to convert all Excel files in the artifacts directory? (y/n): ")
        if response.lower() in ['y', 'yes']:
            convert_all_excel_files() 