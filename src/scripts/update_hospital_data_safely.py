#!/usr/bin/env python3
"""
Safe Database Update Script for Hospital Health Data
Updates disease_monitor_hospitalhealthdata with new merged data while preserving existing data
"""

import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime
import hashlib
import logging
import re

# Setup Django
sys.path.append('/home/grandkojo/Documents/GITHUB/EpiScope')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import HospitalHealthData, HospitalLocalities
from django.db import connection, transaction
from django.core.management import execute_from_command_line

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_age_numeric(age_input):
    """Extract numeric age from various formats"""
    if pd.isna(age_input) or age_input == '':
        return None
    
    # If already numeric, return as is
    if isinstance(age_input, (int, float)):
        return int(age_input)
    
    # If string, try to extract numeric value
    age_str = str(age_input)
    numbers = re.findall(r'\d+', age_str)
    if numbers:
        return int(numbers[0])
    
    return None

def create_backup_tables():
    """Create backup tables before making changes"""
    logger.info("Creating backup tables...")
    
    with connection.cursor() as cursor:
        # Backup main table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disease_monitor_hospitalhealthdata_backup AS 
            SELECT * FROM disease_monitor_hospitalhealthdata
        """)
        
        # Backup localities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospital_localities_backup AS 
            SELECT * FROM hospital_localities
        """)
        
        # Get record counts
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata_backup")
        main_backup_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hospital_localities_backup")
        localities_backup_count = cursor.fetchone()[0]
        
        logger.info(f"Backup created: {main_backup_count} health records, {localities_backup_count} localities")

