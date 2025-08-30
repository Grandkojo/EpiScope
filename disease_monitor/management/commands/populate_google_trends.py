import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from api.services.google_trends_service import GoogleTrendsService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populate initial Google Trends data for major diseases'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--diseases',
            nargs='+',
            type=str,
            default=['Diabetes', 'Malaria', 'Meningitis', 'Cholera'],
            help='List of diseases to populate data for'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh even if cache exists'
        )
        parser.add_argument(
            '--timeframes',
            nargs='+',
            type=str,
            default=['now 7-d', 'today 12-m'],
            help='Timeframes to fetch data for'
        )
        parser.add_argument(
            '--import-csv',
            action='store_true',
            help='Import existing CSV data before fetching new data'
        )
    
    def handle(self, *args, **options):
        diseases = options['diseases']
        force = options['force']
        timeframes = options['timeframes']
        import_csv = options['import_csv']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Google Trends data population for {len(diseases)} diseases'
            )
        )
        
        # Import existing CSV data if requested
        if import_csv:
            self.stdout.write('Importing existing CSV data...')
            self._import_csv_data()
        
        trends_service = GoogleTrendsService()
        
        for disease in diseases:
            if disease not in trends_service.SUPPORTED_DISEASES:
                self.stdout.write(
                    self.style.WARNING(f'Disease "{disease}" not supported, skipping...')
                )
                continue
                
            self.stdout.write(f'Processing disease: {disease}')
            
            for timeframe in timeframes:
                self.stdout.write(f'  Fetching data for timeframe: {timeframe}')
                
                try:
                    # Fetch all data types for this disease and timeframe
                    trends_data = trends_service.get_trends_data(
                        disease, 
                        timeframe, 
                        data_types=['interest_over_time', 'related_queries', 'related_topics', 'interest_by_region']
                    )
                    
                    if trends_data and 'error' not in trends_data:
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✓ All data types fetched successfully')
                        )
                        
                        # Store metrics if we have interest over time data
                        if 'interest_over_time' in trends_data and 'timelineData' in trends_data['interest_over_time']:
                            self._store_metrics(disease, trends_data['interest_over_time'], timeframe)
                    else:
                        error_msg = trends_data.get('error', 'Unknown error') if trends_data else 'No data returned'
                        self.stdout.write(
                            self.style.ERROR(f'    ✗ Error: {error_msg}')
                        )
                    
                    # Add delay to respect rate limits
                    if timeframe != timeframes[-1]:  # Don't delay after last timeframe
                        self.stdout.write('    Waiting 65 seconds for rate limit...')
                        import time
                        time.sleep(65)
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'    ✗ Error fetching data: {str(e)}')
                    )
                    logger.error(f'Error fetching Google Trends data for {disease}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS('Google Trends data population completed!')
        )
    
    def _import_csv_data(self):
        """Import existing CSV data into the database"""
        try:
            # Path to CSV files
            csv_dir = 'src/artifacts/time_series'
            
            # Import full monthly data
            full_monthly_path = os.path.join(csv_dir, 'google_trends_full_monthly.csv')
            if os.path.exists(full_monthly_path):
                self.stdout.write('  Importing full monthly data...')
                self._import_monthly_csv(full_monthly_path)
            
            # Import time series data
            time_series_path = os.path.join(csv_dir, 'google_trends_time_series.csv')
            if os.path.exists(time_series_path):
                self.stdout.write('  Importing time series data...')
                self._import_time_series_csv(time_series_path)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing CSV data: {str(e)}')
            )
            logger.error(f'Error importing CSV data: {str(e)}')
    
    def _import_monthly_csv(self, file_path):
        """Import monthly CSV data"""
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    month_str = row['Month']
                    try:
                        # Parse month (format: YYYY-MM)
                        date = datetime.strptime(month_str, '%Y-%m').date()
                        
                        # Import diabetes data
                        if 'diabetes_trend' in row and row['diabetes_trend']:
                            self._create_metrics_from_csv('Diabetes', date, float(row['diabetes_trend']))
                        
                        # Import malaria data
                        if 'malaria_trend' in row and row['malaria_trend']:
                            self._create_metrics_from_csv('Malaria', date, float(row['malaria_trend']))
                            
                    except (ValueError, KeyError) as e:
                        self.stdout.write(f'    Skipping row {row}: {str(e)}')
                        
        except Exception as e:
            self.stdout.write(f'    Error reading monthly CSV: {str(e)}')
    
    def _import_time_series_csv(self, file_path):
        """Import time series CSV data"""
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    month_str = row['Month']
                    try:
                        # Parse month (format: YYYY-MM)
                        date = datetime.strptime(month_str, '%Y-%m').date()
                        
                        # Import diabetes data
                        if 'diabetes_trend' in row and row['diabetes_trend']:
                            self._create_metrics_from_csv('Diabetes', date, float(row['diabetes_trend']))
                        
                        # Import malaria data
                        if 'malaria_trend' in row and row['malaria_trend']:
                            self._create_metrics_from_csv('Malaria', date, float(row['malaria_trend']))
                            
                    except (ValueError, KeyError) as e:
                        self.stdout.write(f'    Skipping row {row}: {str(e)}')
                        
        except Exception as e:
            self.stdout.write(f'    Error reading time series CSV: {str(e)}')
    
    def _create_metrics_from_csv(self, disease_name, date, search_interest):
        """Create metrics from CSV data"""
        try:
            metrics, created = GoogleTrendsMetrics.objects.update_or_create(
                disease_name=disease_name,
                date=date,
                defaults={
                    'search_interest': search_interest,
                    'peak_interest': search_interest,  # Single data point
                    'total_searches': search_interest,  # Approximate
                    'trend_direction': 'stable',  # Default for historical data
                    'trend_strength': 0,  # Default for historical data
                    'data_source': 'csv_import',
                    'last_updated': datetime.now()
                }
            )
            
            if created:
                self.stdout.write(f'      ✓ Created metrics for {disease_name} on {date}')
            else:
                self.stdout.write(f'      ✓ Updated metrics for {disease_name} on {date}')
                
        except Exception as e:
            self.stdout.write(f'      ✗ Error creating metrics for {disease_name}: {str(e)}')
    
    def _store_metrics(self, disease_name, data, timeframe):
        """Store processed metrics from interest over time data"""
        try:
            if 'timelineData' not in data:
                return
            
            timeline_data = data['timelineData']
            if not timeline_data:
                return
            
            # Get the most recent data point
            latest_data = timeline_data[-1]
            
            # Calculate trend direction
            if len(timeline_data) >= 2:
                current_interest = latest_data.get('value', [0])[0]
                previous_interest = timeline_data[-2].get('value', [0])[0]
                
                if current_interest > previous_interest:
                    trend_direction = 'increasing'
                elif current_interest < previous_interest:
                    trend_direction = 'decreasing'
                else:
                    trend_direction = 'stable'
                
                trend_strength = abs(current_interest - previous_interest)
            else:
                trend_direction = 'stable'
                trend_strength = 0
            
            # Find peak interest
            peak_interest = max(
                [point.get('value', [0])[0] for point in timeline_data]
            )
            
            # Calculate total searches (approximate)
            total_searches = sum(
                [point.get('value', [0])[0] for point in timeline_data]
            )
            
            # Get date from latest data
            date_str = latest_data.get('time', '')
            if date_str:
                try:
                    from datetime import datetime
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    date = datetime.now().date()
            else:
                date = datetime.now().date()
            
            # Create or update metrics
            metrics, created = GoogleTrendsMetrics.objects.update_or_create(
                disease_name=disease_name,
                date=date,
                defaults={
                    'search_interest': latest_data.get('value', [0])[0],
                    'peak_interest': peak_interest,
                    'total_searches': total_searches,
                    'trend_direction': trend_direction,
                    'trend_strength': trend_strength,
                    'data_source': 'google_trends',
                    'last_updated': datetime.now()
                }
            )
            
            if created:
                self.stdout.write(f'      ✓ Metrics stored for {date}')
            else:
                self.stdout.write(f'      ✓ Metrics updated for {date}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'      ✗ Error storing metrics: {str(e)}')
            )
            logger.error(f'Error storing metrics for {disease_name}: {str(e)}') 