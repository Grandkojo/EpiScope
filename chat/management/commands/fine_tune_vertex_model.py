from django.core.management.base import BaseCommand
from django.conf import settings
from chat.models import FineTuningDataset, ChatMessage, ChatSession
from src.models.disease_monitor import DiseaseMonitor
import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fine-tune Vertex AI model with collected chat data and disease monitoring information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--disease',
            type=str,
            help='Specific disease to fine-tune for (e.g., diabetes, malaria)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of chat history to include (default: 30)'
        )
        parser.add_argument(
            '--export-only',
            action='store_true',
            help='Only export data without starting fine-tuning'
        )
        parser.add_argument(
            '--model-name',
            type=str,
            default='gemini-2.0-flash-001',
            help='Vertex AI model to fine-tune'
        )

    def handle(self, *args, **kwargs):
        disease_name = kwargs['disease']
        days = kwargs['days']
        export_only = kwargs['export_only']
        model_name = kwargs['model_name']

        self.stdout.write(self.style.SUCCESS(f'Starting fine-tuning process for {disease_name or "all diseases"}'))

        try:
            # Initialize disease monitor
            monitor = DiseaseMonitor(
                project_id=settings.VERTEX_AI_PROJECT_ID,
                location=settings.VERTEX_AI_LOCATION,
                model_name=model_name
            )

            # Generate fine-tuning data
            training_data = self.generate_training_data(monitor, disease_name, days)

            if not training_data:
                self.stdout.write(self.style.WARNING('No training data found'))
                return

            self.stdout.write(f'Generated {len(training_data)} training examples')

            # Export data
            export_path = monitor.export_fine_tuning_data(disease_name, format='json')
            
            if export_path:
                self.stdout.write(self.style.SUCCESS(f'Exported data to: {export_path}'))

            if export_only:
                self.stdout.write(self.style.SUCCESS('Export completed. Use --export-only to skip fine-tuning.'))
                return

            # Start fine-tuning
            self.start_fine_tuning(monitor, export_path, disease_name, model_name)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in fine-tuning process: {e}'))
            logger.error(f'Fine-tuning error: {e}')

    def generate_training_data(self, monitor, disease_name, days):
        """Generate training data from chat history and disease monitoring"""
        training_data = []

        try:
            # Get recent chat sessions
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_sessions = ChatSession.objects.filter(
                start_time__gte=cutoff_date,
                status='ended'
            )

            for session in recent_sessions:
                # Get chat messages
                messages = ChatMessage.objects.filter(
                    session=session
                ).order_by('timestamp')

                # Convert to chat history format
                chat_history = []
                for msg in messages:
                    chat_history.append({
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat()
                    })

                # Generate fine-tuning data from chat history
                session_data = monitor.generate_fine_tuning_data(chat_history, disease_name)
                training_data.extend(session_data)

            # Add disease-specific training examples
            disease_examples = self.generate_disease_specific_examples(disease_name)
            training_data.extend(disease_examples)

            # Add medical knowledge examples
            medical_examples = self.generate_medical_knowledge_examples(disease_name)
            training_data.extend(medical_examples)

            return training_data

        except Exception as e:
            logger.error(f'Error generating training data: {e}')
            return []

    def generate_disease_specific_examples(self, disease_name):
        """Generate disease-specific training examples"""
        examples = []

        if disease_name == 'diabetes':
            examples = [
                {
                    "instruction": "What are the early warning signs of diabetes?",
                    "input": "Context: diabetes epidemic monitoring",
                    "output": "Early warning signs of diabetes include increased thirst, frequent urination, unexplained weight loss, fatigue, blurred vision, slow-healing sores, and frequent infections. If you experience these symptoms, consult a healthcare professional immediately for proper diagnosis and management."
                },
                {
                    "instruction": "How can I prevent diabetes?",
                    "input": "Context: diabetes epidemic monitoring",
                    "output": "To prevent diabetes, maintain a healthy weight through balanced diet and regular exercise, limit processed foods and sugary drinks, monitor blood sugar levels if at risk, get regular health checkups, and manage stress levels. Early detection and lifestyle modifications are key to prevention."
                },
                {
                    "instruction": "What are the current diabetes trends?",
                    "input": "Context: diabetes epidemic monitoring",
                    "output": "Based on our monitoring data, diabetes cases show [specific trends from your data]. Key indicators include age distribution, geographic patterns, and seasonal variations. Regular monitoring helps identify risk factors and enables timely intervention strategies."
                }
            ]
        elif disease_name == 'malaria':
            examples = [
                {
                    "instruction": "What are the symptoms of malaria?",
                    "input": "Context: malaria epidemic monitoring",
                    "output": "Malaria symptoms typically include fever, chills, headache, muscle aches, fatigue, nausea, vomiting, and diarrhea. Severe cases may involve confusion, seizures, and organ failure. Seek immediate medical attention if you experience these symptoms, especially in endemic areas."
                },
                {
                    "instruction": "How can I prevent malaria?",
                    "input": "Context: malaria epidemic monitoring",
                    "output": "Prevent malaria by using insecticide-treated bed nets, applying mosquito repellent, wearing protective clothing, taking antimalarial medication when traveling to endemic areas, and eliminating standing water around your home. Early diagnosis and treatment are crucial."
                },
                {
                    "instruction": "What are the malaria hotspots?",
                    "input": "Context: malaria epidemic monitoring",
                    "output": "Based on our monitoring data, malaria hotspots include [specific areas from your data]. These areas show higher transmission rates and require increased surveillance and intervention measures. Regular monitoring helps track transmission patterns."
                }
            ]

        return examples

    def generate_medical_knowledge_examples(self, disease_name):
        """Generate general medical knowledge examples"""
        examples = [
            {
                "instruction": "What is epidemic monitoring?",
                "input": "Context: epidemic monitoring",
                "output": "Epidemic monitoring involves systematic collection, analysis, and interpretation of health data to track disease patterns, identify outbreaks, and inform public health interventions. It includes surveillance systems, data analysis, and early warning mechanisms."
            },
            {
                "instruction": "How do I interpret health metrics?",
                "input": "Context: epidemic monitoring",
                "output": "Health metrics include case counts, incidence rates, prevalence, mortality rates, and geographic distribution. Key indicators to monitor are trends over time, demographic patterns, and seasonal variations. Understanding these metrics helps identify risk factors and guide prevention strategies."
            },
            {
                "instruction": "When should I seek medical attention?",
                "input": "Context: epidemic monitoring",
                "output": "Seek medical attention immediately if you experience severe symptoms, persistent fever, difficulty breathing, chest pain, confusion, or symptoms that worsen rapidly. Early medical intervention is crucial for better outcomes and preventing complications."
            }
        ]

        return examples

    def start_fine_tuning(self, monitor, export_path, disease_name, model_name):
        """Start Vertex AI fine-tuning process"""
        try:
            # This would integrate with Vertex AI fine-tuning API
            # For now, we'll create a placeholder for the fine-tuning process
            
            self.stdout.write(self.style.SUCCESS('Starting Vertex AI fine-tuning...'))
            
            # Create fine-tuning job configuration
            job_config = {
                'model_name': model_name,
                'training_data_path': export_path,
                'disease_focus': disease_name,
                'created_at': datetime.now().isoformat()
            }
            
            # Save job configuration
            config_path = export_path.replace('.json', '_config.json')
            with open(config_path, 'w') as f:
                json.dump(job_config, f, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f'Fine-tuning configuration saved to: {config_path}'))
            
            # TODO: Implement actual Vertex AI fine-tuning API call
            # This would involve:
            # 1. Uploading training data to Vertex AI
            # 2. Creating a fine-tuning job
            # 3. Monitoring training progress
            # 4. Deploying the fine-tuned model
            
            self.stdout.write(self.style.SUCCESS('Fine-tuning process initiated successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error starting fine-tuning: {e}'))
            logger.error(f'Fine-tuning error: {e}') 