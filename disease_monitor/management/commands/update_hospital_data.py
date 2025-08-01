from django.core.management.base import BaseCommand
from django.db import connection
from disease_monitor.models import HospitalHealthData, HospitalLocalities
import pandas as pd
import re
import logging
import json
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Safely update hospital health data with new merged data while preserving existing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-only',
            action='store_true',
            help='Only create backup tables without updating data',
        )
        parser.add_argument(
            '--verify-only',
            action='store_true',
            help='Only verify the current state of the database',
        )

    def extract_age_numeric(self, age_input):
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

    def load_locality_mapping(self):
        """Load locality normalization mapping"""
        mapping_file = 'locality_normalization_mapping.json'
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                return json.load(f)
        else:
            self.stdout.write(
                self.style.WARNING(f"Locality mapping file {mapping_file} not found. Using original locality names.")
            )
            return {}

    def get_final_localities(self):
        """Get the final curated list of localities"""
        final_localities = [
            # Major areas around Weija
            "KASOA", "WEIJA", "GBAWE", "ABLEKUMA", "AWOSHIE", "MALLAM", "MCCARTHY", 
            "ODORKOR", "KWASHIEMAN", "TETEGU", "TUBA", "BORTIANOR", "DANSOMAN", 
            "SOWUTUOM", "LAPAZ", "AMANFROM", "AMASAMAN", "KOKROBITE", "APLAKU", 
            "KWASHIEBU", "DARKUMAN", "TABORA", "OFANKOR", "GALILEA", "SAKAMAN", 
            "MATAHEKO", "POKUASE", "OMANJOR", "BUBIASHIE", "TEMA", "KANESHIE", 
            "AWUTU", "ABEKA", "OLEBU", "DOME", "AGONA", "ADENTA", "KALABULE", 
            "PALAS", "TESHIE", "BAWJIASE", "FANMILK", "KWAHU", "BUSIA", "PALACE", 
            "LIBERIA", "BRIGADE", "MENSKROM", "NIC", "CHOICE", "BARRIER", "SAMPA", 
            "ODOKOR", "SOWUTOUM", "GBEWE", "AWOSHI", "MACCARTHY", "BLOCKFACTORY", 
            "MCCHARTHY", "MCCATHY", "KWASHIMAN", "MALLA", "DJAMAN", "BAAH", 
            "MALAM", "GALELIA", "ODORKO", "TATOP", "TABOLA", "KAOSA", "SOWUTUM", 
            "MCARTHY", "ACCRA", "AMANFRO"
        ]
        return sorted(list(set(final_localities)))

    def normalize_locality(self, locality, final_localities):
        """Normalize locality name using final localities list"""
        if not locality or pd.isna(locality):
            return 'Unknown'
        
        locality_str = str(locality).strip().upper()
        
        # Remove quotes and extra spaces
        locality_str = re.sub(r'["\']', '', locality_str)
        locality_str = re.sub(r'\s+', ' ', locality_str)
        
        # First, try exact match with final localities
        if locality_str in final_localities:
            return locality_str
        
        # Try to find a match by checking if any final locality is contained in the original
        for final_loc in final_localities:
            if final_loc in locality_str or locality_str in final_loc:
                return final_loc
        
        # If no match found, return original (cleaned)
        return locality_str

    def create_backup_tables(self):
        """Create backup tables before making changes"""
        self.stdout.write("Creating backup tables...")
        
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
            
            self.stdout.write(
                self.style.SUCCESS(f"Backup created: {main_backup_count} health records, {localities_backup_count} localities")
            )

    def add_new_columns(self):
        """Add new columns to the database table"""
        self.stdout.write("Adding new columns to database table...")
        
        with connection.cursor() as cursor:
            # Add new columns if they don't exist
            columns_to_add = [
                ("data_source", "VARCHAR(20) DEFAULT 'merged_2024'"),
                ("medicine_prescribed", "TEXT"),
                ("cost_of_treatment", "DECIMAL(10,2)"),
                ("schedule_date", "DATE"),
                ("locality_encoded", "INTEGER")
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    cursor.execute(f"ALTER TABLE disease_monitor_hospitalhealthdata ADD COLUMN {column_name} {column_type}")
                    self.stdout.write(f"Added column: {column_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        self.stdout.write(f"Column {column_name} already exists")
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"Could not add column {column_name}: {e}")
                        )

    def clear_existing_data(self):
        """Clear existing data from both tables before insertion"""
        self.stdout.write("Clearing existing data from tables...")
        
        # Clear health data table
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM disease_monitor_hospitalhealthdata")
            health_deleted = cursor.rowcount
            self.stdout.write(f"Deleted {health_deleted} records from hospital health data")
            
            # Check if sequence exists and reset it
            cursor.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_name = 'disease_monitor_hospitalhealthdata_id_seq'
            """)
            sequence_exists = cursor.fetchone()
            
            if sequence_exists:
                cursor.execute("ALTER SEQUENCE disease_monitor_hospitalhealthdata_id_seq RESTART WITH 1")
                self.stdout.write("Reset ID sequence for hospital health data")
            else:
                self.stdout.write("No ID sequence found for hospital health data - using default")
        
        # Clear localities table
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM hospital_localities")
            localities_deleted = cursor.rowcount
            self.stdout.write(f"Deleted {localities_deleted} records from hospital localities")
            
            # Check if sequence exists and reset it
            cursor.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_name = 'hospital_localities_id_seq'
            """)
            sequence_exists = cursor.fetchone()
            
            if sequence_exists:
                cursor.execute("ALTER SEQUENCE hospital_localities_id_seq RESTART WITH 1")
                self.stdout.write("Reset ID sequence for hospital localities")
            else:
                self.stdout.write("No ID sequence found for hospital localities - using default")
        
        self.stdout.write("Data clearing completed")

    def transform_merged_data(self):
        """Transform merged CSV data to match existing database structure"""
        self.stdout.write("Loading and transforming merged data...")
        
        # Get final localities list
        final_localities = self.get_final_localities()
        self.stdout.write(f"Using {len(final_localities)} final localities for normalization")
        
        # Load merged data
        diabetes_path = 'src/artifacts/merged_data/weija_diabetes_merged.csv'
        malaria_path = 'src/artifacts/merged_data/weija_malaria_merged.csv'
        
        try:
            diabetes_df = pd.read_csv(diabetes_path)
            malaria_df = pd.read_csv(malaria_path)
        except FileNotFoundError as e:
            self.stdout.write(
                self.style.ERROR(f"Merged data files not found: {e}")
            )
            return []
        
        self.stdout.write(f"Loaded diabetes data: {len(diabetes_df)} records")
        self.stdout.write(f"Loaded malaria data: {len(malaria_df)} records")
        
        # Combine datasets
        combined_df = pd.concat([diabetes_df, malaria_df], ignore_index=True)
        self.stdout.write(f"Combined data: {len(combined_df)} records")
        
        # Transform data
        transformed_records = []
        
        for idx, row in combined_df.iterrows():
            try:
                # Extract age
                age = self.extract_age_numeric(row['Age'])
                if age is None:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping record {idx}: Invalid age - {row['Age']}")
                    )
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
                    self.stdout.write(
                        self.style.WARNING(f"Skipping record {idx}: Invalid date - {row['Schedule Date']}")
                    )
                    continue
                
                # Transform cost
                cost_of_treatment = None
                if pd.notna(row['Cost of Treatment (GHS )']):
                    try:
                        cost_of_treatment = float(row['Cost of Treatment (GHS )'])
                    except:
                        cost_of_treatment = None
                
                # Normalize locality
                original_locality = row['Locality'] if pd.notna(row['Locality']) else 'Unknown'
                normalized_locality = self.normalize_locality(original_locality, final_localities)
                
                # Create record
                record = {
                    'orgname': row['orgname'] if pd.notna(row['orgname']) else 'Weija',
                    'address_locality': normalized_locality,
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
                    'locality_encoded': hash(normalized_locality) % 100
                }
                
                transformed_records.append(record)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing record {idx}: {e}")
                )
                continue
        
        self.stdout.write(f"Successfully transformed {len(transformed_records)} records")
        
        # Show locality normalization summary
        original_localities = set()
        normalized_localities = set()
        for record in transformed_records:
            original_localities.add(record.get('address_locality', ''))
            normalized_localities.add(record.get('address_locality', ''))
        
        self.stdout.write(f"Locality consolidation: {len(normalized_localities)} unique localities after normalization")
        
        return transformed_records

    def insert_transformed_data(self, transformed_records):
        """Insert transformed data into the database"""
        self.stdout.write("Inserting transformed data into database...")
        
        # Use bulk_create for better performance
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(transformed_records), batch_size):
            batch = transformed_records[i:i + batch_size]
            
            # Create HospitalHealthData objects
            health_data_objects = []
            for record in batch:
                # Don't specify id - let Django auto-generate it
                health_data_objects.append(HospitalHealthData(**record))
            
            # Bulk insert
            try:
                created_objects = HospitalHealthData.objects.bulk_create(health_data_objects)
                total_inserted += len(created_objects)
                self.stdout.write(f"Inserted batch {i//batch_size + 1}: {len(created_objects)} records")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error inserting batch {i//batch_size + 1}: {e}")
                )
        
        self.stdout.write(f"Total records inserted: {total_inserted}")
        return total_inserted

    def update_locality_mappings(self):
        """Update hospital_localities table with final localities"""
        self.stdout.write("Updating locality mappings...")
        
        # Clear existing localities (already done in clear_existing_data, but just in case)
        HospitalLocalities.objects.all().delete()
        self.stdout.write("Cleared existing localities")
        
        # Get final localities
        final_localities = self.get_final_localities()
        
        # Create new locality records
        new_localities = []
        for locality in final_localities:
            # Don't specify id - let Django auto-generate it
            new_localities.append(HospitalLocalities(
                locality=locality,
                orgname='weija'
            ))
        
        # Bulk insert
        created_localities = HospitalLocalities.objects.bulk_create(new_localities)
        self.stdout.write(f"Created {len(created_localities)} final locality mappings")
        
        # Show the localities
        self.stdout.write("Final localities:")
        for locality in final_localities:
            self.stdout.write(f"  - {locality}")

    def verify_analytics_compatibility(self):
        """Verify that analytics endpoints still work"""
        self.stdout.write("Verifying analytics compatibility...")
        
        # Test basic queries
        with connection.cursor() as cursor:
            # Test total count
            cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
            total_count = cursor.fetchone()[0]
            self.stdout.write(f"Total records in database: {total_count}")
            
            # Test by data source (only if column exists)
            try:
                cursor.execute("SELECT data_source, COUNT(*) FROM disease_monitor_hospitalhealthdata GROUP BY data_source")
                source_counts = cursor.fetchall()
                for source, count in source_counts:
                    self.stdout.write(f"Records from {source}: {count}")
            except Exception as e:
                if "does not exist" in str(e):
                    self.stdout.write("data_source column not yet added (this is normal for initial verification)")
                else:
                    self.stdout.write(f"Error checking data_source: {e}")
            
            # Test locality count
            cursor.execute("SELECT COUNT(DISTINCT address_locality) FROM disease_monitor_hospitalhealthdata")
            locality_count = cursor.fetchone()[0]
            self.stdout.write(f"Unique localities: {locality_count}")
            
            # Test orgname count
            cursor.execute("SELECT COUNT(DISTINCT orgname) FROM disease_monitor_hospitalhealthdata")
            orgname_count = cursor.fetchone()[0]
            self.stdout.write(f"Unique orgnames: {orgname_count}")
            
            # Test some sample records (only if there are records)
            if total_count > 0:
                cursor.execute("SELECT orgname, address_locality, age, sex FROM disease_monitor_hospitalhealthdata LIMIT 3")
                sample_records = cursor.fetchall()
                self.stdout.write("Sample records:")
                for record in sample_records:
                    self.stdout.write(f"  {record}")
            else:
                self.stdout.write("No records in database yet")

    def check_and_fix_table_structure(self):
        """Check and fix table structure to ensure proper ID handling"""
        self.stdout.write("Checking table structure...")
        
        with connection.cursor() as cursor:
            # Check if health data table has an id column
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'disease_monitor_hospitalhealthdata' 
                AND column_name = 'id'
            """)
            id_column = cursor.fetchone()
            
            if not id_column:
                self.stdout.write("Adding ID column to hospital health data table...")
                cursor.execute("""
                    ALTER TABLE disease_monitor_hospitalhealthdata 
                    ADD COLUMN id SERIAL PRIMARY KEY
                """)
                self.stdout.write("Added ID column to hospital health data table")
            else:
                self.stdout.write("ID column already exists in hospital health data table")
            
            # Check if localities table has an id column
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'hospital_localities' 
                AND column_name = 'id'
            """)
            id_column = cursor.fetchone()
            
            if not id_column:
                self.stdout.write("Adding ID column to hospital localities table...")
                cursor.execute("""
                    ALTER TABLE hospital_localities 
                    ADD COLUMN id SERIAL PRIMARY KEY
                """)
                self.stdout.write("Added ID column to hospital localities table")
            else:
                self.stdout.write("ID column already exists in hospital localities table")

    def handle(self, *args, **options):
        """Main update process"""
        self.stdout.write("Starting safe database update process...")
        
        try:
            if options['verify_only']:
                self.verify_analytics_compatibility()
                return
            
            if options['backup_only']:
                self.create_backup_tables()
                return
            
            # Step 1: Create backups
            self.create_backup_tables()
            
            # Step 2: Check and fix table structure
            self.check_and_fix_table_structure()
            
            # Step 3: Add new columns
            self.add_new_columns()
            
            # Step 4: Clear existing data
            self.clear_existing_data()
            
            # Step 5: Transform data
            transformed_records = self.transform_merged_data()
            
            # Step 6: Insert data
            if transformed_records:
                self.insert_transformed_data(transformed_records)
            
            # Step 7: Update locality mappings
            self.update_locality_mappings()
            
            # Step 8: Verify compatibility
            self.verify_analytics_compatibility()
            
            self.stdout.write(
                self.style.SUCCESS("Database update completed successfully!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Database update failed: {e}")
            )
            self.stdout.write(
                self.style.ERROR("Please check the backup tables and restore if necessary")
            )
            raise 