from django.db import models
from disease_monitor.models import NationalHotspots, DiseaseYear, Disease

def get_national_hotspots(year=None, region=None, disease=None):
    """
    Get filtered national hotspots data
    
    Args:
        year (str): Filter by specific year (2020, 2021, 2022, 2023, 2024, 2025)
        region (str): Filter by region name (partial match, case-insensitive)
        disease (str): Filter by disease type (cholera, diabetes, meningitis, all)
    
    Returns:
        QuerySet: Filtered NationalHotspots queryset
    """
    # Start with all hotspots
    hotspots = NationalHotspots.objects.all()
    
    # Exclude Ghana region (it's a summary/total row)
    hotspots = hotspots.exclude(organisationunitname='Ghana')
    
    # Filter by region if provided
    if region:
        if region.lower() == 'all':
            # Don't filter by region, return all regions
            pass
        else:
            # Filter by specific region name
            hotspots = hotspots.filter(organisationunitname__icontains=region)
    
    # Filter by year if provided
    if year and year.lower() != 'all':
        # Validate that the year exists in available years
        available_years = get_available_years()
        if year not in available_years:
            # Return empty queryset if year doesn't exist
            return NationalHotspots.objects.none()
        
        # Create a filter for the specific year across all disease types
        year_filters = models.Q()
        year_filters |= models.Q(**{f'cholera_lab_confirmed_cases_{year}__isnull': False})
        year_filters |= models.Q(**{f'diabetes_mellitus_lab_confirmed_cases_{year}__isnull': False})
        year_filters |= models.Q(**{f'meningococcal_meningitis_lab_confirmed_cases_{year}__isnull': False})
        hotspots = hotspots.filter(year_filters)
    
    # Filter by disease type if provided
    if disease:
        disease = disease.lower()
        
        if disease == 'all':
            # For 'all', keep the OR logic to get any disease data
            disease_filters = models.Q()
            for year_suffix in get_available_years():
                disease_filters |= models.Q(**{f'cholera_lab_confirmed_cases_{year_suffix}__isnull': False})
                disease_filters |= models.Q(**{f'diabetes_mellitus_lab_confirmed_cases_{year_suffix}__isnull': False})
                disease_filters |= models.Q(**{f'meningococcal_meningitis_lab_confirmed_cases_{year_suffix}__isnull': False})
            hotspots = hotspots.filter(disease_filters)
        elif disease == 'cholera':
            # For specific disease, only return records with that disease data
            cholera_filters = models.Q()
            for year_suffix in get_available_years():
                cholera_filters |= models.Q(**{f'cholera_lab_confirmed_cases_{year_suffix}__isnull': False})
            hotspots = hotspots.filter(cholera_filters)
        elif disease == 'diabetes':
            # For specific disease, only return records with that disease data
            diabetes_filters = models.Q()
            for year_suffix in get_available_years():
                diabetes_filters |= models.Q(**{f'diabetes_mellitus_lab_confirmed_cases_{year_suffix}__isnull': False})
            hotspots = hotspots.filter(diabetes_filters)
        elif disease == 'meningitis':
            # For specific disease, only return records with that disease data
            meningitis_filters = models.Q()
            for year_suffix in get_available_years():
                meningitis_filters |= models.Q(**{f'meningococcal_meningitis_lab_confirmed_cases_{year_suffix}__isnull': False})
            hotspots = hotspots.filter(meningitis_filters)
    
    return hotspots

def get_national_hotspots_summary(hotspots, year=None, disease=None):
    """
    Get aggregated summary data for national hotspots
    
    Args:
        hotspots (QuerySet): Filtered NationalHotspots queryset
        year (str): Specific year to filter by
        disease (str): Specific disease to filter by
    
    Returns:
        list: List of summary data dictionaries
    """
    summary_data = []
    
    for hotspot in hotspots:
        region_data = {
            'region': hotspot.organisationunitname,
            'total_cases': 0,
            'disease_breakdown': {}
        }
        
        # Calculate totals for each disease type
        cholera_total = 0
        diabetes_total = 0
        meningitis_total = 0
        
        for year_suffix in get_available_years():
            # Only include specific year if requested
            if year and year_suffix != year:
                continue
            
            # Only include specific disease if requested
            if not disease or disease in ['cholera', 'all']:
                cholera_cases = getattr(hotspot, f'cholera_lab_confirmed_cases_{year_suffix}', 0) or 0
                cholera_total += cholera_cases
            
            if not disease or disease in ['diabetes', 'all']:
                diabetes_cases = getattr(hotspot, f'diabetes_mellitus_lab_confirmed_cases_{year_suffix}', 0) or 0
                diabetes_total += diabetes_cases
            
            if not disease or disease in ['meningitis', 'all']:
                meningitis_cases = getattr(hotspot, f'meningococcal_meningitis_lab_confirmed_cases_{year_suffix}', 0) or 0
                meningitis_total += meningitis_cases
        
        region_data['total_cases'] = cholera_total + diabetes_total + meningitis_total
        region_data['disease_breakdown'] = {
            'cholera': cholera_total,
            'diabetes': diabetes_total,
            'meningitis': meningitis_total
        }
        
        summary_data.append(region_data)
    
    return summary_data

def get_available_years():
    """
    Get list of available years in the national hotspots data using DiseaseYear model
    Returns:
        list: List of available years
    """
    return list(DiseaseYear.objects.values_list('periodname', flat=True).distinct().order_by('-periodname'))

def get_available_regions():
    """
    Get list of available regions in the national hotspots data
    
    Returns:
        list: List of available regions
    """
    return list(NationalHotspots.objects.values_list('organisationunitname', flat=True).distinct())

def get_available_diseases():
    """
    Get list of available disease types using Disease model
    Returns:
        list: List of available disease types
    """
    return list(Disease.objects.values_list('disease_name', flat=True).distinct().order_by('disease_name')) 