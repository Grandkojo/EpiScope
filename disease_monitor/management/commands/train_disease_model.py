from django.core.management.base import BaseCommand
from disease_monitor.models import HospitalHealthData, Disease
from src.models.disease_monitor import DiseaseMonitor
import pandas as pd
import logging
import os
import shap

class Command(BaseCommand):
    help = 'Train disease prediction models for all diseases in the Disease table using Vertex AI.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=str,
            required=True,
            help='Google Cloud project ID for Vertex AI'
        )
        parser.add_argument(
            '--location',
            type=str,
            default='us-central1',
            help='Google Cloud location (default: us-central1)'
        )
        parser.add_argument(
            '--model-name',
            type=str,
            default='gemini-2.0-flash-001',
            help='Vertex AI model name (default: gemini-2.0-flash-001)'
        )

    def handle(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        
        # Get Vertex AI configuration
        project_id = kwargs['project_id']
        location = kwargs['location']
        model_name = kwargs['model_name']
        
        logger.info(f'Initializing DiseaseMonitor with Vertex AI (Project: {project_id}, Location: {location})')
        
        # Initialize DiseaseMonitor with Vertex AI
        monitor = DiseaseMonitor(
            project_id=project_id,
            location=location,
            model_name=model_name
        )
        
        logger.info('Loading HospitalHealthData...')
        qs = HospitalHealthData.objects.all()
        data = list(qs.values())
        if not data:
            self.stdout.write(self.style.ERROR('No data found in HospitalHealthData.'))
            return

        df = pd.DataFrame(data)
        all_diseases = Disease.objects.all()

        for disease_obj in all_diseases:
            disease_name = disease_obj.disease_name.lower()
            print(f"\n=== Training for {disease_name} ===")

            # Filter positive cases
            pos_df = df[df['principal_diagnosis_new'].str.contains(disease_name, case=False, na=False)].copy()
            n_pos = len(pos_df)
            if n_pos == 0:
                print(f"Skipping {disease_name}: no positive samples found.")
                continue

            print(f"{disease_name.title()} positive cases: {n_pos}")

            # Generate negative cases using the full dataset
            neg_df = monitor.generate_negative_cases(df, disease_name, n_negative=n_pos)
            n_neg = len(neg_df)
            print(f"{disease_name.title()} negative cases: {n_neg}")

            # Train model with both positive and negative cases
            model, splits = monitor.train_with_validation(pos_df, neg_df, disease_type=disease_name, threshold=0.7)

            model_dir = os.path.join('models', disease_name)
            os.makedirs(model_dir, exist_ok=True)
            monitor.save_models(path=model_dir)

            # Generate SHAP explanations
            try:
                # Use combined dataset for SHAP analysis
                combined_df = pd.concat([pos_df, neg_df], ignore_index=True)
                monitor.generate_shap_explanations(combined_df, disease_name, path=model_dir)
            except Exception as e:
                print("DEBUG: About to call SHAP summary plot. SHAP version:", shap.__version__)
                import traceback
                logger.warning(f"SHAP generation failed for {disease_name}: {e}\n{traceback.format_exc()}")
                print(f"SHAP generation failed for {disease_name}: {e}")

            self.stdout.write(self.style.SUCCESS(f'{disease_name.title()} model trained and saved to {model_dir}'))
