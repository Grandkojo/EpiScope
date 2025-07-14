from django.core.management.base import BaseCommand
from disease_monitor.models import Disease, DiseaseTrends
import csv
import os

CSV_PATH = 'src/artifacts/time_series/google_trends_full_monthly.csv'

# Map CSV columns to disease names in DB
DISEASE_MAP = {
    'diabetes_trend': 'diabetes',
    'malaria_trend': 'malaria',
    # Add more mappings as needed
}

class Command(BaseCommand):
    help = 'Seed DiseaseTrends from Google Trends CSV'

    def handle(self, *args, **kwargs):
        if not os.path.exists(CSV_PATH):
            self.stderr.write(self.style.ERROR(f'CSV file not found: {CSV_PATH}'))
            return
        with open(CSV_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                month_str = row['Month']  # e.g., '2022-03'
                year, month = map(int, month_str.split('-'))
                for col, disease_key in DISEASE_MAP.items():
                    try:
                        disease = Disease.objects.get(disease_name__iexact=disease_key)
                    except Disease.DoesNotExist:
                        self.stderr.write(self.style.WARNING(f'Disease not found: {disease_key}'))
                        continue
                    trend_value = float(row[col]) if row[col] else None
                    if trend_value is not None:
                        DiseaseTrends.objects.update_or_create(
                            disease=disease, year=year, month=month,
                            defaults={'trend_value': trend_value}
                        )
            self.stdout.write(self.style.SUCCESS('DiseaseTrends seeded successfully.')) 