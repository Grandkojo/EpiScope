from django.test import TestCase
from .models import DiabetesData, MeningitisData, CholeraData, Disease, DiseaseYear
from django.core.management import call_command
from io import StringIO

# Create your tests here.

class DiseaseModelTest(TestCase):
    def test_disease_str(self):
        disease = Disease.objects.create(disease_name='Diabetes', description='desc')
        self.assertEqual(str(disease), 'Disease Diabetes')

class DiseaseYearModelTest(TestCase):
    def test_disease_year_str(self):
        disease = Disease.objects.create(disease_name='Diabetes', description='desc')
        year = DiseaseYear.objects.create(periodname='2025', disease_id=disease, hot_spots='Yes', summary_data='No', case_count_summary='Yes')
        self.assertEqual(str(year), 'Disease Year 2025')

class ManagementCommandTest(TestCase):
    def test_seed_disease_command(self):
        out = StringIO()
        call_command('seed_disease', stdout=out)
        self.assertIn('Disease table seeded successfully', out.getvalue())
        self.assertTrue(Disease.objects.filter(disease_name='Diabetes').exists())

    def test_seed_disease_years_command(self):
        Disease.objects.create(id=1, disease_name='Diabetes', description='desc')
        Disease.objects.create(id=2, disease_name='Malaria', description='desc')
        Disease.objects.create(id=3, disease_name='Cholera', description='desc')
        Disease.objects.create(id=4, disease_name='Meningitis', description='desc')
        out = StringIO()
        call_command('seed_disease_years', stdout=out)
        self.assertIn('Disease_years table seeded successfully', out.getvalue())
        self.assertTrue(DiseaseYear.objects.filter(periodname='2020').exists())
