from django.core.management.base import BaseCommand
from chat.models import FineTuningDataset
import pandas as pd
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Generate contextual training data from CSV files for Vertex AI fine-tuning'

    def add_arguments(self, parser):
        parser.add_argument('--csv-dir', type=str, default='src/artifacts', help='Directory containing CSV files')
        parser.add_argument('--disease', type=str, required=True, help='Disease name (e.g., diabetes, malaria)')
        parser.add_argument('--output-file', type=str, help='Output JSON file for training data')
        parser.add_argument('--save-to-db', action='store_true', help='Save training examples to database')

    def handle(self, *args, **kwargs):
        csv_dir = kwargs['csv_dir']
        disease_name = kwargs['disease']
        output_file = kwargs['output_file']
        save_to_db = kwargs['save_to_db']

        self.stdout.write(f'Generating training data for {disease_name} from {csv_dir}')
        training_data = self.generate_from_csv_files(csv_dir, disease_name)

        if training_data:
            self.stdout.write(f'Generated {len(training_data)} training examples')
            
            if save_to_db:
                self.save_to_database(training_data, disease_name)

            if output_file:
                self.save_to_json(training_data, output_file)

            default_file = f'training_data_{disease_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            self.save_to_json(training_data, default_file)
        else:
            self.stdout.write(self.style.WARNING('No training data generated'))

    def generate_from_csv_files(self, csv_dir, disease_name):
        training_data = []
        
        # Process time series data
        time_series_file = os.path.join(csv_dir, 'time_series', f'health_data_eams_{disease_name}_time_stamped.csv')
        if os.path.exists(time_series_file):
            training_data.extend(self.process_time_series_data(time_series_file, disease_name))

        # Process hotspots data
        hotspots_file = os.path.join(csv_dir, 'csv', 'national_hotspots.csv')
        if os.path.exists(hotspots_file):
            training_data.extend(self.process_hotspots_data(hotspots_file, disease_name))

        return training_data

    def process_time_series_data(self, file_path, disease_name):
        training_data = []
        
        try:
            df = pd.read_csv(file_path)
            
            if 'date' in df.columns and 'cases' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                recent_data = df.tail(30)
                
                if len(recent_data) > 0:
                    trend = self.calculate_trend(recent_data['cases'])
                    
                    training_data.extend([
                        {
                            "instruction": f"What are the current {disease_name} trends?",
                            "input": f"Context: {disease_name} epidemic monitoring with time series data",
                            "output": f"Based on our monitoring data, {disease_name} cases show a {trend} trend over the past 30 days. Recent data indicates {len(recent_data)} cases in the last month. Key indicators suggest {self.get_trend_interpretation(trend)}. Regular monitoring helps identify patterns and enables timely intervention strategies."
                        }
                    ])

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing time series data: {e}'))

        return training_data

    def process_hotspots_data(self, file_path, disease_name):
        training_data = []
        
        try:
            df = pd.read_csv(file_path)
            disease_data = df[df['disease'].str.contains(disease_name, case=False, na=False)]
            
            if len(disease_data) > 0:
                top_hotspots = disease_data.nlargest(5, 'cases') if 'cases' in disease_data.columns else disease_data.head(5)
                hotspot_names = top_hotspots['region'].tolist() if 'region' in top_hotspots.columns else []
                
                training_data.append({
                    "instruction": f"What are the {disease_name} hotspots?",
                    "input": f"Context: {disease_name} epidemic monitoring with hotspot data",
                    "output": f"Based on our monitoring data, the main {disease_name} hotspots include {', '.join(hotspot_names)}. These areas show higher transmission rates and require increased surveillance and intervention measures."
                })

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing hotspots data: {e}'))

        return training_data

    def calculate_trend(self, data):
        if len(data) < 2:
            return "stable"
        
        first_half = data[:len(data)//2].mean()
        second_half = data[len(data)//2:].mean()
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"

    def get_trend_interpretation(self, trend):
        if trend == "increasing":
            return "a concerning upward trend that requires immediate attention"
        elif trend == "decreasing":
            return "a positive downward trend indicating effective control measures"
        else:
            return "a stable pattern that requires continued monitoring"

    def save_to_database(self, training_data, disease_name):
        count = 0
        for example in training_data:
            obj, created = FineTuningDataset.objects.get_or_create(
                disease_name=disease_name,
                instruction=example['instruction'],
                defaults={
                    'input_text': example.get('input', ''),
                    'output_text': example['output'],
                    'source': 'csv_analysis',
                    'quality_score': 0.9,
                    'is_approved': True
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Saved {count} training examples to database'))

    def save_to_json(self, training_data, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f'Saved training data to {filename}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error saving to JSON: {e}')) 