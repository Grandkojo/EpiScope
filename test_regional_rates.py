#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import RegionPopulation, NationalHotspots
from api.models import User
from django.contrib.auth import authenticate
from api.services.admin.regional_rates import (
    get_regional_disease_rates, 
    get_available_years_for_rates, 
    get_available_regions_for_rates, 
    get_available_diseases_for_rates,
    get_rate_statistics
)

def test_population_data():
    """Test that population data is loaded correctly"""
    print("=== Testing Population Data ===")
    
    # Check total records
    total = RegionPopulation.objects.count()
    print(f"Total population records: {total}")
    
    # Check unique regions and years
    regions = RegionPopulation.objects.values_list('region', flat=True).distinct()
    years = RegionPopulation.objects.values_list('periodname', flat=True).distinct()
    
    print(f"Unique regions: {len(regions)}")
    print(f"Unique years: {len(years)}")
    
    # Show sample data for 2022
    print("\nSample population data for 2022:")
    sample_2022 = RegionPopulation.objects.filter(periodname='2022')[:3]
    for record in sample_2022:
        print(f"  {record.region}: {record.population:,}")
    
    return True

def test_hotspots_data():
    """Test that hotspots data is available"""
    print("\n=== Testing Hotspots Data ===")
    
    # Check total records
    total = NationalHotspots.objects.count()
    print(f"Total hotspots records: {total}")
    
    # Show sample regions
    regions = NationalHotspots.objects.values_list('organisationunitname', flat=True)
    print(f"Available regions: {list(regions)}")
    
    # Show sample data for one region
    if total > 0:
        sample = NationalHotspots.objects.first()
        print(f"\nSample data for {sample.organisationunitname}:")
        print(f"  Diabetes 2022: {getattr(sample, 'diabetes_mellitus_lab_confirmed_cases_2022', 'N/A')}")
        print(f"  Cholera 2022: {getattr(sample, 'cholera_lab_confirmed_cases_2022', 'N/A')}")
        print(f"  Meningitis 2022: {getattr(sample, 'meningococcal_meningitis_lab_confirmed_cases_2022', 'N/A')}")
    
    return True

def test_rate_calculation():
    """Test rate calculation manually"""
    print("\n=== Testing Rate Calculation ===")
    
    # Get population for Ashanti 2022
    try:
        population = RegionPopulation.objects.get(region='Ashanti', periodname='2022')
        print(f"Ashanti 2022 population: {population.population:,}")
        
        # Get diabetes cases for Ashanti 2022
        hotspot = NationalHotspots.objects.get(organisationunitname='Ashanti')
        cases = getattr(hotspot, 'diabetes_mellitus_lab_confirmed_cases_2022', 0) or 0
        print(f"Ashanti 2022 diabetes cases: {cases}")
        
        # Calculate rate
        rate = (cases / population.population) * 1000 if population.population > 0 else 0
        print(f"Calculated rate: {rate:.2f} per 1000 population")
        
    except RegionPopulation.DoesNotExist:
        print("Error: No population data for Ashanti 2022")
    except NationalHotspots.DoesNotExist:
        print("Error: No hotspots data for Ashanti")
    except Exception as e:
        print(f"Error: {e}")

def test_service_functions():
    """Test the new service functions"""
    print("\n=== Testing Service Functions ===")
    
    # Test available data functions
    print("Available years:", get_available_years_for_rates())
    print("Available regions:", len(get_available_regions_for_rates()))
    print("Available diseases:", get_available_diseases_for_rates())
    
    # Test regional disease rates service
    print("\nTesting regional disease rates service...")
    result = get_regional_disease_rates('diabetes', '2022')
    
    if result['success']:
        print(f"Success! Got {len(result['data'])} regions")
        print(f"Summary: {result['summary']}")
        
        # Show sample results
        print("\nSample results:")
        for item in result['data'][:3]:
            print(f"  {item['region']}: {item['cases']} cases, {item['population']:,} population, {item['rate']} per 1000")
    else:
        print(f"Error: {result['error']}")
    
    # Test statistics service
    print("\nTesting statistics service...")
    stats_result = get_rate_statistics('diabetes', '2022')
    
    if stats_result['success']:
        print(f"Statistics: {stats_result['statistics']}")
    else:
        print(f"Error: {stats_result['error']}")

def test_api_endpoint():
    """Test the API endpoint"""
    print("\n=== Testing API Endpoint ===")
    
    base_url = "http://localhost:8000"
    
    # Test diabetes rates for 2022
    print("Testing diabetes rates for 2022...")
    try:
        response = requests.get(f"{base_url}/api/diseases/region-rates/?disease=diabetes&year=2022")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Got {len(data)} regions")
            
            # Show sample results
            print("\nSample results:")
            for item in data[:3]:
                print(f"  {item['region']}: {item['cases']} cases, {item['population']:,} population, {item['rate']} per 1000")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"Error: {e}")

def test_direct_calculation():
    """Test the calculation logic directly"""
    print("\n=== Testing Direct Calculation ===")
    
    disease = 'diabetes'
    year = '2022'
    
    # Get all regions with their population data for the specified year
    try:
        population_data = RegionPopulation.objects.filter(periodname=year)
        print(f"Found {population_data.count()} population records for {year}")
        
        # Get disease cases from NationalHotspots
        hotspots = NationalHotspots.objects.all()
        print(f"Found {hotspots.count()} hotspot records")
        
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
                print(f"  Skipping {region_name} - no population data")
                continue
            
            # Get cases based on disease type
            cases = 0
            if disease == 'diabetes':
                cases = getattr(hotspot, f'diabetes_mellitus_lab_confirmed_cases_{year}', 0) or 0
            elif disease == 'cholera':
                cases = getattr(hotspot, f'cholera_lab_confirmed_cases_{year}', 0) or 0
            elif disease == 'meningitis':
                cases = getattr(hotspot, f'meningococcal_meningitis_lab_confirmed_cases_{year}', 0) or 0
            
            # Calculate rate per 1000 population
            rate = round((cases / population) * 1000, 2) if population > 0 else 0
            
            data.append({
                'region': region_name,
                'cases': cases,
                'population': population,
                'rate': rate,
            })
        
        # Sort by region name for consistency
        data.sort(key=lambda x: x['region'])
        
        print(f"Calculated rates for {len(data)} regions:")
        for item in data[:5]:  # Show first 5
            print(f"  {item['region']}: {item['cases']} cases, {item['population']:,} population, {item['rate']} per 1000")
        
        if len(data) > 5:
            print(f"  ... and {len(data) - 5} more regions")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Regional Disease Rates API")
    print("=" * 40)
    
    # Run tests
    test_population_data()
    test_hotspots_data()
    test_rate_calculation()
    test_service_functions()
    test_direct_calculation()
    test_api_endpoint()
    
    print("\n" + "=" * 40)
    print("Testing completed!") 