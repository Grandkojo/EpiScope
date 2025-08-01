import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from django.conf import settings
from typing import Dict, List, Any, Optional
import json
from disease_monitor.models import HospitalHealthData, Disease
from django.db.models import Q, Count, Avg
from .disease_config import get_disease_config, get_disease_filters, is_disease_supported

class AnalyticsDataService:
    """Service for providing analytics data for the health dashboard"""
    
    def __init__(self):
        # Disease configuration mapping
        self.disease_config = self._load_disease_config()
    
    def _load_disease_config(self) -> Dict[str, Dict[str, Any]]:
        """Load disease configuration from database and create mapping"""
        config = {}
        
        # Get all diseases from database
        diseases = Disease.objects.all()
        
        for disease in diseases:
            disease_name = disease.disease_name.lower()
            
            # Get configuration from disease_config module
            disease_config = get_disease_config(disease_name)
            
            config[disease_name] = {
                'name': disease.disease_name,
                'description': disease.description,
                'filters': disease_config.get('filters', get_disease_filters(disease_name)),
                'icd_codes': disease_config.get('icd_codes', []),
                'symptoms': disease_config.get('symptoms', [])
            }
        
        return config
    
    def _build_disease_query(self, disease_name: str) -> Q:
        """Build Django Q object for disease filtering"""
        if disease_name not in self.disease_config:
            return Q()
        
        filters = self.disease_config[disease_name]['filters']
        query = Q()
        
        # Add text filters
        for text_filter in filters['text_filters']:
            query |= Q(principal_diagnosis_new__icontains=text_filter)
        
        # Add regex patterns
        for pattern in filters['regex_patterns']:
            query |= Q(principal_diagnosis_new__regex=pattern)
        
        # Add code patterns
        for code in filters['code_patterns']:
            query |= Q(principal_diagnosis_new__icontains=code)
        
        return query
    
    def _get_disease_queryset(self, disease_name: str, year: int = None, orgname: str = None) -> Optional[Any]:
        """Get queryset for a specific disease with optional year and orgname filters"""
        if disease_name not in self.disease_config:
            return None
        
        # Build base disease query
        disease_q = self._build_disease_query(disease_name)
        if not disease_q:
            return None
        
        # Start with disease filter
        queryset = HospitalHealthData.objects.filter(disease_q)
        
        # Add year filter if provided
        if year:
            queryset = queryset.filter(month__year=year)
        
        # Add orgname filter if provided
        if orgname:
            queryset = queryset.filter(orgname__icontains=orgname)
        
        return queryset
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get overview statistics for the dashboard"""
        try:
            result = {
                'total_cases': {},
                'localities': {},
                'age_distribution': {},
                'sex_distribution': {}
            }
            
            for disease_name, config in self.disease_config.items():
                queryset = self._get_disease_queryset(disease_name)
                if queryset is None:
                    continue
                
                # Calculate basic statistics
                result['total_cases'][disease_name] = queryset.count()
                result['localities'][disease_name] = queryset.values('address_locality').distinct().count()
                result['age_distribution'][disease_name] = self._get_age_distribution_from_queryset(queryset)
                result['sex_distribution'][disease_name] = self._get_sex_distribution_from_queryset(queryset)
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_principal_diagnoses(self, disease: str = None, year: int = None, orgname: str = None) -> Dict[str, Any]:
        """Get top principal diagnoses with counts"""
        try:
            result = {}
            
            if disease:
                # Single disease
                if disease not in self.disease_config:
                    return {'success': False, 'error': f'Unknown disease: {disease}'}
                
                queryset = self._get_disease_queryset(disease, year, orgname)
                if queryset is not None:
                    diagnoses = queryset.values('principal_diagnosis_new').annotate(
                        count=Count('principal_diagnosis_new')
                    ).order_by('-count')[:10]
                    
                    result[disease] = [
                        {'code': item['principal_diagnosis_new'], 'count': item['count'], 'description': self._extract_description(item['principal_diagnosis_new'])}
                        for item in diagnoses
                    ]
            else:
                # All diseases
                for disease_name in self.disease_config:
                    queryset = self._get_disease_queryset(disease_name, year, orgname)
                    if queryset is not None:
                        diagnoses = queryset.values('principal_diagnosis_new').annotate(
                            count=Count('principal_diagnosis_new')
                        ).order_by('-count')[:10]
                        
                        result[disease_name] = [
                            {'code': item['principal_diagnosis_new'], 'count': item['count'], 'description': self._extract_description(item['principal_diagnosis_new'])}
                            for item in diagnoses
                        ]
                
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_additional_diagnoses(self, disease: str = None, year: int = None, orgname: str = None) -> Dict[str, Any]:
        """Get top additional diagnoses with counts"""
        try:
            result = {}
            
            if disease:
                # Single disease
                if disease not in self.disease_config:
                    return {'success': False, 'error': f'Unknown disease: {disease}'}
                
                queryset = self._get_disease_queryset(disease, year, orgname)
                if queryset is not None:
                    # Filter out null/empty additional diagnoses
                    diagnoses = queryset.exclude(
                        additional_diagnosis_new__isnull=True
                    ).exclude(
                        additional_diagnosis_new__exact=''
                    ).values('additional_diagnosis_new').annotate(
                        count=Count('additional_diagnosis_new')
                    ).order_by('-count')[:10]
                    
                    result[disease] = [
                        {'code': item['additional_diagnosis_new'], 'count': item['count'], 'description': self._extract_description(item['additional_diagnosis_new'])}
                        for item in diagnoses
                    ]
            else:
                # All diseases
                for disease_name in self.disease_config:
                    queryset = self._get_disease_queryset(disease_name, year, orgname)
                    if queryset is not None:
                        # Filter out null/empty additional diagnoses
                        diagnoses = queryset.exclude(
                            additional_diagnosis_new__isnull=True
                        ).exclude(
                            additional_diagnosis_new__exact=''
                        ).values('additional_diagnosis_new').annotate(
                            count=Count('additional_diagnosis_new')
                        ).order_by('-count')[:10]
                        
                        result[disease_name] = [
                            {'code': item['additional_diagnosis_new'], 'count': item['count'], 'description': self._extract_description(item['additional_diagnosis_new'])}
                            for item in diagnoses
                        ]
                
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_nhia_status(self) -> Dict[str, Any]:
        """Get NHIA status distribution from HospitalHealthData model"""
        try:
            result = {}
            
            for disease_name in self.disease_config:
                disease_q = self._build_disease_query(disease_name)
                
                if disease_q:
                    yes_count = HospitalHealthData.objects.filter(disease_q, nhia_patient=True).count()
                    no_count = HospitalHealthData.objects.filter(disease_q, nhia_patient=False).count()
                    
                    result[disease_name] = {
                        'Yes': yes_count,
                        'No': no_count
                    }
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_nhia_status_filtered(self, disease_name: str, year: int = None, locality: str = None, orgname: str = None) -> Dict[str, Any]:
        """Get NHIA status for a specific disease, year, locality, and orgname"""
        try:
            if disease_name.lower() not in self.disease_config:
                return {'success': False, 'error': 'Unsupported disease_name'}
            
            disease_q = self._build_disease_query(disease_name.lower())
            
            # Add year filter if provided
            if year:
                disease_q = disease_q & Q(month__year=year)
                year_val = year
            else:
                year_val = 'all'
            
            # Add locality filter if provided
            if locality and locality.lower() != 'all':
                disease_q = disease_q & Q(address_locality__icontains=locality)
            
            # Add orgname filter if provided
            if orgname:
                disease_q = disease_q & Q(orgname__icontains=orgname)
            
            yes_count = HospitalHealthData.objects.filter(disease_q, nhia_patient=True).count()
            no_count = HospitalHealthData.objects.filter(disease_q, nhia_patient=False).count()
            
            return {
                'success': True,
                'data': {
                    disease_name.lower(): {
                        'year': year_val,
                        'locality': locality if locality else 'all',
                        'orgname': orgname if orgname else 'all',
                        'yes': yes_count,
                        'no': no_count
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_pregnancy_status(self) -> Dict[str, Any]:
        """Get pregnancy status distribution"""
        try:
            result = {}
            
            for disease_name in self.disease_config:
                queryset = self._get_disease_queryset(disease_name)
                if queryset is not None:
                    pregnant_count = queryset.filter(pregnant_patient=True).count()
                    not_pregnant_count = queryset.filter(pregnant_patient=False).count()
                    
                    result[disease_name] = {
                        'Yes': pregnant_count,
                        'No': not_pregnant_count
                    }
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_pregnancy_status_filtered(self, disease_name: str, year: int = None, locality: str = None, orgname: str = None) -> Dict[str, Any]:
        """Get pregnancy status for a specific disease, year, locality, and orgname"""
        try:
            if disease_name.lower() not in self.disease_config:
                return {'success': False, 'error': 'Unsupported disease_name'}
            
            disease_q = self._build_disease_query(disease_name.lower())
            
            # Add year filter if provided
            if year:
                disease_q = disease_q & Q(month__year=year)
                year_val = year
            else:
                year_val = 'all'
            
            # Add locality filter if provided
            if locality and locality.lower() != 'all':
                disease_q = disease_q & Q(address_locality__icontains=locality)
            
            # Add orgname filter if provided
            if orgname:
                disease_q = disease_q & Q(orgname__icontains=orgname)
            
            yes_count = HospitalHealthData.objects.filter(disease_q, pregnant_patient=True).count()
            no_count = HospitalHealthData.objects.filter(disease_q, pregnant_patient=False).count()
            
            return {
                'success': True,
                'data': {
                    disease_name.lower(): {
                        'year': year_val,
                        'locality': locality if locality else 'all',
                        'orgname': orgname if orgname else 'all',
                        'yes': yes_count,
                        'no': no_count
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_hotspots_by_locality(self, disease: str = None, year: int = None, orgname: str = None) -> Dict[str, Any]:
        """Get disease hotspots by locality"""
        try:
            result = {}
            
            if disease:
                # Single disease
                if disease not in self.disease_config:
                    return {'success': False, 'error': f'Unknown disease: {disease}'}
                
                queryset = self._get_disease_queryset(disease, year, orgname)
                if queryset is not None:
                    hotspots = queryset.values('address_locality').annotate(
                        cases=Count('address_locality')
                    ).order_by('-cases')[:10]
                    
                    result[disease] = [
                        {'locality': item['address_locality'], 'cases': item['cases']}
                        for item in hotspots
                    ]
            else:
                # All diseases
                for disease_name in self.disease_config:
                    queryset = self._get_disease_queryset(disease_name, year, orgname)
                    if queryset is not None:
                        hotspots = queryset.values('address_locality').annotate(
                            cases=Count('address_locality')
                        ).order_by('-cases')[:10]
                        
                        result[disease_name] = [
                            {'locality': item['address_locality'], 'cases': item['cases']}
                            for item in hotspots
                        ]
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_disease_comparison(self, disease1: str, disease2: str, year: int = None, orgname: str = None) -> Dict[str, Any]:
        """Compare two diseases"""
        try:
            if disease1 not in self.disease_config or disease2 not in self.disease_config:
                return {'success': False, 'error': 'One or both diseases not found'}
            
            queryset1 = self._get_disease_queryset(disease1, year, orgname)
            queryset2 = self._get_disease_queryset(disease2, year, orgname)
            
            if queryset1 is None or queryset2 is None:
                return {'success': False, 'error': 'Data not available for one or both diseases'}
            
            comparison = {
                'disease1': {
                    'name': disease1,
                    'total_cases': queryset1.count(),
                    'localities': queryset1.values('address_locality').distinct().count(),
                    'avg_age': queryset1.aggregate(avg_age=Avg('age'))['avg_age'],
                    'sex_distribution': self._get_sex_distribution_from_queryset(queryset1)
                },
                'disease2': {
                    'name': disease2,
                    'total_cases': queryset2.count(),
                    'localities': queryset2.values('address_locality').distinct().count(),
                    'avg_age': queryset2.aggregate(avg_age=Avg('age'))['avg_age'],
                    'sex_distribution': self._get_sex_distribution_from_queryset(queryset2)
                }
            }
            
            return {'success': True, 'data': comparison}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_trends_by_locality(self, disease: str, year: int = None, orgname: str = None, locality: str = None, months: list = None) -> Dict[str, Any]:
        """Get trends by locality over time with optional year, orgname, locality, and months filters"""
        try:
            if disease not in self.disease_config:
                return {'success': False, 'error': f'Unknown disease: {disease}'}
            
            # Use the helper method for consistent filtering
            queryset = self._get_disease_queryset(disease, year, orgname)
            if queryset is None:
                return {'success': False, 'error': f'No data available for {disease}'}
            
            # Apply month filter if specified (default to 03, 06, 09, 10 if not provided)
            if months is None:
                months = [3, 6, 9, 10]  # Default months
            
            if months:
                queryset = queryset.filter(month__month__in=months)
            
            # Get localities based on filter
            if locality and locality.lower() != 'all':
                # Single locality specified
                locality_queryset = queryset.filter(address_locality__icontains=locality)
                if locality_queryset.count() == 0:
                    return {'success': False, 'error': f'No data found for locality: {locality}'}
                
                top_localities = locality_queryset.values('address_locality').annotate(
                    count=Count('address_locality')
                ).order_by('-count')
                top_locality_names = [item['address_locality'] for item in top_localities]
            else:
                # Get top 3 localities (efficient default) - either no locality specified or locality='all'
                top_localities = queryset.values('address_locality').annotate(
                    count=Count('address_locality')
                ).order_by('-count')[:3]
                top_locality_names = [item['address_locality'] for item in top_localities]
            
            # Get monthly trends for localities
            trends_data = {}
            for locality_name in top_locality_names:
                locality_data = queryset.filter(address_locality=locality_name).values(
                    'month'
                ).annotate(
                    cases=Count('id')
                ).order_by('month')
                
                trends_data[locality_name] = {
                    'labels': [item['month'].strftime('%Y-%m') for item in locality_data],
                    'data': [item['cases'] for item in locality_data]
                }
            
            # Convert to chart format
            result = {
                'labels': list(set([label for data in trends_data.values() for label in data['labels']])),
                'datasets': []
            }
            
            # Sort labels chronologically
            result['labels'].sort()
            
            for locality_name in top_locality_names:
                if locality_name in trends_data:
                    # Create data array matching the labels
                    data = []
                    for label in result['labels']:
                        if label in trends_data[locality_name]['labels']:
                            idx = trends_data[locality_name]['labels'].index(label)
                            data.append(trends_data[locality_name]['data'][idx])
                        else:
                            data.append(0)
                    
                    result['datasets'].append({
                        'label': locality_name,
                        'data': data
                    })
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_all_localities(self) -> Dict[str, Any]:
        try:
            localities = list(HospitalHealthData.objects.values_list('address_locality', flat=True).distinct())
            return {'success': True, 'localities': localities}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_available_diseases(self) -> Dict[str, Any]:
        """Get list of available diseases"""
        try:
            diseases = list(self.disease_config.keys())
            return {'success': True, 'diseases': diseases}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_available_orgnames(self) -> Dict[str, Any]:
        """Get list of available orgnames (hospitals)"""
        try:
            orgnames = list(HospitalHealthData.objects.values_list('orgname', flat=True).distinct())
            return {'success': True, 'orgnames': orgnames}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_age_distribution(self, disease: str = None, year: int = None, orgname: str = None) -> Dict[str, Any]:
        """Get age distribution with optional disease, year, and orgname filters"""
        try:
            result = {}
            
            if disease:
                # Single disease
                if disease not in self.disease_config:
                    return {'success': False, 'error': f'Unknown disease: {disease}'}
                
                queryset = self._get_disease_queryset(disease, year, orgname)
                if queryset is not None:
                    result[disease] = self._get_age_distribution_from_queryset(queryset)
            else:
                # All diseases
                for disease_name in self.disease_config:
                    queryset = self._get_disease_queryset(disease_name, year, orgname)
                    if queryset is not None:
                        result[disease_name] = self._get_age_distribution_from_queryset(queryset)
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_sex_distribution(self, disease: str = None, year: int = None, orgname: str = None) -> Dict[str, Any]:
        """Get sex distribution with optional disease, year, and orgname filters"""
        try:
            result = {}
            
            if disease:
                # Single disease
                if disease not in self.disease_config:
                    return {'success': False, 'error': f'Unknown disease: {disease}'}
                
                queryset = self._get_disease_queryset(disease, year, orgname)
                if queryset is not None:
                    result[disease] = self._get_sex_distribution_from_queryset(queryset)
            else:
                # All diseases
                for disease_name in self.disease_config:
                    queryset = self._get_disease_queryset(disease_name, year, orgname)
                    if queryset is not None:
                        result[disease_name] = self._get_sex_distribution_from_queryset(queryset)
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_disease_info(self, disease_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific disease"""
        try:
            if disease_name.lower() not in self.disease_config:
                return {'success': False, 'error': 'Disease not found'}
            
            config = self.disease_config[disease_name.lower()]
            
            return {
                'success': True,
                'data': {
                    'name': config['name'],
                    'description': config['description'],
                    'icd_codes': config['icd_codes'],
                    'symptoms': config['symptoms'],
                    'filters': config['filters']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_age_distribution_from_queryset(self, queryset) -> Dict[str, int]:
        """Get age distribution from queryset"""
        try:
            age_groups = {
                '0-18': queryset.filter(age__lte=18).count(),
                '19-35': queryset.filter(age__gt=18, age__lte=35).count(),
                '36-60': queryset.filter(age__gt=35, age__lte=60).count(),
                '60+': queryset.filter(age__gt=60).count()
            }
            return age_groups
        except:
            return {'0-18': 0, '19-35': 0, '36-60': 0, '60+': 0}
    
    def _get_sex_distribution_from_queryset(self, queryset) -> Dict[str, int]:
        """Get sex distribution from queryset"""
        try:
            sex_dist = queryset.values('sex').annotate(count=Count('sex'))
            result = {'Male': 0, 'Female': 0}
            
            for item in sex_dist:
                sex_value = item['sex']
                count = item['count']
                
                # Handle different possible formats
                if sex_value == 1 or sex_value == '1' or sex_value == 'Male' or sex_value == 'male':
                    result['Male'] = count
                elif sex_value == 0 or sex_value == '0' or sex_value == 'Female' or sex_value == 'female':
                    result['Female'] = count
                # Handle boolean values if they exist
                elif sex_value is True:
                    result['Male'] = count
                elif sex_value is False:
                    result['Female'] = count
            
            return result
        except Exception as e:
            return {'Male': 0, 'Female': 0}
    
    def _extract_description(self, code: str) -> str:
        """Extract description from diagnosis code"""
        try:
            if '[' in code and ']' in code:
                return code.split('[')[1].split(']')[0]
            return code
        except:
            return code 

# Create singleton instance
analytics_service = AnalyticsDataService() 