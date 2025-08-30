#!/usr/bin/env python3
"""
Django management command to run reinforcement learning training for XGBoost models
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import os
import sys

# Add the disease_monitor directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from reinforcement_xgboost_training import ReinforcementXGBoostTrainer


class Command(BaseCommand):
    help = 'Run reinforcement learning training for XGBoost models using prediction history data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--disease-type',
            type=str,
            choices=['diabetes', 'malaria', 'both'],
            default='both',
            help='Disease type to train (diabetes, malaria, or both)'
        )
        
        parser.add_argument(
            '--period-days',
            type=int,
            default=30,
            help='Number of days to look back for reinforcement learning data (default: 30)'
        )
        
        parser.add_argument(
            '--min-confidence',
            type=float,
            default=0.7,
            help='Minimum confidence score for reinforcement learning data (default: 0.7)'
        )
        
        parser.add_argument(
            '--base-data-path',
            type=str,
            help='Path to base training data CSV file (optional)'
        )
        
        parser.add_argument(
            '--base-model-path',
            type=str,
            help='Path to base model file (optional)'
        )
        
        parser.add_argument(
            '--output-dir',
            type=str,
            default='src/artifacts/models',
            help='Output directory for trained models (default: src/artifacts/models)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Reinforcement Learning XGBoost Training')
        )
        self.stdout.write('=' * 60)
        
        disease_type = options['disease_type']
        period_days = options['period_days']
        min_confidence = options['min_confidence']
        base_data_path = options['base_data_path']
        base_model_path = options['base_model_path']
        output_dir = options['output_dir']
        
        # Validate output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine which diseases to train
        diseases_to_train = []
        if disease_type == 'both':
            diseases_to_train = ['diabetes', 'malaria']
        else:
            diseases_to_train = [disease_type]
        
        results = {}
        
        for disease in diseases_to_train:
            self.stdout.write(f"\n🎯 Training {disease.title()} Model with Reinforcement Learning")
            self.stdout.write('-' * 50)
            
            try:
                # Set default paths if not provided
                if not base_data_path:
                    base_data_path = f"src/artifacts/formatted/{disease}_balanced_formatted.csv"
                
                if not base_model_path:
                    base_model_path = f"src/artifacts/models/{disease}_xgboost_model_v2.pkl"
                
                # Initialize trainer
                trainer = ReinforcementXGBoostTrainer(
                    disease_type=disease,
                    base_model_path=base_model_path if os.path.exists(base_model_path) else None
                )
                
                # Run training
                success = trainer.run_reinforcement_training(
                    base_data_path=base_data_path,
                    period_days=period_days,
                    min_confidence=min_confidence
                )
                
                results[disease] = success
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {disease.title()} reinforcement learning training completed")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {disease.title()} reinforcement learning training failed")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error training {disease} model: {str(e)}")
                )
                results[disease] = False
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("REINFORCEMENT LEARNING TRAINING SUMMARY")
        self.stdout.write("=" * 60)
        
        for disease, success in results.items():
            status = "✅ COMPLETED" if success else "❌ FAILED"
            self.stdout.write(f"{disease.title()}: {status}")
        
        # Print output information
        self.stdout.write(f"\n📁 Models saved to: {output_dir}")
        self.stdout.write("📁 SHAP plots saved to: src/artifacts/reinforcement_shap_plots/")
        
        # Check if any training was successful
        if any(results.values()):
            self.stdout.write(
                self.style.SUCCESS("\n🎉 Reinforcement learning training completed successfully!")
            )
        else:
            self.stdout.write(
                self.style.ERROR("\n💥 All reinforcement learning training failed!")
            )
            raise CommandError("Reinforcement learning training failed for all diseases") 