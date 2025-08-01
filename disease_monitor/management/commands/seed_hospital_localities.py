from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd
import os
from disease_monitor.models import HospitalLocalities

class Command(BaseCommand):
    help = 'Seed HospitalLocalities model from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='hospital_localities.csv',
            help='Path to the CSV file (default: hospital_localities.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear_existing = options['clear']
        dry_run = options['dry_run']

        self.stdout.write('🏥 Seeding Hospital Localities...')
        self.stdout.write('=' * 60)

        # Check if CSV file exists
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'❌ CSV file not found: {csv_file}')
            )
            self.stdout.write(
                '💡 Run the extract_hospital_localities.py script first to generate the CSV file.'
            )
            return

        try:
            # Read CSV file
            self.stdout.write(f'📖 Reading CSV file: {csv_file}')
            df = pd.read_csv(csv_file)
            
            self.stdout.write(f'✅ Found {len(df)} records in CSV')
            
            # Validate required columns
            required_columns = ['locality', 'orgname']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f'❌ Missing required columns: {missing_columns}')
                )
                return

            # Clean data
            df = df.dropna(subset=['locality', 'orgname'])
            df['locality'] = df['locality'].str.strip()
            df['orgname'] = df['orgname'].str.strip()
            df = df[df['locality'] != '']
            df = df[df['orgname'] != '']
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['locality', 'orgname'])
            
            self.stdout.write(f'✅ Cleaned data: {len(df)} unique records')

            if dry_run:
                self.stdout.write('\n📊 Sample data that would be imported:')
                self.stdout.write('-' * 60)
                for _, row in df.head(10).iterrows():
                    self.stdout.write(f'   {row["locality"]} - {row["orgname"]}')
                
                if len(df) > 10:
                    self.stdout.write(f'   ... and {len(df) - 10} more records')
                
                self.stdout.write(f'\n✅ Dry run completed. Would import {len(df)} records.')
                return

            # Clear existing data if requested
            if clear_existing:
                self.stdout.write('🗑️  Clearing existing data...')
                HospitalLocalities.objects.all().delete()
                self.stdout.write('✅ Existing data cleared')

            # Import data
            self.stdout.write('📥 Importing data...')
            
            with transaction.atomic():
                created_count = 0
                skipped_count = 0
                
                for _, row in df.iterrows():
                    locality = row['locality']
                    orgname = row['orgname']
                    
                    # Check if combination already exists
                    if not HospitalLocalities.objects.filter(
                        locality=locality, 
                        orgname=orgname
                    ).exists():
                        HospitalLocalities.objects.create(
                            locality=locality,
                            orgname=orgname
                        )
                        created_count += 1
                    else:
                        skipped_count += 1

            # Show results
            self.stdout.write('\n📊 Import Results:')
            self.stdout.write('-' * 40)
            self.stdout.write(f'   Created: {created_count}')
            self.stdout.write(f'   Skipped (duplicates): {skipped_count}')
            self.stdout.write(f'   Total in database: {HospitalLocalities.objects.count()}')

            # Show statistics
            total_localities = HospitalLocalities.objects.values('locality').distinct().count()
            total_hospitals = HospitalLocalities.objects.values('orgname').distinct().count()
            
            self.stdout.write(f'\n📈 Database Statistics:')
            self.stdout.write('-' * 40)
            self.stdout.write(f'   Unique localities: {total_localities}')
            self.stdout.write(f'   Unique hospitals: {total_hospitals}')
            self.stdout.write(f'   Total combinations: {HospitalLocalities.objects.count()}')

            # Show sample data
            self.stdout.write(f'\n📋 Sample data in database:')
            self.stdout.write('-' * 40)
            sample_data = HospitalLocalities.objects.all()[:10]
            for item in sample_data:
                self.stdout.write(f'   {item.locality} - {item.orgname}')

            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Successfully seeded {created_count} hospital localities!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error seeding data: {e}')
            )
            raise 