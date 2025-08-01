from django.db import models
import json
import re

# Create your models here.

class RegionPopulation(models.Model):
    region = models.CharField(max_length=100)
    periodname = models.CharField(max_length=100)
    population = models.IntegerField()
    
    class Meta:
        db_table = 'region_population'
        verbose_name = 'Region Population'
        verbose_name_plural = 'Region Populations'
        unique_together = ['region', 'periodname']
        ordering = ['-periodname', 'region']

    def __str__(self):
        return f"{self.region} - {self.periodname} ({self.population:,})"

class DiabetesData(models.Model):
    periodname = models.CharField(max_length=100, primary_key=True)
    diabetes_mellitus = models.IntegerField(db_column='Diabetes Mellitus')
    diabetes_mellitus_female = models.IntegerField(db_column='Diabetes Mellitus +AC0- Female')
    diabetes_mellitus_male = models.IntegerField(db_column='Diabetes Mellitus +AC0- Male')
    diabetes_mellitus_deaths = models.IntegerField(db_column='Diabetes mellitus deaths')
    diabetes_mellitus_lab_confirmed_cases = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases')

    class Meta:
        db_table = "diabetes"
        managed = False
        verbose_name = "Diabetes Data"
        verbose_name_plural = "Diabetes Data"
        ordering = ['-periodname']

    def __str__(self):
        return f"Diabetes Data for {self.periodname}"

class MeningitisData(models.Model):
    periodname = models.CharField(max_length=100, primary_key=True)
    meningitis_cases = models.IntegerField(db_column='Meningitis')
    meningitis_cases_female = models.IntegerField(db_column="Meningitis - Female")
    meningitis_cases_male = models.IntegerField(db_column="Meningitis - Male")
    meningitis_case_fatality_rate = models.IntegerField(db_column="Meningitis case fatality rate")
    meningococcal_meningitis_cases_weekly = models.IntegerField(db_column="Meningococcal Meningitis cases (weekly)")
    meningococcal_meningitis_deaths_weekly = models.IntegerField(db_column="Meningococcal Meningitis deaths (weekly)")
    meningococcal_meningitis_lab_confirmed_cases = models.IntegerField(db_column="Meningococcal Meningitis lab confirmed cases")
    meningococcal_meningitis_lab_confirmed_cases_weekly = models.IntegerField(db_column="Meningococcal Meningitis lab confirmed cases (weekly)")
    meningococcal_meningitis_cases_cds = models.IntegerField(db_column="Meningococcal meningitis cases (CDS)")
    meningococcal_meningitis_deaths = models.IntegerField(db_column="Meningococcal meningitis deaths")

    class Meta:
        db_table = 'meningitis'
        verbose_name = 'Meningitis Data'
        verbose_name_plural = 'Meningitis Data'
        managed = False
        ordering = ['-periodname']

    def __str__(self):
        return f"Meningitis Data for {self.periodname}"

class CholeraData(models.Model):
    periodname = models.CharField(max_length=100, primary_key=True)
    cholera_female = models.IntegerField(db_column="Cholera - Female", null=True)
    cholera_male = models.IntegerField(db_column="Cholera - Male", null=True)
    cholera_deaths_cds = models.IntegerField(db_column="Cholera Deaths (CDS)", null=True)
    cholera_cases_cds = models.IntegerField(db_column="Cholera cases (CDS)", null=True)
    cholera_cases_weekly = models.IntegerField(db_column="Cholera cases (weekly)", null=True)
    cholera_deaths_weekly = models.IntegerField(db_column="Cholera deaths (weekly)", null=True)
    cholera_lab_confirmed = models.IntegerField(db_column="Cholera lab confirmed cases", null=True)
    cholera_lab_confirmed_weekly = models.IntegerField(db_column="Cholera lab confirmed cases (weekly)", null=True)
    cholera_waho_cases = models.IntegerField(db_column="WAHO/OOAS Cholera cases", null=True)

    class Meta:
        db_table = 'cholera'
        verbose_name = 'Cholera Data'
        verbose_name_plural = 'Cholera Data'
        managed = False
        ordering = ['-periodname']

    def __str__(self):
        return f"Cholera Data - {self.periodname}"

