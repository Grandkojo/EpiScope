from django.core.management.base import BaseCommand
from disease_monitor.models import DiseaseYear, Disease

class Command(BaseCommand):
    help = 'Seed the disease_years table'

    def handle(self, *args, **kwargs):
        disease_years = [
            {'periodname': '2020', 'disease_id': 1, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2020', 'disease_id': 2, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2020', 'disease_id': 3, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2020', 'disease_id': 4, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2021', 'disease_id': 1, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2021', 'disease_id': 2, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2021', 'disease_id': 3, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2021', 'disease_id': 4, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2022', 'disease_id': 1, 'hot_spots': 'Yes', 'summary_data': 'Yes', 'case_count_summary': 'Yes'},
            {'periodname': '2022', 'disease_id': 2, 'hot_spots': 'Yes', 'summary_data': 'Yes', 'case_count_summary': 'Yes'},
            {'periodname': '2022', 'disease_id': 3, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2022', 'disease_id': 4, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2023', 'disease_id': 1, 'hot_spots': 'Yes', 'summary_data': 'Yes', 'case_count_summary': 'Yes'},
            {'periodname': '2023', 'disease_id': 2, 'hot_spots': 'Yes', 'summary_data': 'Yes', 'case_count_summary': 'Yes'},
            {'periodname': '2023', 'disease_id': 3, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2023', 'disease_id': 4, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2024', 'disease_id': 1, 'hot_spots': 'Yes', 'summary_data': 'Yes', 'case_count_summary': 'Yes'},
            {'periodname': '2024', 'disease_id': 2, 'hot_spots': 'Yes', 'summary_data': 'Yes', 'case_count_summary': 'Yes'},
            {'periodname': '2024', 'disease_id': 3, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2024', 'disease_id': 4, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2025', 'disease_id': 1, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2025', 'disease_id': 2, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2025', 'disease_id': 3, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'},
            {'periodname': '2025', 'disease_id': 4, 'hot_spots': 'Yes', 'summary_data': 'No', 'case_count_summary': 'Yes'}, 
        ]

        for disease_year in disease_years:
            # Get the Disease instance
            disease = Disease.objects.get(id=disease_year['disease_id'])
            # Create DiseaseYear with the Disease instance
            DiseaseYear.objects.create(
                periodname=disease_year['periodname'],
                disease_id=disease,
                hot_spots=disease_year['hot_spots'],
                summary_data=disease_year['summary_data'],
                case_count_summary=disease_year['case_count_summary']
            )
            self.stdout.write(f"Created disease_year: {disease_year['periodname']} for disease {disease.disease_name}")

        self.stdout.write(self.style.SUCCESS('Disease_years table seeded successfully'))

