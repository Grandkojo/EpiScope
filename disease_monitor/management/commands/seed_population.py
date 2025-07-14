from django.core.management.base import BaseCommand
from disease_monitor.models import RegionPopulation
import csv
import os

class Command(BaseCommand):
    help = 'Seed the region population data from CSV'

    def handle(self, *args, **options):
        # Path to the CSV file
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'src', 'artifacts', 'csv', 'ghana_census_estimates.csv'
        )
        
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found at: {csv_path}')
            )
            return
        
        # Clear existing data
        RegionPopulation.objects.all().delete()
        self.stdout.write('Cleared existing population data')
        
        # Read and insert data
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                try:
                    RegionPopulation.objects.create(
                        region=row['region'],
                        periodname=row['periodname'],
                        population=int(row['population'])
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error inserting {row}: {e}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully inserted {count} population records')
        )
        
        # Show summary
        total_records = RegionPopulation.objects.count()
        regions = RegionPopulation.objects.values_list('region', flat=True).distinct()
        years = RegionPopulation.objects.values_list('periodname', flat=True).distinct()
        
        self.stdout.write(f'Total records: {total_records}')
        self.stdout.write(f'Unique regions: {len(regions)}')
        self.stdout.write(f'Unique years: {len(years)}')
        
        # Show sample data
        self.stdout.write('\nSample data:')
        sample = RegionPopulation.objects.all()[:5]
        for record in sample:
            self.stdout.write(f'  {record}')
        
        # Show regions and years
        self.stdout.write(f'\nRegions: {", ".join(sorted(regions))}')
        self.stdout.write(f'Years: {", ".join(sorted(years))}') 