class NationalHotspots(models.Model):
    organisationunitname = models.CharField(db_column='organisationunitname', max_length=100, primary_key=True)
    cholera_lab_confirmed_cases_2020 = models.IntegerField(db_column='Cholera lab confirmed cases 2020', null=True)
    cholera_lab_confirmed_cases_2021 = models.IntegerField(db_column='Cholera lab confirmed cases 2021', null=True)
    cholera_lab_confirmed_cases_2022 = models.IntegerField(db_column='Cholera lab confirmed cases 2022', null=True)
    cholera_lab_confirmed_cases_2023 = models.IntegerField(db_column='Cholera lab confirmed cases 2023', null=True)
    cholera_lab_confirmed_cases_2024 = models.IntegerField(db_column='Cholera lab confirmed cases 2024', null=True)
    cholera_lab_confirmed_cases_2025 = models.IntegerField(db_column='Cholera lab confirmed cases 2025', null=True)
    diabetes_mellitus_lab_confirmed_cases_2020 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2020', null=True)
    diabetes_mellitus_lab_confirmed_cases_2021 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2021', null=True)
    diabetes_mellitus_lab_confirmed_cases_2022 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2022', null=True)
    diabetes_mellitus_lab_confirmed_cases_2023 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2023', null=True)
    diabetes_mellitus_lab_confirmed_cases_2024 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2024', null=True)
    diabetes_mellitus_lab_confirmed_cases_2025 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2025', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2020 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2020', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2021 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2021', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2022 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2022', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2023 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2023', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2024 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2024', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2025 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2025', null=True)

    class Meta:
        managed = False
        db_table = 'national_hotspots'
        verbose_name = 'National Hotspots'
        verbose_name_plural = 'National Hotspots'

    def __str__(self):
        return f"National Hotspots - {self.organisationunitname}"

class Disease(models.Model):
    disease_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"Disease {self.disease_name}"

class DiseaseYear(models.Model):
    periodname = models.CharField(max_length=100)
    disease_id = models.ForeignKey(Disease, on_delete=models.CASCADE)
    hot_spots = models.CharField(max_length=3)
    summary_data = models.CharField(max_length=3)
    case_count_summary = models.CharField(max_length=3)

    class Meta:
        verbose_name = "Disease Year"
        verbose_name_plural = "Disease Years"
        ordering = ['-periodname']

    def __str__(self):
        return f"Disease Year {self.periodname}"

class DiseaseTrends(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='trends')
    year = models.IntegerField()
    month = models.IntegerField()  # 1=Jan, 12=Dec
    trend_value = models.FloatField()

    class Meta:
        unique_together = ('disease', 'year', 'month')
        verbose_name = 'Disease Trend'
        verbose_name_plural = 'Disease Trends'
        ordering = ['disease', 'year', 'month']

    def __str__(self):
        return f"{self.disease.disease_name} - {self.year}-{self.month:02d}: {self.trend_value}"

class CommonSymptom(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='common_symptoms')
    symptom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    rank = models.PositiveIntegerField(default=1)  

    class Meta:
        unique_together = ('disease', 'symptom')
        ordering = ['disease', 'rank']

    def __str__(self):
        return f"{self.disease.disease_name}: {self.symptom} (#{self.rank})"


