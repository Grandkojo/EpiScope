import pandas as pd
import re

def fix_csv_for_rag(input_file, output_file):
    """Fix CSV file for Vertex AI RAG compatibility"""
    
    # Read CSV with proper encoding
    df = pd.read_csv(input_file, encoding='utf-8')
    
    # Clean column names - remove special characters
    df.columns = [re.sub(r'[^\w\s]', '', col).strip().replace(' ', '_') for col in df.columns]
    
    # Clean text data - remove line breaks and extra spaces
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).apply(lambda x: re.sub(r'\n+', ' ', x).strip())
        df[col] = df[col].apply(lambda x: re.sub(r'\s+', ' ', x))  # Remove extra spaces
    
    # Remove rows with all NaN values
    df = df.dropna(how='all')
    
    # Save as clean CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ Fixed {input_file} -> {output_file}")
    print(f"📊 Shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")

# Fix your files
fix_csv_for_rag(
    'src/artifacts/time_series/health_data_eams_malaria_time_stamped.csv',
    'src/artifacts/rag/cleaned_malaria_data.csv'
)

fix_csv_for_rag(
    'src/artifacts/csv/national_hotspots.csv',
    'src/artifacts/rag/cleaned_hotspots_data.csv'
)