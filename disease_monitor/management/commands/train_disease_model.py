from django.core.management.base import BaseCommand
from disease_monitor.models import HospitalHealthData, CommonSymptom, Disease
from src.models.disease_monitor import DiseaseMonitor
from src.utils.data_preparation import combine_and_label_datasets
import pandas as pd
import logging
import os
import shap
class Command(BaseCommand):
    help = 'Train disease prediction models for all diseases in the Disease table.'

    def handle(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
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

            # Sample negatives from patients who do NOT have this disease in their diagnosis
            neg_df = df[~df['principal_diagnosis_new'].str.contains(disease_name, case=False, na=False)].copy()
            if len(neg_df) == 0:
                print(f"Skipping {disease_name}: no negative samples found.")
                continue
            neg_df = neg_df.sample(n=n_pos, replace=True, random_state=42)

            # Use new utility to combine, label, and inject symptoms
            full_df = combine_and_label_datasets(pos_df, neg_df, target_col='target', disease_type=disease_name)
            full_df = full_df[full_df['target'].isin([0, 1])]

            if full_df['target'].nunique() < 2:
                print(f"Skipping {disease_name}: only one class present.")
                continue

            print(f"{disease_name.title()} class counts:\n", full_df['target'].value_counts())

            # Train model with new pipeline
            monitor = DiseaseMonitor()
            model, splits = monitor.train_with_validation(pos_df, neg_df, disease_type=disease_name, threshold=0.5)

            model_dir = os.path.join('models', disease_name)
            os.makedirs(model_dir, exist_ok=True)
            monitor.save_models(path=model_dir)

            # Generate SHAP explanations
            try:
                monitor.generate_shap_explanations(full_df, disease_name, path=model_dir)
            except Exception as e:
                print("DEBUG: About to call SHAP summary plot. SHAP version:", shap.__version__)
                import traceback
                logger.warning(f"SHAP generation failed for {disease_name}: {e}\n{traceback.format_exc()}")
                print(f"SHAP generation failed for {disease_name}: {e}")

            self.stdout.write(self.style.SUCCESS(f'{disease_name.title()} model trained and saved to {model_dir}'))
