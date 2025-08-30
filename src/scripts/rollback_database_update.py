#!/usr/bin/env python3
"""
Rollback Script for Database Update
Reverts the hospital health data table to its previous state if needed
"""

import os
import sys
import django
import logging

# Setup Django
sys.path.append('/home/grandkojo/Documents/GITHUB/EpiScope')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from django.db import connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_rollback.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_backup_exists():
    """Check if backup tables exist"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN (
                'disease_monitor_hospitalhealthdata_backup',
                'hospital_localities_backup'
            )
        """)
        backup_tables = [row[0] for row in cursor.fetchall()]
        
        if len(backup_tables) < 2:
            logger.error("Backup tables not found. Cannot perform rollback.")
            return False
        
        logger.info(f"Found backup tables: {backup_tables}")
        return True

def rollback_main_table():
    """Rollback the main hospital health data table"""
    logger.info("Rolling back main hospital health data table...")
    
    with connection.cursor() as cursor:
        # Get counts before rollback
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
        current_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata_backup")
        backup_count = cursor.fetchone()[0]
        
        logger.info(f"Current records: {current_count}, Backup records: {backup_count}")
        
        # Drop current table and restore from backup
        cursor.execute("DROP TABLE disease_monitor_hospitalhealthdata")
        cursor.execute("""
            CREATE TABLE disease_monitor_hospitalhealthdata AS 
            SELECT * FROM disease_monitor_hospitalhealthdata_backup
        """)
        
        # Verify rollback
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
        restored_count = cursor.fetchone()[0]
        
        logger.info(f"Rollback completed. Restored {restored_count} records")

def rollback_localities_table():
    """Rollback the hospital localities table"""
    logger.info("Rolling back hospital localities table...")
    
    with connection.cursor() as cursor:
        # Get counts before rollback
        cursor.execute("SELECT COUNT(*) FROM hospital_localities")
        current_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hospital_localities_backup")
        backup_count = cursor.fetchone()[0]
        
        logger.info(f"Current localities: {current_count}, Backup localities: {backup_count}")
        
        # Drop current table and restore from backup
        cursor.execute("DROP TABLE hospital_localities")
        cursor.execute("""
            CREATE TABLE hospital_localities AS 
            SELECT * FROM hospital_localities_backup
        """)
        
        # Verify rollback
        cursor.execute("SELECT COUNT(*) FROM hospital_localities")
        restored_count = cursor.fetchone()[0]
        
        logger.info(f"Localities rollback completed. Restored {restored_count} records")

def verify_rollback():
    """Verify that the rollback was successful"""
    logger.info("Verifying rollback...")
    
    with connection.cursor() as cursor:
        # Check main table
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
        main_count = cursor.fetchone()[0]
        
        # Check localities table
        cursor.execute("SELECT COUNT(*) FROM hospital_localities")
        localities_count = cursor.fetchone()[0]
        
        # Check if new columns still exist (they shouldn't)
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'disease_monitor_hospitalhealthdata' 
            AND column_name IN ('data_source', 'medicine_prescribed', 'cost_of_treatment', 'schedule_date', 'locality_encoded')
        """)
        new_columns = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Main table records: {main_count}")
        logger.info(f"Localities records: {localities_count}")
        
        if new_columns:
            logger.warning(f"New columns still exist: {new_columns}")
        else:
            logger.info("All new columns removed successfully")

def main():
    """Main rollback process"""
    logger.info("Starting database rollback process...")
    
    try:
        # Check if backups exist
        if not check_backup_exists():
            return
        
        # Confirm rollback
        response = input("Are you sure you want to rollback the database? This will remove all new data. (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Rollback cancelled by user")
            return
        
        # Perform rollback
        rollback_main_table()
        rollback_localities_table()
        verify_rollback()
        
        logger.info("Database rollback completed successfully!")
        
    except Exception as e:
        logger.error(f"Database rollback failed: {e}")
        raise

if __name__ == "__main__":
    main() 