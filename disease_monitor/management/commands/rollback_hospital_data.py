from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Rollback hospital health data to previous state using backup tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-backup',
            action='store_true',
            help='Only check if backup tables exist',
        )

    def check_backup_exists(self):
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
                self.stdout.write(
                    self.style.ERROR("Backup tables not found. Cannot perform rollback.")
                )
                return False
            
            self.stdout.write(f"Found backup tables: {backup_tables}")
            return True

    def rollback_main_table(self):
        """Rollback the main hospital health data table"""
        self.stdout.write("Rolling back main hospital health data table...")
        
        with connection.cursor() as cursor:
            # Get counts before rollback
            cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
            current_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata_backup")
            backup_count = cursor.fetchone()[0]
            
            self.stdout.write(f"Current records: {current_count}, Backup records: {backup_count}")
            
            # Drop current table and restore from backup
            cursor.execute("DROP TABLE disease_monitor_hospitalhealthdata")
            cursor.execute("""
                CREATE TABLE disease_monitor_hospitalhealthdata AS 
                SELECT * FROM disease_monitor_hospitalhealthdata_backup
            """)
            
            # Verify rollback
            cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
            restored_count = cursor.fetchone()[0]
            
            self.stdout.write(f"Rollback completed. Restored {restored_count} records")

    def rollback_localities_table(self):
        """Rollback the hospital localities table"""
        self.stdout.write("Rolling back hospital localities table...")
        
        with connection.cursor() as cursor:
            # Get counts before rollback
            cursor.execute("SELECT COUNT(*) FROM hospital_localities")
            current_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM hospital_localities_backup")
            backup_count = cursor.fetchone()[0]
            
            self.stdout.write(f"Current localities: {current_count}, Backup localities: {backup_count}")
            
            # Drop current table and restore from backup
            cursor.execute("DROP TABLE hospital_localities")
            cursor.execute("""
                CREATE TABLE hospital_localities AS 
                SELECT * FROM hospital_localities_backup
            """)
            
            # Verify rollback
            cursor.execute("SELECT COUNT(*) FROM hospital_localities")
            restored_count = cursor.fetchone()[0]
            
            self.stdout.write(f"Localities rollback completed. Restored {restored_count} records")

    def verify_rollback(self):
        """Verify that the rollback was successful"""
        self.stdout.write("Verifying rollback...")
        
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
            
            self.stdout.write(f"Main table records: {main_count}")
            self.stdout.write(f"Localities records: {localities_count}")
            
            if new_columns:
                self.stdout.write(
                    self.style.WARNING(f"New columns still exist: {new_columns}")
                )
            else:
                self.stdout.write("All new columns removed successfully")

    def handle(self, *args, **options):
        """Main rollback process"""
        self.stdout.write("Starting database rollback process...")
        
        try:
            if options['check_backup']:
                self.check_backup_exists()
                return
            
            # Check if backups exist
            if not self.check_backup_exists():
                return
            
            # Confirm rollback
            response = input("Are you sure you want to rollback the database? This will remove all new data. (yes/no): ")
            if response.lower() != 'yes':
                self.stdout.write("Rollback cancelled by user")
                return
            
            # Perform rollback
            self.rollback_main_table()
            self.rollback_localities_table()
            self.verify_rollback()
            
            self.stdout.write(
                self.style.SUCCESS("Database rollback completed successfully!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Database rollback failed: {e}")
            )
            raise 