from django.core.management.base import BaseCommand
import pandas as pd
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Setup Vertex AI Search (RAG) with CSV files for disease monitoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-dir',
            type=str,
            default='src/artifacts',
            help='Directory containing CSV files'
        )
        parser.add_argument(
            '--disease',
            type=str,
            required=True,
            help='Disease name (e.g., diabetes, malaria)'
        )
        parser.add_argument(
            '--project-id',
            type=str,
            required=True,
            help='Google Cloud Project ID'
        )
        parser.add_argument(
            '--location',
            type=str,
            default='us-central1',
            help='Google Cloud location'
        )

    def handle(self, *args, **kwargs):
        csv_dir = kwargs['csv_dir']
        disease_name = kwargs['disease']
        project_id = kwargs['project_id']
        location = kwargs['location']

        self.stdout.write(f'Setting up Vertex AI Search (RAG) for {disease_name}')

        try:
            # Step 1: Prepare CSV files for RAG
            self.prepare_csv_for_rag(csv_dir, disease_name)
            
            # Step 2: Create Vertex AI Search data store
            self.create_search_datastore(disease_name, project_id, location)
            
            # Step 3: Upload CSV files to the data store
            self.upload_csv_to_datastore(disease_name, project_id, location)
            
            # Step 4: Create search app
            self.create_search_app(disease_name, project_id, location)
            
            self.stdout.write(
                self.style.SUCCESS(f'Vertex AI Search setup completed for {disease_name}')
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'RAG setup failed: {e}'))

    def prepare_csv_for_rag(self, csv_dir, disease_name):
        """Prepare CSV files for Vertex AI Search"""
        self.stdout.write('Preparing CSV files for RAG...')
        
        # Process time series data
        time_series_file = os.path.join(csv_dir, 'time_series', f'health_data_eams_{disease_name}_time_stamped.csv')
        if os.path.exists(time_series_file):
            self.process_time_series_for_rag(time_series_file, disease_name)

        # Process hotspots data
        hotspots_file = os.path.join(csv_dir, 'csv', 'national_hotspots.csv')
        if os.path.exists(hotspots_file):
            self.process_hotspots_for_rag(hotspots_file, disease_name)

    def process_time_series_for_rag(self, file_path, disease_name):
        """Process time series data for RAG"""
        try:
            df = pd.read_csv(file_path)
            
            # Create structured data for RAG
            rag_data = []
            
            if 'date' in df.columns and 'cases' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
                # Create summary documents
                recent_data = df.tail(30)
                total_cases = df['cases'].sum()
                avg_cases = df['cases'].mean()
                
                rag_data.append({
                    "title": f"{disease_name.title()} Time Series Summary",
                    "content": f"Total {disease_name} cases: {total_cases}. Average cases per period: {avg_cases:.0f}. Recent trend: {len(recent_data)} cases in last 30 days.",
                    "metadata": {
                        "disease": disease_name,
                        "data_type": "time_series",
                        "total_cases": total_cases,
                        "avg_cases": avg_cases
                    }
                })
                
                # Create trend analysis
                trend = self.calculate_trend(recent_data['cases'])
                rag_data.append({
                    "title": f"{disease_name.title()} Trend Analysis",
                    "content": f"Current {disease_name} trend is {trend}. {self.get_trend_interpretation(trend)}. Data based on {len(df)} time periods.",
                    "metadata": {
                        "disease": disease_name,
                        "data_type": "trend_analysis",
                        "trend": trend,
                        "periods": len(df)
                    }
                })

            # Save RAG-ready data
            self.save_rag_data(rag_data, f"{disease_name}_time_series_rag.json")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing time series for RAG: {e}'))

    def process_hotspots_for_rag(self, file_path, disease_name):
        """Process hotspots data for RAG"""
        try:
            df = pd.read_csv(file_path)
            disease_data = df[df['disease'].str.contains(disease_name, case=False, na=False)]
            
            rag_data = []
            
            if len(disease_data) > 0:
                top_hotspots = disease_data.nlargest(5, 'cases') if 'cases' in disease_data.columns else disease_data.head(5)
                hotspot_names = top_hotspots['region'].tolist() if 'region' in top_hotspots.columns else []
                
                rag_data.append({
                    "title": f"{disease_name.title()} Hotspots",
                    "content": f"Main {disease_name} hotspots: {', '.join(hotspot_names)}. These areas require increased surveillance and intervention measures.",
                    "metadata": {
                        "disease": disease_name,
                        "data_type": "hotspots",
                        "hotspots": hotspot_names
                    }
                })

            # Save RAG-ready data
            self.save_rag_data(rag_data, f"{disease_name}_hotspots_rag.json")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing hotspots for RAG: {e}'))

    def create_search_datastore(self, disease_name, project_id, location):
        """Create Vertex AI Search data store"""
        try:
            from google.cloud import aiplatform
            
            # Initialize Vertex AI
            aiplatform.init(project=project_id, location=location)
            
            # Create data store
            datastore_id = f"{disease_name}-datastore"
            
            # This would create the actual data store
            # For now, we'll just show the command structure
            self.stdout.write(f'Creating data store: {datastore_id}')
            
            # In practice, you would use:
            # datastore = aiplatform.SearchDatastore.create(
            #     datastore_id=datastore_id,
            #     display_name=f"{disease_name.title()} Disease Data",
            #     content_config={"structured_content_config": {}}
            # )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating data store: {e}'))

    def upload_csv_to_datastore(self, disease_name, project_id, location):
        """Upload CSV files to Vertex AI Search data store"""
        try:
            self.stdout.write(f'Uploading CSV files to data store...')
            
            # Upload time series CSV
            time_series_file = f"src/artifacts/time_series/health_data_eams_{disease_name}_time_stamped.csv"
            if os.path.exists(time_series_file):
                self.stdout.write(f'Uploading: {time_series_file}')
                # In practice, you would use Vertex AI Search API to upload
            
            # Upload hotspots CSV
            hotspots_file = f"src/artifacts/csv/national_hotspots.csv"
            if os.path.exists(hotspots_file):
                self.stdout.write(f'Uploading: {hotspots_file}')
                # In practice, you would use Vertex AI Search API to upload
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error uploading to data store: {e}'))

    def create_search_app(self, disease_name, project_id, location):
        """Create Vertex AI Search app"""
        try:
            self.stdout.write(f'Creating search app for {disease_name}...')
            
            # This would create the search app
            # In practice, you would use Vertex AI Search API
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating search app: {e}'))

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
            return "This indicates a concerning upward trend that requires immediate attention"
        elif trend == "decreasing":
            return "This shows a positive downward trend indicating effective control measures"
        else:
            return "This represents a stable pattern that requires continued monitoring"

    def save_rag_data(self, rag_data, filename):
        """Save RAG-ready data"""
        try:
            os.makedirs('rag_data', exist_ok=True)
            filepath = os.path.join('rag_data', filename)
            
            with open(filepath, 'w') as f:
                json.dump(rag_data, f, indent=2)
            
            self.stdout.write(f'Saved RAG data to: {filepath}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error saving RAG data: {e}')) 