def add_new_columns():
    """Add new columns to the database table"""
    logger.info("Adding new columns to database table...")
    
    with connection.cursor() as cursor:
        # Add new columns if they don't exist
        columns_to_add = [
            ("data_source", "VARCHAR(20) DEFAULT 'legacy'"),
            ("medicine_prescribed", "TEXT"),
            ("cost_of_treatment", "DECIMAL(10,2)"),
            ("schedule_date", "DATE"),
            ("locality_encoded", "INTEGER")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE disease_monitor_hospitalhealthdata ADD COLUMN {column_name} {column_type}")
                logger.info(f"Added column: {column_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Column {column_name} already exists")
                else:
                    logger.warning(f"Could not add column {column_name}: {e}")

def transform_merged_data():
    """Transform merged CSV data to match existing database structure"""
    logger.info("Loading and transforming merged data...")
    
    # Load merged data
    diabetes_path = 'src/artifacts/merged_data/weija_diabetes_merged.csv'
    malaria_path = 'src/artifacts/merged_data/weija_malaria_merged.csv'
    
    if not os.path.exists(diabetes_path) or not os.path.exists(malaria_path):
        raise FileNotFoundError("Merged data files not found")
    
    diabetes_df = pd.read_csv(diabetes_path)
    malaria_df = pd.read_csv(malaria_path)
    
    logger.info(f"Loaded diabetes data: {len(diabetes_df)} records")
    logger.info(f"Loaded malaria data: {len(malaria_df)} records")
    
    # Combine datasets
    combined_df = pd.concat([diabetes_df, malaria_df], ignore_index=True)
    logger.info(f"Combined data: {len(combined_df)} records")
    
    # Transform data
    transformed_records = []
    
    for idx, row in combined_df.iterrows():
        try:
            # Extract age
            age = extract_age_numeric(row['Age'])
            if age is None:
                logger.warning(f"Skipping record {idx}: Invalid age - {row['Age']}")
                continue
            
            # Transform gender
            gender = row['Gender'].strip() if pd.notna(row['Gender']) else 'Unknown'
            sex = 'Male' if gender.lower() == 'male' else 'Female'
            
            # Transform boolean fields
            pregnant_patient = str(row['Pregnant Patient']).lower() == 'yes' if pd.notna(row['Pregnant Patient']) else False
            nhia_patient = str(row['NHIA Patient']).lower() == 'insured' if pd.notna(row['NHIA Patient']) else False
            
            # Transform date
            try:
                schedule_date = pd.to_datetime(row['Schedule Date'])
                month = schedule_date
            except:
                logger.warning(f"Skipping record {idx}: Invalid date - {row['Schedule Date']}")
                continue
            
            # Transform cost
            cost_of_treatment = None
            if pd.notna(row['Cost of Treatment (GHS )']):
                try:
                    cost_of_treatment = float(row['Cost of Treatment (GHS )'])
                except:
                    cost_of_treatment = None
            
            # Create record
            record = {
                'orgname': row['orgname'] if pd.notna(row['orgname']) else 'Weija',
                'address_locality': row['Locality'] if pd.notna(row['Locality']) else 'Unknown',
                'age': age,
                'sex': sex,
                'principal_diagnosis_new': row['Principal Diagnosis'] if pd.notna(row['Principal Diagnosis']) else '',
                'additional_diagnosis_new': row['Additional Diagnosis'] if pd.notna(row['Additional Diagnosis']) else '',
                'pregnant_patient': pregnant_patient,
                'nhia_patient': nhia_patient,
                'month': month,
                
                # New columns
                'data_source': 'merged_2024',
                'medicine_prescribed': row['Medicine Prescribed'] if pd.notna(row['Medicine Prescribed']) else '',
                'cost_of_treatment': cost_of_treatment,
                'schedule_date': schedule_date,
                'locality_encoded': hash(str(row['Locality'])) % 100 if pd.notna(row['Locality']) else 0
            }
            
            transformed_records.append(record)
            
        except Exception as e:
            logger.error(f"Error processing record {idx}: {e}")
            continue
    
    logger.info(f"Successfully transformed {len(transformed_records)} records")
    return transformed_records

def insert_transformed_data(transformed_records):
    """Insert transformed data into the database"""
    logger.info("Inserting transformed data into database...")
    
    # Use bulk_create for better performance
    batch_size = 1000
    total_inserted = 0
    
    for i in range(0, len(transformed_records), batch_size):
        batch = transformed_records[i:i + batch_size]
        
        # Create HospitalHealthData objects
        health_data_objects = []
        for record in batch:
            health_data_objects.append(HospitalHealthData(**record))
        
        # Bulk insert
        try:
            HospitalHealthData.objects.bulk_create(health_data_objects, ignore_conflicts=True)
            total_inserted += len(health_data_objects)
            logger.info(f"Inserted batch {i//batch_size + 1}: {len(health_data_objects)} records")
        except Exception as e:
            logger.error(f"Error inserting batch {i//batch_size + 1}: {e}")
    
    logger.info(f"Total records inserted: {total_inserted}")
    return total_inserted

def update_locality_mappings():
    """Update hospital_localities table with new locality data"""
    logger.info("Updating locality mappings...")
    
    # Get unique locality-orgname combinations from new data
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT address_locality, orgname 
            FROM disease_monitor_hospitalhealthdata 
            WHERE data_source = 'merged_2024'
        """)
        new_localities = cursor.fetchall()
    
    # Add new localities to the table
    localities_created = 0
    for locality, orgname in new_localities:
        try:
            HospitalLocalities.objects.get_or_create(
                locality=locality,
                orgname=orgname
            )
            localities_created += 1
        except Exception as e:
            logger.warning(f"Could not create locality {locality}: {e}")
    
    logger.info(f"Created {localities_created} new locality mappings")

def verify_analytics_compatibility():
    """Verify that analytics endpoints still work"""
    logger.info("Verifying analytics compatibility...")
    
    # Test basic queries
    with connection.cursor() as cursor:
        # Test total count
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
        total_count = cursor.fetchone()[0]
        logger.info(f"Total records in database: {total_count}")
        
        # Test by data source
        cursor.execute("SELECT data_source, COUNT(*) FROM disease_monitor_hospitalhealthdata GROUP BY data_source")
        source_counts = cursor.fetchall()
        for source, count in source_counts:
            logger.info(f"Records from {source}: {count}")
        
        # Test locality count
        cursor.execute("SELECT COUNT(DISTINCT address_locality) FROM disease_monitor_hospitalhealthdata")
        locality_count = cursor.fetchone()[0]
        logger.info(f"Unique localities: {locality_count}")
        
        # Test orgname count
        cursor.execute("SELECT COUNT(DISTINCT orgname) FROM disease_monitor_hospitalhealthdata")
        orgname_count = cursor.fetchone()[0]
        logger.info(f"Unique orgnames: {orgname_count}")

def main():
    """Main update process"""
    logger.info("Starting safe database update process...")
    
    try:
        # Step 1: Create backups
        create_backup_tables()
        
        # Step 2: Add new columns
        add_new_columns()
        
        # Step 3: Transform data
        transformed_records = transform_merged_data()
        
        # Step 4: Insert data
        if transformed_records:
            insert_transformed_data(transformed_records)
        
        # Step 5: Update locality mappings
        update_locality_mappings()
        
        # Step 6: Verify compatibility
        verify_analytics_compatibility()
        
        logger.info("Database update completed successfully!")
        
    except Exception as e:
        logger.error(f"Database update failed: {e}")
        logger.error("Please check the backup tables and restore if necessary")
        raise

if __name__ == "__main__":
    main() 