class HospitalHealthData(models.Model):
    orgname = models.CharField(max_length=100) 
    address_locality = models.CharField(max_length=255)
    age = models.IntegerField()
    sex = models.CharField(max_length=10) 
    principal_diagnosis_new = models.CharField(max_length=255)
    additional_diagnosis_new = models.CharField(max_length=255, blank=True, null=True)
    pregnant_patient = models.BooleanField()
    nhia_patient = models.BooleanField()
    month = models.DateField() 
    
    # New fields added for merged data
    data_source = models.CharField(max_length=20, default='legacy', blank=True, null=True)
    medicine_prescribed = models.TextField(blank=True, null=True)
    cost_of_treatment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    schedule_date = models.DateField(blank=True, null=True)
    locality_encoded = models.IntegerField(blank=True, null=True)


    class Meta:
        indexes = [
            models.Index(fields=['orgname', 'month']),
        ]
        verbose_name = 'Hospital Health Data'
        verbose_name_plural = 'Hospital Health Data'

class PredictionLog(models.Model):
    orgname = models.CharField(max_length=100)
    address_locality = models.CharField(max_length=255)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    pregnant_patient = models.BooleanField()
    nhia_patient = models.BooleanField()
    disease_type = models.CharField(max_length=50)
    symptoms = models.TextField()  # Store as JSON string
    prediction = models.CharField(max_length=100)
    probability = models.FloatField()
    gemini_enabled = models.BooleanField(default=False)
    gemini_recommendation = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_symptoms(self, symptoms_list):
        self.symptoms = json.dumps(symptoms_list)

    def get_symptoms(self):
        return json.loads(self.symptoms)

    def __str__(self):
        return f"{self.orgname} | {self.disease_type} | {self.prediction} | {self.timestamp}"

class HospitalLocalities(models.Model):
    """
    Model to store hospital-locality combinations for filtering
    """
    id = models.AutoField(primary_key=True)
    locality = models.CharField(max_length=255, help_text="Patient's residential area")
    orgname = models.CharField(max_length=255, help_text="Healthcare facility name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hospital_localities'
        verbose_name = 'Hospital Locality'
        verbose_name_plural = 'Hospital Localities'
        unique_together = ['locality', 'orgname']
        ordering = ['locality', 'orgname']
        indexes = [
            models.Index(fields=['locality']),
            models.Index(fields=['orgname']),
            models.Index(fields=['locality', 'orgname']),
        ]
    
    def __str__(self):
        return f"{self.locality} - {self.orgname}"
    
    @classmethod
    def get_localities_for_hospital(cls, orgname):
        """Get all localities for a specific hospital"""
        return cls.objects.filter(orgname__icontains=orgname).values_list('locality', flat=True).distinct()
    
    @classmethod
    def get_hospitals_for_locality(cls, locality):
        """Get all hospitals for a specific locality"""
        return cls.objects.filter(locality__icontains=locality).values_list('orgname', flat=True).distinct()
    
    @classmethod
    def get_all_localities(cls):
        """Get all unique localities"""
        return cls.objects.values_list('locality', flat=True).distinct().order_by('locality')
    
    @classmethod
    def get_all_hospitals(cls):
        """Get all unique hospitals"""
        return cls.objects.values_list('orgname', flat=True).distinct().order_by('orgname')
    
    @classmethod
    def search_localities(cls, query):
        """Search localities by partial match"""
        return cls.objects.filter(locality__icontains=query).values_list('locality', flat=True).distinct()
    
    @classmethod
    def search_hospitals(cls, query):
        """Search hospitals by partial match"""
        return cls.objects.filter(orgname__icontains=query).values_list('orgname', flat=True).distinct()

class Hospital(models.Model):
    """
    Model to store hospitals in the system
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, help_text="Hospital name")
    slug = models.CharField(max_length=255, unique=True, help_text="URL-friendly identifier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hospitals'
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)

    def _generate_slug(self):
        """Generate a URL-friendly slug from the hospital name"""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', self.name.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return slug

    @classmethod
    def get_by_slug(cls, slug):
        """Get hospital by slug"""
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None

    @classmethod
    def search_by_name(cls, query):
        """Search hospitals by name"""
        return cls.objects.filter(name__icontains=query)

    @classmethod
    def get_all_hospitals(cls):
        """Get all hospitals ordered by name"""
        return cls.objects.all().order_by('name')