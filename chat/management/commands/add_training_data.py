from django.core.management.base import BaseCommand
from chat.models import FineTuningDataset
import json

class Command(BaseCommand):
    help = 'Add training data for Vertex AI fine-tuning'

    def add_arguments(self, parser):
        parser.add_argument(
            '--disease',
            type=str,
            required=True,
            help='Disease name (e.g., diabetes, malaria)'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='JSON file containing training examples'
        )
        parser.add_argument(
            '--instruction',
            type=str,
            help='Single instruction/prompt'
        )
        parser.add_argument(
            '--input',
            type=str,
            default='',
            help='Input context (optional)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Expected output/response'
        )
        parser.add_argument(
            '--source',
            type=str,
            default='manual_curation',
            choices=['chat_history', 'manual_curation', 'expert_knowledge', 'medical_literature'],
            help='Source of the training data'
        )
        parser.add_argument(
            '--quality-score',
            type=float,
            default=1.0,
            help='Quality score (0.0 to 1.0)'
        )
        parser.add_argument(
            '--approve',
            action='store_true',
            help='Automatically approve the training example'
        )

    def handle(self, *args, **kwargs):
        disease_name = kwargs['disease']
        file_path = kwargs['file']
        instruction = kwargs['instruction']
        input_text = kwargs['input']
        output_text = kwargs['output']
        source = kwargs['source']
        quality_score = kwargs['quality_score']
        approve = kwargs['approve']

        if file_path:
            self.add_from_file(disease_name, file_path)
        elif instruction and output_text:
            self.add_single_example(disease_name, instruction, input_text, output_text, source, quality_score, approve)
        else:
            self.stdout.write(self.style.ERROR('Please provide either --file or both --instruction and --output'))

    def add_from_file(self, disease_name, file_path):
        """Add training examples from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            count = 0
            for example in data:
                if isinstance(example, dict):
                    instruction = example.get('instruction', '')
                    input_text = example.get('input', '')
                    output_text = example.get('output', '')
                    
                    if instruction and output_text:
                        FineTuningDataset.objects.create(
                            disease_name=disease_name,
                            instruction=instruction,
                            input_text=input_text,
                            output_text=output_text,
                            source='manual_curation',
                            quality_score=1.0,
                            is_approved=True
                        )
                        count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Successfully added {count} training examples for {disease_name}')
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error adding data: {e}'))

    def add_single_example(self, disease_name, instruction, input_text, output_text, source, quality_score, approve):
        """Add a single training example"""
        try:
            example = FineTuningDataset.objects.create(
                disease_name=disease_name,
                instruction=instruction,
                input_text=input_text,
                output_text=output_text,
                source=source,
                quality_score=quality_score,
                is_approved=approve
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully added training example for {disease_name}')
            )
            self.stdout.write(f'Instruction: {instruction[:100]}...')
            self.stdout.write(f'Output: {output_text[:100]}...')
            self.stdout.write(f'Status: {"Approved" if approve else "Pending approval"}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error adding training example: {e}')) 