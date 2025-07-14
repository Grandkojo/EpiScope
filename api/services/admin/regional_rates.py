from disease_monitor.models import RegionPopulation, NationalHotspots, Disease
from rest_framework.response import Response
from rest_framework import status


def get_regional_disease_rates(disease, year):
    """
    Calculate regional disease rates (cases per 1000 population) for a selected disease and year.
    
    Args:
        disease (str): Disease type (from Disease model)
        year (str): Year to calculate rates for
        
    Returns:
        dict: Response data with success/error status and data
    """
    try:
        # Validate inputs
        disease = disease.lower()
        year = str(year)
        
        # Get available diseases from Disease model
        available_diseases = [d.disease_name.lower() for d in Disease.objects.all()]
        
        if disease not in available_diseases:
            return {
                'success': False,
                'error': f'Unsupported disease type. Available diseases: {", ".join(available_diseases)}',
                'status_code': 400
            }
        
        # Get all regions with their population data for the specified year
        population_data = RegionPopulation.objects.filter(periodname=year)
        if not population_data.exists():
            return {
                'success': False,
                'error': f'No population data available for year {year}',
                'status_code': 404
            }
        
        # Get disease cases from NationalHotspots (which has regional data)
        hotspots = NationalHotspots.objects.all()
        data = []
        
        for hotspot in hotspots:
            region_name = hotspot.organisationunitname
            
            # Skip Ghana (it's a summary row)
            if region_name == 'Ghana':
                continue
            
            # Get population for this region and year
            try:
                population_record = population_data.get(region=region_name)
                population = population_record.population
            except RegionPopulation.DoesNotExist:
                # Skip regions without population data
                continue
            
            # Get cases based on disease type
            cases = 0
            if disease == 'diabetes':
                cases = getattr(hotspot, f'diabetes_mellitus_lab_confirmed_cases_{year}', 0) or 0
            elif disease == 'cholera':
                cases = getattr(hotspot, f'cholera_lab_confirmed_cases_{year}', 0) or 0
            elif disease == 'meningitis':
                cases = getattr(hotspot, f'meningococcal_meningitis_lab_confirmed_cases_{year}', 0) or 0
            elif disease == 'malaria':
                # Malaria data not available yet - will return 0 cases until data is added
                cases = getattr(hotspot, f'malaria_lab_confirmed_cases_{year}', 0) or 0
            else:
                # For any other disease, try to get cases using the disease name pattern
                field_name = f'{disease}_lab_confirmed_cases_{year}'
                cases = getattr(hotspot, field_name, 0) or 0
            
            # Calculate rate per 1000 population
            rate = round((cases / population) * 1000, 2) if population > 0 else 0
            
            data.append({
                'region': region_name,
                'cases': cases,
                'population': population,
                'rate': rate
            })
        
        # Sort by region name for consistency
        data.sort(key=lambda x: x['region'])
        
        return {
            'success': True,
            'data': data,
            'summary': {
                'total_regions': len(data),
                'disease': disease,
                'year': year,
                'total_cases': sum(item['cases'] for item in data),
                'total_population': sum(item['population'] for item in data),
                'average_rate': round(sum(item['rate'] for item in data) / len(data), 2) if data else 0
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error processing disease data: {str(e)}',
            'status_code': 500
        }


def get_available_years_for_rates():
    """
    Get available years for regional disease rates calculation.
    
    Returns:
        list: Available years
    """
    try:
        years = RegionPopulation.objects.values_list('periodname', flat=True).distinct().order_by('periodname')
        return list(years)
    except Exception as e:
        return []


def get_available_regions_for_rates():
    """
    Get available regions for regional disease rates calculation.
    
    Returns:
        list: Available regions
    """
    try:
        regions = RegionPopulation.objects.values_list('region', flat=True).distinct().order_by('region')
        return list(regions)
    except Exception as e:
        return []


def get_available_diseases_for_rates():
    """
    Get available diseases for regional disease rates calculation.
    
    Returns:
        list: Available diseases
    """
    try:
        diseases = Disease.objects.values_list('disease_name', flat=True).order_by('disease_name')
        return list(diseases)
    except Exception as e:
        return []


def get_rate_statistics(disease, year):
    """
    Get statistical summary for regional disease rates.
    
    Args:
        disease (str): Disease type
        year (str): Year
        
    Returns:
        dict: Statistical summary
    """
    result = get_regional_disease_rates(disease, year)
    
    if not result['success']:
        return result
    
    data = result['data']
    
    if not data:
        return {
            'success': False,
            'error': 'No data available for the specified parameters',
            'status_code': 404
        }
    
    rates = [item['rate'] for item in data]
    cases = [item['cases'] for item in data]
    
    # Calculate statistics
    stats = {
        'total_regions': len(data),
        'total_cases': sum(cases),
        'total_population': sum(item['population'] for item in data),
        'average_rate': round(sum(rates) / len(rates), 2),
        'min_rate': min(rates),
        'max_rate': max(rates),
        'min_cases': min(cases),
        'max_cases': max(cases),
        'regions_with_cases': len([c for c in cases if c > 0]),
        'regions_without_cases': len([c for c in cases if c == 0])
    }
    
    return {
        'success': True,
        'statistics': stats,
        'disease': disease,
        'year': year
    } 