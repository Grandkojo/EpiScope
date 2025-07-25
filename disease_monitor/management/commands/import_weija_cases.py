import pandas as pd
from django.core.management.base import BaseCommand
from disease_monitor.models import HospitalHealthData
from datetime import datetime
import os
from django.conf import settings

DIABETES_CSV = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_diabetes_time_stamped.csv')
MALARIA_CSV = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_malaria_time_stamped.csv')

FIELD_MAP = {
    'Address (Locality)': 'address_locality',
    'Age': 'age',
    'Sex': 'sex',
    'Principal Diagnosis (New Case)': 'principal_diagnosis_new',
    'Additional Diagnosis (New Case)': 'additional_diagnosis_new',
    'Pregnant Patient': 'pregnant_patient',
    'NHIA Patient': 'nhia_patient',
    'Month': 'month',
    'orgname': 'orgname',
}

class Command(BaseCommand):
    help = 'Import Weija diabetes and malaria cases into HospitalHealthData model.'

    def handle(self, *args, **kwargs):
        for csv_path in [DIABETES_CSV, MALARIA_CSV]:
            if not os.path.exists(csv_path):
                self.stderr.write(self.style.ERROR(f'CSV not found: {csv_path}'))
                continue
            df = pd.read_csv(csv_path)
            # Filter for Weija only (should already be, but just in case)
            df = df[df['orgname'].str.lower() == 'weija']
            # --- Group rows by month-level data for day assignment ---
            month_rows = {}
            full_date_rows = []
            for idx, row in df.iterrows():
                val = row.get('Month', None)
                if isinstance(val, str):
                    val = val.strip()
                    # MM-YYYY
                    if len(val) == 7 and '-' in val and val[2] == '-':
                        key = datetime.strptime(val, '%m-%Y').strftime('%Y-%m')
                        month_rows.setdefault(key, []).append((idx, row))
                    # YYYY-MM
                    elif len(val) == 7 and '-' in val and val[4] == '-':
                        key = datetime.strptime(val, '%Y-%m').strftime('%Y-%m')
                        month_rows.setdefault(key, []).append((idx, row))
                    # DD-MM-YYYY
                    elif len(val) == 10 and '-' in val and val[2] == '-' and val[5] == '-':
                        full_date_rows.append((idx, row))
                    # YYYY-MM-DD
                    elif len(val) == 10 and '-' in val and val[4] == '-' and val[7] == '-':
                        full_date_rows.append((idx, row))
                    else:
                        full_date_rows.append((idx, row))
                else:
                    full_date_rows.append((idx, row))

            # Assign days to month-level rows
            from calendar import monthrange
            records = []
            # First, handle full-date rows
            for idx, row in full_date_rows:
                data = {}
                for csv_col, model_field in FIELD_MAP.items():
                    val = row.get(csv_col, None)
                    if model_field == 'month' and isinstance(val, str):
                        val = val.strip()
                        parsed = None
                        # DD-MM-YYYY
                        if len(val) == 10 and '-' in val and val[2] == '-' and val[5] == '-':
                            try:
                                parsed = datetime.strptime(val, '%d-%m-%Y').date()
                            except Exception:
                                parsed = None
                        # YYYY-MM-DD
                        elif len(val) == 10 and '-' in val and val[4] == '-' and val[7] == '-':
                            try:
                                parsed = datetime.strptime(val, '%Y-%m-%d').date()
                            except Exception:
                                parsed = None
                        val = parsed
                    data[model_field] = val
                if not HospitalHealthData.objects.filter(
                    orgname=data['orgname'],
                    address_locality=data['address_locality'],
                    age=data['age'],
                    sex=data['sex'],
                    principal_diagnosis_new=data['principal_diagnosis_new'],
                    month=data['month']
                ).exists():
                    records.append(HospitalHealthData(**data))
            # Now, handle month-level rows
            for key, rows in month_rows.items():
                year, month = map(int, key.split('-'))
                num_days = monthrange(year, month)[1]
                total_rows = len(rows)
                base_rows_per_day = total_rows // num_days
                extra = total_rows % num_days
                # Build a list of day assignments
                day_assignments = []
                for day in range(1, num_days + 1):
                    count = base_rows_per_day + (1 if day <= extra else 0)
                    day_assignments.extend([day] * count)
                # If there are any rounding issues, trim or extend
                day_assignments = day_assignments[:total_rows]
                for (i, (idx, row)) in enumerate(rows):
                    day = day_assignments[i]
                    data = {}
                    for csv_col, model_field in FIELD_MAP.items():
                        val = row.get(csv_col, None)
                        if model_field == 'month':
                            val = datetime(year, month, day).date()
                        data[model_field] = val
                    if not HospitalHealthData.objects.filter(
                        orgname=data['orgname'],
                        address_locality=data['address_locality'],
                        age=data['age'],
                        sex=data['sex'],
                        principal_diagnosis_new=data['principal_diagnosis_new'],
                        month=data['month']
                    ).exists():
                        records.append(HospitalHealthData(**data))
    
            HospitalHealthData.objects.bulk_create(records, batch_size=500)
            self.stdout.write(self.style.SUCCESS(f'Imported {len(records)} records from {os.path.basename(csv_path)}')) 