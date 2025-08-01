from django.core.management.base import BaseCommand
import pandas as pd
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Prepare CSV files for direct Vertex AI upload and training'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-dir',
            type=str,
            default='src/artifacts',
            help='Directory containing CSV files'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='vertex_ai_uploads',
            help='Output directory for Vertex AI ready files'
        )
        parser.add_argument(
            '--disease',
            type=str,
            required=True,
            help='Disease name (e.g., diabetes, malaria)'
        )

    def handle(self, *args, **kwargs):
        csv_dir = kwargs['csv_dir']
        output_dir = kwargs['output_dir']
        disease_name = kwargs['disease']

        self.stdout.write(f'Preparing CSV files for Vertex AI upload - {disease_name}')

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Process all CSV files
        self.process_csv_files(csv_dir, output_dir, disease_name)

        self.stdout.write(self.style.SUCCESS(f'Files prepared for Vertex AI upload in: {output_dir}'))

    def process_csv_files(self, csv_dir, output_dir, disease_name):
        """Process all CSV files and prepare for Vertex AI"""
        
        # Process time series data
        time_series_file = os.path.join(csv_dir, 'time_series', f'health_data_eams_{disease_name}_time_stamped.csv')
        if os.path.exists(time_series_file):
            self.process_time_series_for_vertex_ai(time_series_file, output_dir, disease_name)

        # Process hotspots data
        hotspots_file = os.path.join(csv_dir, 'csv', 'national_hotspots.csv')
        if os.path.exists(hotspots_file):
            self.process_hotspots_for_vertex_ai(hotspots_file, output_dir, disease_name)

        # Process any other CSV files
        for root, dirs, files in os.walk(csv_dir):
            for file in files:
                if file.endswith('.csv') and disease_name.lower() in file.lower():
                    file_path = os.path.join(root, file)
                    self.process_generic_csv_for_vertex_ai(file_path, output_dir, disease_name)

    def process_time_series_for_vertex_ai(self, file_path, output_dir, disease_name):
        """Process time series data for Vertex AI"""
        try:
            df = pd.read_csv(file_path)
            
            # Create Vertex AI training format
            training_data = []
            
            if 'date' in df.columns and 'cases' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
                # Generate trend-based questions
                recent_data = df.tail(30)
                if len(recent_data) > 0:
                    trend = self.calculate_trend(recent_data['cases'])
                    
                    training_data.extend([
                        {
                            "instruction": f"What are the current {disease_name} trends?",
                            "input": f"Context: Time series data shows {len(recent_data)} cases in the last 30 days",
                            "output": f"Based on our {disease_name} monitoring data, cases show a {trend} trend over the past 30 days. Recent data indicates {len(recent_data)} cases in the last month. Key indicators suggest {self.get_trend_interpretation(trend)}. Regular monitoring helps identify patterns and enables timely intervention strategies."
                        },
                        {
                            "instruction": f"What is the {disease_name} case trend this month?",
                            "input": f"Context: Recent time series data for {disease_name}",
                            "output": f"Current {disease_name} case trends show {trend} with {len(recent_data)} cases recorded in the past 30 days. The data indicates {self.get_trend_interpretation(trend)}. This trend analysis helps inform public health interventions and resource allocation."
                        }
                    ])

                # Generate seasonal pattern questions
                df['month'] = pd.to_datetime(df['date']).dt.month
                monthly_patterns = df.groupby('month')['cases'].mean()
                
                if len(monthly_patterns) > 0:
                    peak_month = monthly_patterns.idxmax()
                    peak_cases = monthly_patterns.max()
                    
                    training_data.append({
                        "instruction": f"When is {disease_name} most common?",
                        "input": f"Context: Seasonal analysis of {disease_name} data",
                        "output": f"Based on our analysis of {disease_name} data, the disease shows seasonal patterns with peak transmission typically occurring in month {peak_month} with an average of {peak_cases:.0f} cases. Understanding these seasonal patterns helps in planning prevention campaigns and resource allocation."
                    })

            # Save to Vertex AI format
            self.save_vertex_ai_format(training_data, output_dir, f"{disease_name}_time_series_training.json")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing time series: {e}'))

    def process_hotspots_for_vertex_ai(self, file_path, output_dir, disease_name):
        """Process hotspots data for Vertex AI"""
        try:
            df = pd.read_csv(file_path)
            disease_data = df[df['disease'].str.contains(disease_name, case=False, na=False)]
            
            training_data = []
            
            if len(disease_data) > 0:
                top_hotspots = disease_data.nlargest(5, 'cases') if 'cases' in disease_data.columns else disease_data.head(5)
                hotspot_names = top_hotspots['region'].tolist() if 'region' in top_hotspots.columns else []
                
                training_data.extend([
                    {
                        "instruction": f"What are the {disease_name} hotspots?",
                        "input": f"Context: Geographic hotspot analysis for {disease_name}",
                        "output": f"Based on our monitoring data, the main {disease_name} hotspots include {', '.join(hotspot_names)}. These areas show higher transmission rates and require increased surveillance and intervention measures. Regular monitoring helps track transmission patterns and enables targeted prevention strategies."
                    },
                    {
                        "instruction": f"Which areas have the highest {disease_name} cases?",
                        "input": f"Context: Regional case distribution for {disease_name}",
                        "output": f"The areas with the highest {disease_name} cases are {', '.join(hotspot_names)}. These hotspots require focused public health interventions, increased surveillance, and community awareness campaigns to control transmission."
                    }
                ])

            # Save to Vertex AI format
            self.save_vertex_ai_format(training_data, output_dir, f"{disease_name}_hotspots_training.json")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing hotspots: {e}'))

    def process_generic_csv_for_vertex_ai(self, file_path, output_dir, disease_name):
        """Process generic CSV files for Vertex AI"""
        try:
            df = pd.read_csv(file_path)
            training_data = []
            
            # Generate demographic questions
            if 'age' in df.columns:
                age_stats = df['age'].describe()
                avg_age = age_stats['mean']
                
                training_data.append({
                    "instruction": f"What is the age distribution of {disease_name} cases?",
                    "input": f"Context: Demographic analysis of {disease_name} cases",
                    "output": f"Based on our {disease_name} data analysis, the average age of cases is {avg_age:.1f} years. The age distribution shows {self.get_age_interpretation(avg_age)}. Understanding demographic patterns helps in targeting prevention and intervention strategies."
                })

            if 'sex' in df.columns:
                gender_dist = df['sex'].value_counts()
                if len(gender_dist) > 0:
                    dominant_gender = gender_dist.index[0]
                    dominant_count = gender_dist.iloc[0]
                    
                    training_data.append({
                        "instruction": f"Does {disease_name} affect men or women more?",
                        "input": f"Context: Gender distribution analysis for {disease_name}",
                        "output": f"Based on our {disease_name} data analysis, {dominant_gender} cases are more common with {dominant_count} cases compared to other groups. This gender distribution pattern helps inform targeted public health messaging and intervention strategies."
                    })

            # Save to Vertex AI format
            filename = f"{disease_name}_{os.path.basename(file_path).replace('.csv', '_training.json')}"
            self.save_vertex_ai_format(training_data, output_dir, filename)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing generic CSV: {e}'))

    def calculate_trend(self, data):
        """Calculate trend direction"""
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
        """Get trend interpretation"""
        if trend == "increasing":
            return "a concerning upward trend that requires immediate attention"
        elif trend == "decreasing":
            return "a positive downward trend indicating effective control measures"
        else:
            return "a stable pattern that requires continued monitoring"

    def get_age_interpretation(self, avg_age):
        """Get age interpretation"""
        if avg_age < 30:
            return "a younger population affected, suggesting need for youth-focused interventions"
        elif avg_age > 60:
            return "an older population affected, highlighting the importance of geriatric care"
        else:
            return "a middle-aged population affected, indicating broad public health measures are needed"

    def save_vertex_ai_format(self, training_data, output_dir, filename):
        """Save in Vertex AI format"""
        if training_data:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            self.stdout.write(f'Saved {len(training_data)} training examples to {filepath}')
        else:
            self.stdout.write(self.style.WARNING(f'No training data generated for {filename}')) 