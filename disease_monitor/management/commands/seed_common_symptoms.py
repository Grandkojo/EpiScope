from django.core.management.base import BaseCommand
from disease_monitor.models import Disease, CommonSymptom

class Command(BaseCommand):
    help = 'Seed the CommonSymptom model for Malaria and Diabetes (Ghana - Most Common Symptoms)'

    def handle(self, *args, **kwargs):
        # Malaria symptoms
        malaria_symptoms = [
            'Fever  - Sudden high temperature is the most common and early symptom.',
            'Headache  - Persistent and severe headaches often accompany fever.',
            'Chills and Shivering  - Often come before or during fever spikes.',
            'Sweating  - Especially after fever drops, excessive sweating is common.',
            'Nausea and Vomiting  - Gastrointestinal symptoms occur in many patients.',
            'Muscle and Joint Pain  - Body aches, especially in lower back and legs.',
            'Fatigue and Weakness  - General body weakness and tiredness.',
        ]
        # Diabetes symptoms
        diabetes_symptoms = [
            'Frequent Urination (Polyuria)  - Especially at night (nocturia).',
            'Excessive Thirst (Polydipsia)  - Due to fluid loss from frequent urination.',
            'Unexplained Weight Loss  - Despite normal or increased eating.',
            'Fatigue  - Persistent tiredness and low energy.',
            'Blurred Vision  - Due to fluctuating blood sugar levels.',
            'Slow-Healing Sores or Wounds  - Especially on the feet.',
            'Frequent Infections  - Urinary tract infections, skin infections, etc.',
        ]

        # Get or create Disease objects
        malaria, _ = Disease.objects.get_or_create(
            disease_name='Malaria',
            defaults={'description': 'Malaria is a life-threatening disease caused by parasites that are transmitted to people through the bites of infected female Anopheles mosquitoes.'}
        )
        diabetes, _ = Disease.objects.get_or_create(
            disease_name='Diabetes',
            defaults={'description': 'Diabetes is a chronic condition that affects the way your body uses and stores sugar.'}
        )

        # Seed Malaria symptoms
        for rank, symptom_full in enumerate(malaria_symptoms, start=1):
            if '-' in symptom_full:
                symptom, description = symptom_full.split('-', 1)
            elif '-' in symptom_full:
                symptom, description = symptom_full.split('-', 1)
            else:
                symptom, description = symptom_full, ''
            symptom = symptom.strip()[:100]
            description = description.strip()
            CommonSymptom.objects.update_or_create(
                disease=malaria,
                symptom=symptom,
                defaults={'description': description, 'rank': rank}
            )
        self.stdout.write(self.style.SUCCESS('Seeded Malaria common symptoms.'))

        # Seed Diabetes symptoms
        for rank, symptom_full in enumerate(diabetes_symptoms, start=1):
            if '-' in symptom_full:
                symptom, description = symptom_full.split('-', 1)
            elif '-' in symptom_full:
                symptom, description = symptom_full.split('-', 1)
            else:
                symptom, description = symptom_full, ''
            symptom = symptom.strip()[:100]
            description = description.strip()
            CommonSymptom.objects.update_or_create(
                disease=diabetes,
                symptom=symptom,
                defaults={'description': description, 'rank': rank}
            )
        self.stdout.write(self.style.SUCCESS('Seeded Diabetes common symptoms.')) 