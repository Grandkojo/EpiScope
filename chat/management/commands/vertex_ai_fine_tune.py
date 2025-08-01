from django.core.management.base import BaseCommand
from django.conf import settings
import json
import os
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fine-tune Vertex AI model with actual API calls'

    def add_arguments(self, parser):
        parser.add_argument(
            '--training-data',
            type=str,
            required=True,
            help='Path to training data JSON file'
        )
        parser.add_argument(
            '--disease',
            type=str,
            required=True,
            help='Disease name for the fine-tuned model'
        )
        parser.add_argument(
            '--base-model',
            type=str,
            default='gemini-2.0-flash-001',
            help='Base model to fine-tune'
        )
        parser.add_argument(
            '--epochs',
            type=int,
            default=3,
            help='Number of training epochs'
        )

    def handle(self, *args, **kwargs):
        training_data_path = kwargs['training_data']
        disease_name = kwargs['disease']
        base_model = kwargs['base_model']
        epochs = kwargs['epochs']

        self.stdout.write(f'Starting Vertex AI fine-tuning for {disease_name}')

        try:
            # Step 1: Validate training data
            training_data = self.load_training_data(training_data_path)
            
            # Step 2: Upload data to Vertex AI
            gcs_uri = self.upload_to_gcs(training_data, disease_name)
            
            # Step 3: Create fine-tuning job
            job_name = self.create_fine_tuning_job(disease_name, base_model, gcs_uri, epochs)
            
            # Step 4: Monitor training progress
            self.monitor_training(job_name)
            
            # Step 5: Deploy the fine-tuned model
            model_endpoint = self.deploy_model(job_name, disease_name)
            
            self.stdout.write(
                self.style.SUCCESS(f'Fine-tuning completed! Model endpoint: {model_endpoint}')
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Fine-tuning failed: {e}'))
            logger.error(f'Fine-tuning error: {e}')

    def load_training_data(self, file_path):
        """Load and validate training data"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Validate format
            for example in data:
                if not all(key in example for key in ['instruction', 'output']):
                    raise ValueError("Training data must contain 'instruction' and 'output' fields")
            
            self.stdout.write(f'Loaded {len(data)} training examples')
            return data
            
        except Exception as e:
            raise Exception(f'Error loading training data: {e}')

    def upload_to_gcs(self, training_data, disease_name):
        """Upload training data to Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            # Initialize GCS client
            storage_client = storage.Client(project=settings.VERTEX_AI_PROJECT_ID)
            
            # Create bucket name
            bucket_name = f"{settings.VERTEX_AI_PROJECT_ID}-fine-tuning-data"
            
            # Create bucket if it doesn't exist
            try:
                bucket = storage_client.create_bucket(bucket_name)
            except:
                bucket = storage_client.bucket(bucket_name)
            
            # Upload training data
            blob_name = f"{disease_name}/training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            blob = bucket.blob(blob_name)
            
            # Convert to Vertex AI format
            vertex_format = []
            for example in training_data:
                vertex_format.append({
                    "input_text": example.get('input', ''),
                    "output_text": example['output'],
                    "instruction": example['instruction']
                })
            
            blob.upload_from_string(
                json.dumps(vertex_format, indent=2),
                content_type='application/json'
            )
            
            gcs_uri = f"gs://{bucket_name}/{blob_name}"
            self.stdout.write(f'Uploaded training data to: {gcs_uri}')
            
            return gcs_uri
            
        except Exception as e:
            raise Exception(f'Error uploading to GCS: {e}')

    def create_fine_tuning_job(self, disease_name, base_model, gcs_uri, epochs):
        """Create Vertex AI fine-tuning job"""
        try:
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel
            
            # Initialize Vertex AI
            vertexai.init(project=settings.VERTEX_AI_PROJECT_ID, location=settings.VERTEX_AI_LOCATION)
            
            # Create fine-tuning job
            model = GenerativeModel(base_model)
            
            # Fine-tuning configuration
            tuning_job = model.tune_model(
                training_data=gcs_uri,
                tuning_job_spec={
                    "base_model": base_model,
                    "tuning_task": {
                        "supervised_tuning_spec": {
                            "training_dataset_uri": gcs_uri,
                            "validation_dataset_uri": gcs_uri,  # Using same data for validation
                            "hyper_parameters": {
                                "epoch_count": epochs,
                                "learning_rate": 0.001,
                                "batch_size": 4
                            }
                        }
                    }
                }
            )
            
            job_name = tuning_job.name
            self.stdout.write(f'Created fine-tuning job: {job_name}')
            
            return job_name
            
        except Exception as e:
            raise Exception(f'Error creating fine-tuning job: {e}')

    def monitor_training(self, job_name):
        """Monitor fine-tuning job progress"""
        try:
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel
            
            self.stdout.write('Monitoring training progress...')
            
            while True:
                # Get job status
                job = GenerativeModel.get_tuning_job(job_name)
                state = job.state
                
                self.stdout.write(f'Training status: {state}')
                
                if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                    break
                
                time.sleep(60)  # Check every minute
            
            if state == 'SUCCEEDED':
                self.stdout.write(self.style.SUCCESS('Training completed successfully!'))
            else:
                raise Exception(f'Training failed with state: {state}')
                
        except Exception as e:
            raise Exception(f'Error monitoring training: {e}')

    def deploy_model(self, job_name, disease_name):
        """Deploy the fine-tuned model"""
        try:
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel
            
            # Get the fine-tuned model
            job = GenerativeModel.get_tuning_job(job_name)
            model_name = job.tuned_model_name
            
            # Deploy the model
            model = GenerativeModel(model_name)
            endpoint = model.deploy(
                deployed_model_display_name=f"{disease_name}-fine-tuned-model",
                traffic_split={"0": 100}
            )
            
            endpoint_name = endpoint.name
            self.stdout.write(f'Model deployed to endpoint: {endpoint_name}')
            
            # Save endpoint info for later use
            self.save_endpoint_info(disease_name, endpoint_name, model_name)
            
            return endpoint_name
            
        except Exception as e:
            raise Exception(f'Error deploying model: {e}')

    def save_endpoint_info(self, disease_name, endpoint_name, model_name):
        """Save endpoint information for later use"""
        try:
            endpoint_info = {
                'disease_name': disease_name,
                'endpoint_name': endpoint_name,
                'model_name': model_name,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Save to file
            os.makedirs('model_endpoints', exist_ok=True)
            with open(f'model_endpoints/{disease_name}_endpoint.json', 'w') as f:
                json.dump(endpoint_info, f, indent=2)
            
            self.stdout.write(f'Saved endpoint info for {disease_name}')
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not save endpoint info: {e}')) 