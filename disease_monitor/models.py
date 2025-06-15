from django.db import models

# Create your models here.

class DiabetesData(models.Model):
    periodname = models.CharField(max_length=100)
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
    periodname = models.CharField(max_length=100)
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
    periodname = models.CharField(max_length=100)
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