from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from disease_monitor.prediction_service import PredictionHistoryService
import argparse

User = get_user_model()

class Command(BaseCommand):
    help = 'Manually trigger reinforcement learning training'

    def add_arguments(self, parser):
        parser.add_argument(
            '--disease-type',
            type=str,
            help='Disease type to train for (e.g., diabetes, hypertension)',
            required=False
        )
        parser.add_argument(
            '--min-confidence',
            type=float,
            default=0.0,
            help='Minimum confidence score for predictions to include (default: 0.0)'
        )
        parser.add_argument(
            '--force-retrain',
            action='store_true',
            help='Force retraining even if model exists'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to run training for (admin only)',
            required=False
        )

    def handle(self, *args, **options):
        try:
            disease_type = options['disease_type']
            min_confidence = options['min_confidence']
            force_retrain = options['force_retrain']
            user_id = options['user_id']

            self.stdout.write(
                self.style.SUCCESS(f'🚀 Triggering reinforcement learning...')
            )
            
            if disease_type:
                self.stdout.write(f'   Disease Type: {disease_type}')
            else:
                self.stdout.write(f'   Disease Type: All diseases')
            
            self.stdout.write(f'   Min Confidence: {min_confidence}')
            self.stdout.write(f'   Force Retrain: {force_retrain}')

            # Trigger reinforcement learning
            result = PredictionHistoryService.trigger_reinforcement_learning(
                disease_type=disease_type,
                min_confidence=min_confidence,
                force_retrain=force_retrain
            )

            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Reinforcement learning triggered successfully!')
                )
                self.stdout.write(f'   Predictions processed: {result["predictions_count"]}')
                self.stdout.write(f'   Training session ID: {result["training_session_id"]}')
                self.stdout.write(f'   Aggregated data ID: {result["aggregated_data_id"]}')
                self.stdout.write(f'   Period: {result["period_start"]} to {result["period_end"]}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to trigger reinforcement learning: {result["message"]}')
                )

        except Exception as e:
            raise CommandError(f'Error triggering reinforcement learning: {str(e)}') 