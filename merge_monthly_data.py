import pandas as pd
import os
from pathlib import Path
import glob
import argparse

def merge_monthly_data(disease_type, input_folder, output_file, org_name):
    """
    Merge all monthly CSV files for a specific disease into a single CSV file
    
    Args:
        disease_type (str): 'diabetes' or 'malaria'
        input_folder (str): Path to the folder containing monthly CSV files
        output_file (str): Path for the output merged CSV file
        org_name (str): Organization name to add to each row
    """
    
    # Get all CSV files in the folder
    csv_files = glob.glob(os.path.join(input_folder, f"{disease_type}_*.csv"))
    
    if not csv_files:
        print(f"❌ No CSV files found in {input_folder}")
        return
    
    print(f"📁 Found {len(csv_files)} CSV files for {disease_type}")
    
    # Sort files by name to ensure consistent ordering
    csv_files.sort()
    
    # List to store all dataframes
    all_dataframes = []
    total_rows = 0
    
    # Read each CSV file
    for file_path in csv_files:
        try:
            # Extract month and year from filename
            filename = os.path.basename(file_path)
            print(f"📖 Reading: {filename}")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Drop unnamed columns (empty column names)
            unnamed_cols = [col for col in df.columns if 'Unnamed' in col or col.strip() == '']
            if unnamed_cols:
                df = df.drop(columns=unnamed_cols)
                print(f"   🗑️ Dropped {len(unnamed_cols)} unnamed columns")
            
            # Add organization name and disease type
            df['orgname'] = org_name
            df['disease_type'] = disease_type
            
            # Add to list
            all_dataframes.append(df)
            total_rows += len(df)
            
            print(f"   ✅ {len(df)} rows loaded")
            
        except Exception as e:
            print(f"   ❌ Error reading {file_path}: {str(e)}")
    
    if not all_dataframes:
        print(f"❌ No valid CSV files could be read for {disease_type}")
        return
    
    # Concatenate all dataframes
    print(f"🔄 Merging {len(all_dataframes)} files...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Sort by date if available
    if 'Schedule Date' in merged_df.columns:
        try:
            merged_df['Schedule Date'] = pd.to_datetime(merged_df['Schedule Date'], format='%d-%m-%Y', errors='coerce')
            merged_df = merged_df.sort_values('Schedule Date')
            print("📅 Data sorted by date")
        except Exception as e:
            print(f"⚠️ Could not sort by date: {str(e)}")
    
    # Save merged data
    print(f"💾 Saving merged data to {output_file}")
    merged_df.to_csv(output_file, index=False)
    
    print(f"✅ Successfully merged {disease_type} data!")
    print(f"📊 Total rows: {len(merged_df)}")
    print(f"📋 Columns: {list(merged_df.columns)}")
    print(f"📁 Output file: {output_file}")
    
    # Print summary statistics
    print(f"\n📈 Summary for {disease_type}:")
    print(f"   - Total files processed: {len(csv_files)}")
    print(f"   - Total records: {len(merged_df)}")
    print(f"   - Organization: {org_name}")
    
    if 'Schedule Date' in merged_df.columns:
        date_range = merged_df['Schedule Date'].dropna()
        if len(date_range) > 0:
            print(f"   - Date range: {date_range.min().strftime('%Y-%m-%d')} to {date_range.max().strftime('%Y-%m-%d')}")
    
    if 'Locality' in merged_df.columns:
        unique_localities = merged_df['Locality'].nunique()
        print(f"   - Unique localities: {unique_localities}")
    
    if 'Gender' in merged_df.columns:
        gender_counts = merged_df['Gender'].value_counts()
        print(f"   - Gender distribution:")
        for gender, count in gender_counts.items():
            print(f"     {gender}: {count}")
    
    return merged_df

def main():
    """Main function to merge both diabetes and malaria data"""
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Merge monthly CSV files for diabetes and malaria data')
    parser.add_argument('--org-name', '-o', type=str, default='Weija Hospital',
                       help='Organization name to add to each row (default: Weija Hospital)')
    parser.add_argument('--output-dir', '-d', type=str, default='src/artifacts/merged_data',
                       help='Output directory for merged files (default: src/artifacts/merged_data)')
    
    args = parser.parse_args()
    
    # Define paths
    base_path = "src/artifacts/csv"
    diabetes_folder = os.path.join(base_path, "diabetes/weija")
    malaria_folder = os.path.join(base_path, "malaria/weija")
    
    # Organization name from command line argument
    org_name = args.org_name
    
    # Create output directory if it doesn't exist
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    print("🚀 Starting monthly data merge process...")
    print(f"🏥 Organization: {org_name}")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 50)
    
    # Merge diabetes data
    print("\n🩺 Processing DIABETES data...")
    diabetes_output = os.path.join(output_dir, "weija_diabetes_merged.csv")
    diabetes_df = merge_monthly_data("diabetes", diabetes_folder, diabetes_output, org_name)
    
    print("\n" + "=" * 50)
    
    # Merge malaria data
    print("\n🦟 Processing MALARIA data...")
    malaria_output = os.path.join(output_dir, "weija_malaria_merged.csv")
    malaria_df = merge_monthly_data("malaria", malaria_folder, malaria_output, org_name)
    
    print("\n" + "=" * 50)
    
    # Final summary
    print("\n🎉 MERGE COMPLETE!")
    print("=" * 50)
    
    if diabetes_df is not None:
        print(f"📁 Diabetes file: {diabetes_output}")
        print(f"   Records: {len(diabetes_df)}")
    
    if malaria_df is not None:
        print(f"📁 Malaria file: {malaria_output}")
        print(f"   Records: {len(malaria_df)}")
    
    # Create a combined file with both diseases
    if diabetes_df is not None and malaria_df is not None:
        print(f"\n🔄 Creating combined file...")
        combined_df = pd.concat([diabetes_df, malaria_df], ignore_index=True)
        combined_output = os.path.join(output_dir, "weija_combined_diseases.csv")
        combined_df.to_csv(combined_output, index=False)
        print(f"📁 Combined file: {combined_output}")
        print(f"   Total records: {len(combined_df)}")
    
    print(f"\n✅ All files saved to: {output_dir}")

if __name__ == "__main__":
    main() 