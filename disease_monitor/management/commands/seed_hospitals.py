from django.core.management.base import BaseCommand
from django.db import transaction
from disease_monitor.models import Hospital


class Command(BaseCommand):
    help = 'Seed the Hospital model with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing hospital data before seeding',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        clear = options['clear']
        dry_run = options['dry_run']

        # Initial hospital data
        hospitals_data = [
            {
                'name': 'Weija Hospital',
                'slug': 'weija', 
            },
            # Add more hospitals here as needed
        ]

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN - No changes will be made')
            )
            self.stdout.write('Would create the following hospitals:')
            for hospital_data in hospitals_data:
                self.stdout.write(f"  - {hospital_data['name']} (slug: {hospital_data['slug']})")
            return

        try:
            with transaction.atomic():
                if clear:
                    deleted_count = Hospital.objects.all().delete()[0]
                    self.stdout.write(
                        self.style.SUCCESS(f'Cleared {deleted_count} existing hospital(s)')
                    )

                created_hospitals = []
                for hospital_data in hospitals_data:
                    hospital, created = Hospital.objects.get_or_create(
                        name=hospital_data['name'],
                        defaults={'slug': hospital_data['slug']}
                    )
                    
                    if created:
                        created_hospitals.append(hospital)
                        self.stdout.write(
                            self.style.SUCCESS(f'Created hospital: {hospital.name} (slug: {hospital.slug})')
                        )
                    else:
                        # Update slug if it's different
                        if hospital.slug != hospital_data['slug']:
                            hospital.slug = hospital_data['slug']
                            hospital.save()
                            self.stdout.write(
                                self.style.WARNING(f'Updated slug for {hospital.name}: {hospital.slug}')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'Hospital already exists: {hospital.name}')
                            )

                total_hospitals = Hospital.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nSeeding completed successfully!'
                        f'\nCreated: {len(created_hospitals)} new hospital(s)'
                        f'\nTotal hospitals in database: {total_hospitals}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during seeding: {str(e)}')
            )
            raise 