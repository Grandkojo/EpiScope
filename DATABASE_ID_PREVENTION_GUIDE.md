# Database ID Prevention Guide

## The Problem
When data is inserted into Django models without proper ID handling, you can end up with NULL primary keys, which causes:
- Analytics queries returning 0 values
- Django ORM operations failing
- Inconsistent data behavior between development and production

## Root Causes
1. **Direct SQL INSERT statements** bypassing Django ORM
2. **Bulk operations** that don't properly handle auto-incrementing IDs
3. **Data migration scripts** using raw SQL instead of Django ORM
4. **Missing sequences** for auto-incrementing primary keys

## Prevention Strategies

### 1. Always Use Django ORM for Data Insertion

#### ✅ Good Examples:
```python
# Single record creation
HospitalHealthData.objects.create(
    orgname='Weija',
    address_locality='KASOA',
    age=45,
    sex='Female',
    principal_diagnosis_new='E1101 [Type 2 diabetes]',
    pregnant_patient=False,
    nhia_patient=True,
    month=date(2023, 3, 15)
)

# Bulk creation with proper model instances
records = []
for data in csv_data:
    record = HospitalHealthData(**data)
    records.append(record)

HospitalHealthData.objects.bulk_create(records, batch_size=500)
```

#### ❌ Bad Examples:
```python
# Direct SQL INSERT - AVOID THIS
cursor.execute("""
    INSERT INTO disease_monitor_hospitalhealthdata 
    (orgname, address_locality, age, sex, principal_diagnosis_new, ...)
    VALUES (%s, %s, %s, %s, %s, ...)
""", values)
```

### 2. Proper Model Configuration

Ensure your models have proper primary key configuration:

```python
class HospitalHealthData(models.Model):
    # Django automatically creates 'id' field as AutoField(primary_key=True)
    orgname = models.CharField(max_length=100)
    address_locality = models.CharField(max_length=255)
    # ... other fields
    
    class Meta:
        indexes = [
            models.Index(fields=['orgname', 'month']),
        ]
```

### 3. Safe Data Import Patterns

#### For CSV/Excel Data:
```python
import pandas as pd
from django.core.management.base import BaseCommand
from disease_monitor.models import HospitalHealthData

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        df = pd.read_csv('data.csv')
        
        # Convert DataFrame to model instances
        records = []
        for _, row in df.iterrows():
            # Clean and validate data
            record = HospitalHealthData(
                orgname=row['orgname'],
                address_locality=row['locality'],
                age=int(row['age']),
                sex=row['sex'],
                principal_diagnosis_new=row['diagnosis'],
                pregnant_patient=bool(row['pregnant']),
                nhia_patient=bool(row['nhia']),
                month=pd.to_datetime(row['month']).date()
            )
            records.append(record)
        
        # Use bulk_create for efficiency
        HospitalHealthData.objects.bulk_create(records, batch_size=500)
```

#### For Database Migrations:
```python
# Use Django's transaction management
from django.db import transaction

@transaction.atomic
def migrate_data():
    # Your migration logic here
    pass
```

### 4. Validation and Testing

#### Pre-deployment Checklist:
- [ ] All data insertion uses Django ORM
- [ ] No direct SQL INSERT statements
- [ ] Primary keys are properly configured
- [ ] Auto-increment sequences are set up
- [ ] Test data insertion in development first
- [ ] Verify analytics queries work correctly

#### Testing Queries:
```python
# Test that IDs are properly set
assert HospitalHealthData.objects.filter(id__isnull=True).count() == 0

# Test analytics queries
diabetes_count = HospitalHealthData.objects.filter(
    principal_diagnosis_new__icontains='diabetes'
).count()
assert diabetes_count > 0
```

### 5. When You Must Use Raw SQL

If you absolutely need to use raw SQL:

```python
# Include proper ID generation
cursor.execute("""
    INSERT INTO disease_monitor_hospitalhealthdata 
    (id, orgname, address_locality, age, sex, principal_diagnosis_new, ...)
    SELECT 
        nextval('disease_monitor_hospitalhealthdata_id_seq'),
        %s, %s, %s, %s, %s, ...
""", values)

# Or use Django's raw() method
HospitalHealthData.objects.raw("""
    SELECT * FROM disease_monitor_hospitalhealthdata 
    WHERE principal_diagnosis_new ILIKE '%%diabetes%%'
""")
```

### 6. Monitoring and Detection

#### Add monitoring to detect NULL IDs:
```python
def check_for_null_ids():
    """Check for NULL IDs in critical tables"""
    null_counts = {
        'HospitalHealthData': HospitalHealthData.objects.filter(id__isnull=True).count(),
        'HospitalLocalities': HospitalLocalities.objects.filter(id__isnull=True).count(),
    }
    
    for table, count in null_counts.items():
        if count > 0:
            logger.error(f"Found {count} records with NULL IDs in {table}")
            # Send alert or notification
```

## Emergency Fix Script

If you encounter NULL ID issues, use the `fix_production_ids.py` script:

```bash
python fix_production_ids.py
```

This script will:
1. Detect NULL IDs in all tables
2. Create temporary tables with proper IDs
3. Replace original tables
4. Set up proper sequences
5. Verify the fix

## Best Practices Summary

1. **Always use Django ORM** for data operations
2. **Test thoroughly** in development before production
3. **Use transactions** for data consistency
4. **Monitor for NULL IDs** regularly
5. **Have a backup plan** (like the fix script)
6. **Document your data import processes**
7. **Use Django management commands** for data operations

## Common Pitfalls to Avoid

1. **Bypassing Django ORM** with direct SQL
2. **Not testing** data import scripts in development
3. **Ignoring primary key constraints**
4. **Using raw SQL** without proper ID handling
5. **Not monitoring** for data integrity issues
6. **Rushing deployments** without proper testing

By following these guidelines, you can prevent NULL ID issues and ensure your analytics work correctly in both development and production environments. 