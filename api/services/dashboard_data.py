from django.core.cache import cache
from disease_monitor.models import DiabetesData, Disease, DiseaseYear, MeningitisData, CholeraData

def get_cache_key(year):
    return f'dashboard_counts_{year}'

def invalidate_dashboard_cache(year=None):
    if year:
        # Invalidate cache for specific year
        cache.delete(get_cache_key(year))
    else:
        # Invalidate all year caches
        for year in DiabetesData.objects.values_list('periodname', flat=True).distinct():
            cache.delete(get_cache_key(year))

def get_disease_data(disease_name, year):
    """Helper function to get data for a specific disease"""
    if disease_name == "Diabetes":
        return {
            "title": "Summary of Diabetes Cases",
            "year": year,
            "total_count": DiabetesData.objects.filter(periodname=year).values_list('diabetes_mellitus', flat=True).first(),
            "male_count": DiabetesData.objects.filter(periodname=year, diabetes_mellitus_male__isnull=False).values_list('diabetes_mellitus_male', flat=True).first(),
            "female_count": DiabetesData.objects.filter(periodname=year, diabetes_mellitus_female__isnull=False).values_list('diabetes_mellitus_female', flat=True).first(),
            "deaths_count": DiabetesData.objects.filter(periodname=year, diabetes_mellitus_deaths__isnull=False).values_list('diabetes_mellitus_deaths', flat=True).first(),
            "lab_confirmed_cases_count": DiabetesData.objects.filter(periodname=year, diabetes_mellitus_lab_confirmed_cases__isnull=False).values_list('diabetes_mellitus_lab_confirmed_cases', flat=True).first()
        }
    elif disease_name == "Meningitis":
        return {
            "title": "Summary of Meningitis Cases",
            "year": year,
            "total_count": MeningitisData.objects.filter(periodname=year).values_list('meningitis_cases', flat=True).first(),
            "male_count": MeningitisData.objects.filter(periodname=year, meningitis_cases_male__isnull=False).values_list('meningitis_cases_male', flat=True).first(),
            "female_count": MeningitisData.objects.filter(periodname=year, meningitis_cases_female__isnull=False).values_list('meningitis_cases_female', flat=True).first(),
            "fatality_rate": MeningitisData.objects.filter(periodname=year, meningitis_case_fatality_rate__isnull=False).values_list('meningitis_case_fatality_rate', flat=True).first(),
            "lab_confirmed_cases_count": MeningitisData.objects.filter(periodname=year, meningococcal_meningitis_lab_confirmed_cases__isnull=False).values_list('meningococcal_meningitis_lab_confirmed_cases', flat=True).first(),
            "lab_confirmed_cases_count_weekly": MeningitisData.objects.filter(periodname=year, meningococcal_meningitis_lab_confirmed_cases_weekly__isnull=False).values_list('meningococcal_meningitis_lab_confirmed_cases_weekly', flat=True).first(),
            "cases_cds_count": MeningitisData.objects.filter(periodname=year, meningococcal_meningitis_cases_cds__isnull=False).values_list('meningococcal_meningitis_cases_cds', flat=True).first(),
            "deaths_count": MeningitisData.objects.filter(periodname=year, meningococcal_meningitis_deaths__isnull=False).values_list('meningococcal_meningitis_deaths', flat=True).first()
        }
    elif disease_name == "Cholera":
        return {
            "title": "Summary of Cholera Cases",
            "year": year,
            "total_count": CholeraData.objects.filter(periodname=year).values_list('cholera_cases_weekly', flat=True).first(), #for the year
            "cholera_cases_weekly": CholeraData.objects.filter(periodname=year).values_list('cholera_cases_weekly', flat=True).first(),
            "cholera_male": CholeraData.objects.filter(periodname=year, cholera_male__isnull=False).values_list('cholera_male', flat=True).first(),
            "cholera_female": CholeraData.objects.filter(periodname=year, cholera_female__isnull=False).values_list('cholera_female', flat=True).first(),
            "cholera_deaths_weekly": CholeraData.objects.filter(periodname=year, cholera_deaths_weekly__isnull=False).values_list('cholera_deaths_weekly', flat=True).first(),
            "cholera_lab_confirmed": CholeraData.objects.filter(periodname=year, cholera_lab_confirmed__isnull=False).values_list('cholera_lab_confirmed', flat=True).first(),
            "cholera_lab_confirmed_weekly": CholeraData.objects.filter(periodname=year, cholera_lab_confirmed_weekly__isnull=False).values_list('cholera_lab_confirmed_weekly', flat=True).first(),
            "cholera_cases_cds": CholeraData.objects.filter(periodname=year, cholera_cases_cds__isnull=False).values_list('cholera_cases_cds', flat=True).first(),
            "cholera_deaths_cds": CholeraData.objects.filter(periodname=year, cholera_deaths_cds__isnull=False).values_list('cholera_deaths_cds', flat=True).first(),
            "cholera_waho_cases": CholeraData.objects.filter(periodname=year, cholera_waho_cases__isnull=False).values_list('cholera_waho_cases', flat=True).first()
        }
    return None

def get_dashboard_counts(year=2025, disease_name=None, region=None):
    cache_key = get_cache_key(year)
    dashboard_cache = cache.get(cache_key)
    c_disease_name = disease_name.title() if disease_name else None
    if dashboard_cache:
        return dashboard_cache
    
    #check if disease_name is valid
    disease_name_id = Disease.objects.filter(disease_name=c_disease_name).values_list('id', flat=True).distinct().first()
    if not disease_name_id and c_disease_name != "All":
        return {
            "error": f"Invalid disease name: {c_disease_name}"
        }
        
    #check if year is valid
    found_year = DiabetesData.objects.filter(periodname=year).values_list('periodname', flat=True).distinct().first()
    if not found_year:
        return {
            "error": f"No data for {year} available"
        }

    #get all disease names in an array
    disease_names = list(Disease.objects.values_list('disease_name', flat=True).distinct())
    disease_names.append("All")

    #if disease name is in array
    if c_disease_name in disease_names and found_year:
        if c_disease_name == "All":
            # Get data for all available diseases
            all_data = {}
            for disease in disease_names:
                if disease != "All":  # Skip the "All" option
                    disease_data = get_disease_data(disease, found_year)
                    if disease_data and disease_data["total_count"] is not None:
                        all_data[disease.lower()] = disease_data
            return all_data
        else:
            # Get data for specific disease
            disease_data = get_disease_data(c_disease_name, found_year)
            if disease_data and disease_data["total_count"] is not None:
                return {c_disease_name.lower(): disease_data}

    return {"error": "No data available for the specified parameters"}

def get_disease_years(disease_id):
    if not disease_id:
        return {
            "error": "No disease id provided"
        }
    found_year = DiseaseYear.objects.filter(disease_id=disease_id).values_list('periodname', flat=True).distinct().first()
    if not found_year:
        return {
            "error": f"No disease data for {disease_id} available"
        }
    return DiseaseYear.objects.filter(disease_id=disease_id).distinct('periodname').order_by('-periodname')

# def get_disease_years_only():
#     return DiseaseYear.objects.values_list('periodname', flat=True).distinct().order_by('-periodname')

def get_disease_all():
    return Disease.objects.all()