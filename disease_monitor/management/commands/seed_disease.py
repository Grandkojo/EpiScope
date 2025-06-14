from django.core.management.base import BaseCommand
from disease_monitor.models import Disease

class Command(BaseCommand):
    help = 'Seed the disease table'

    def handle(self, *args, **kwargs):
        diseases = [
            {'disease_name': 'Diabetes', 'description': 'Diabetes is a chronic condition that affects the way your body uses and stores sugar.'},
            {'disease_name': 'Malaria', 'description': 'Malaria is a life-threatening disease caused by parasites that are transmitted to people through the bites of infected female Anopheles mosquitoes.'},
            {'disease_name': 'Cholera', 'description': 'Cholera is an acute diarrheal infection caused by ingestion of food or water contaminated with the bacterium Vibrio cholerae.'},
            {'disease_name': 'Meningitis', 'description': 'Meningitis is an inflammation of the protective membranes covering the brain and spinal cord, usually caused by an infection.'},
        ]
        
        for disease in diseases:
            Disease.objects.create(**disease)
            self.stdout.write(f"Created disease: {disease['disease_name']}")
        
        self.stdout.write(self.style.SUCCESS('Disease table seeded successfully'))
        