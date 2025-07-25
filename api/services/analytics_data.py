import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from django.conf import settings
from typing import Dict, List, Any, Optional
import json
from disease_monitor.models import HospitalHealthData
from django.db.models import Q

class AnalyticsDataService:
    """Service for providing analytics data for the health dashboard"""
    
    def __init__(self):
        self.diabetes_data_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'csv', 'health_data_eams_diabetes.csv')
        self.malaria_data_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'csv', 'health_data_eams_malaria.csv')
        self.diabetes_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_diabetes_time_stamped.csv')
        self.malaria_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_malaria_time_stamped.csv')
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get overview statistics for the dashboard"""
        try:
            diabetes_df = pd.read_csv(self.diabetes_data_path)
            malaria_df = pd.read_csv(self.malaria_data_path)
            
            # Calculate basic statistics
            diabetes_count = len(diabetes_df)
            malaria_count = len(malaria_df)
            
            # Get unique localities
            diabetes_localities = diabetes_df['Address (Locality)'].nunique()
            malaria_localities = malaria_df['Address (Locality)'].nunique()
            
            # Get age distribution
            diabetes_age_groups = self._get_age_distribution(diabetes_df)
            malaria_age_groups = self._get_age_distribution(malaria_df)
            
            # Get sex distribution
            diabetes_sex_dist = self._get_sex_distribution(diabetes_df)
            malaria_sex_dist = self._get_sex_distribution(malaria_df)
            
            return {
                'success': True,
                'data': {
                    'total_cases': {
                        'diabetes': diabetes_count,
                        'malaria': malaria_count
                    },
                    'localities': {
                        'diabetes': diabetes_localities,
                        'malaria': malaria_localities
                    },
                    'age_distribution': {
                        'diabetes': diabetes_age_groups,
                        'malaria': malaria_age_groups
                    },
                    'sex_distribution': {
                        'diabetes': diabetes_sex_dist,
                        'malaria': malaria_sex_dist
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_principal_diagnoses(self, disease: str = None) -> Dict[str, Any]:
        """Get top principal diagnoses with counts"""
        try:
            if disease == 'diabetes' or disease is None:
                diabetes_df = pd.read_csv(self.diabetes_data_path)
                diabetes_diagnoses = diabetes_df['Principal Diagnosis (New Case)'].value_counts().head(10)
                diabetes_data = [
                    {'code': code, 'count': count, 'description': self._extract_description(code)}
                    for code, count in diabetes_diagnoses.items()
                ]
            
            if disease == 'malaria' or disease is None:
                malaria_df = pd.read_csv(self.malaria_data_path)
                malaria_diagnoses = malaria_df['Principal Diagnosis (New Case)'].value_counts().head(10)
                malaria_data = [
                    {'code': code, 'count': count, 'description': self._extract_description(code)}
                    for code, count in malaria_diagnoses.items()
                ]
            
            result = {}
            if disease == 'diabetes' or disease is None:
                result['diabetes'] = diabetes_data
            if disease == 'malaria' or disease is None:
                result['malaria'] = malaria_data
                
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_additional_diagnoses(self, disease: str = None) -> Dict[str, Any]:
        """Get top additional diagnoses with counts"""
        try:
            if disease == 'diabetes' or disease is None:
                diabetes_df = pd.read_csv(self.diabetes_data_path)
                diabetes_diagnoses = diabetes_df['Additional Diagnosis (New Case)'].value_counts().head(10)
                diabetes_data = [
                    {'code': code, 'count': count, 'description': self._extract_description(code)}
                    for code, count in diabetes_diagnoses.items()
                ]
            
            if disease == 'malaria' or disease is None:
                malaria_df = pd.read_csv(self.malaria_data_path)
                malaria_diagnoses = malaria_df['Additional Diagnosis (New Case)'].value_counts().head(10)
                malaria_data = [
                    {'code': code, 'count': count, 'description': self._extract_description(code)}
                    for code, count in malaria_diagnoses.items()
                ]
            
            result = {}
            if disease == 'diabetes' or disease is None:
                result['diabetes'] = diabetes_data
            if disease == 'malaria' or disease is None:
                result['malaria'] = malaria_data
                
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_nhia_status(self) -> Dict[str, Any]:
        """Get NHIA status distribution from HospitalHealthData model"""
        try:
            # Diabetes filter
            diabetes_q = (
                Q(principal_diagnosis_new__icontains='diabetes') |
                Q(principal_diagnosis_new__regex=r'\\bE0[89]|E1[013]\\b') |
                Q(principal_diagnosis_new__icontains='MEDI02A') |
                Q(principal_diagnosis_new__icontains='MEDI03A')
            )
            # Malaria filter
            malaria_q = (
                Q(principal_diagnosis_new__icontains='malaria') |
                Q(principal_diagnosis_new__regex=r'\\bB5[0-4]\\b') |
                Q(principal_diagnosis_new__icontains='MEDI28A')
            )
            # Diabetes NHIA counts
            diabetes_yes = HospitalHealthData.objects.filter(diabetes_q, nhia_patient=True).count()
            diabetes_no = HospitalHealthData.objects.filter(diabetes_q, nhia_patient=False).count()
            # Malaria NHIA counts
            malaria_yes = HospitalHealthData.objects.filter(malaria_q, nhia_patient=True).count()
            malaria_no = HospitalHealthData.objects.filter(malaria_q, nhia_patient=False).count()
            return {
                'success': True,
                'data': {
                    'diabetes': {
                        'Yes': diabetes_yes,
                        'No': diabetes_no
                    },
                    'malaria': {
                        'Yes': malaria_yes,
                        'No': malaria_no
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_nhia_status_filtered(self, disease_name: str, year: int = None, locality: str = None) -> Dict[str, Any]:
        """Get NHIA status for a specific disease, year, and locality (or all years/localities if not provided)"""
        try:
            # Build disease filter
            if disease_name.lower() == 'diabetes':
                disease_q = (
                    Q(principal_diagnosis_new__icontains='diabetes') |
                    Q(principal_diagnosis_new__regex=r'\\bE0[89]|E1[013]\\b') |
                    Q(principal_diagnosis_new__icontains='MEDI02A') |
                    Q(principal_diagnosis_new__icontains='MEDI03A')
                )
            elif disease_name.lower() == 'malaria':
                disease_q = (
                    Q(principal_diagnosis_new__icontains='malaria') |
                    Q(principal_diagnosis_new__regex=r'\\bB5[0-4]\\b') |
                    Q(principal_diagnosis_new__icontains='MEDI28A')
                )
            else:
                return {'success': False, 'error': 'Unsupported disease_name'}
            # Add year filter if provided
            if year:
                disease_q = disease_q & Q(month__year=year)
                year_val = year
            else:
                year_val = 'all'
            # Add locality filter if provided
            if locality and locality.lower() != 'all':
                disease_q = disease_q & Q(address_locality=locality)
            yes_count = HospitalHealthData.objects.filter(disease_q, nhia_patient=True).count()
            no_count = HospitalHealthData.objects.filter(disease_q, nhia_patient=False).count()
            return {
                'success': True,
                'data': {
                    disease_name.lower(): {
                        'year': year_val,
                        'locality': locality if locality else 'all',
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
            diabetes_df = pd.read_csv(self.diabetes_data_path)
            malaria_df = pd.read_csv(self.malaria_data_path)
            
            diabetes_pregnant = diabetes_df['Pregnant Patient'].value_counts()
            malaria_pregnant = malaria_df['Pregnant Patient'].value_counts()
            
            return {
                'success': True,
                'data': {
                    'diabetes': {
                        'Yes': int(diabetes_pregnant.get('Yes', 0)),
                        'No': int(diabetes_pregnant.get('No', 0))
                    },
                    'malaria': {
                        'Yes': int(malaria_pregnant.get('Yes', 0)),
                        'No': int(malaria_pregnant.get('No', 0))
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_pregnancy_status_filtered(self, disease_name: str, year: int = None, locality: str = None) -> Dict[str, Any]:
        """Get pregnancy status for a specific disease, year, and locality (or all years/localities if not provided)"""
        try:
            # Build disease filter
            if disease_name.lower() == 'diabetes':
                disease_q = (
                    Q(principal_diagnosis_new__icontains='diabetes') |
                    Q(principal_diagnosis_new__regex=r'\\bE0[89]|E1[013]\\b') |
                    Q(principal_diagnosis_new__icontains='MEDI02A') |
                    Q(principal_diagnosis_new__icontains='MEDI03A')
                )
            elif disease_name.lower() == 'malaria':
                disease_q = (
                    Q(principal_diagnosis_new__icontains='malaria') |
                    Q(principal_diagnosis_new__regex=r'\\bB5[0-4]\\b') |
                    Q(principal_diagnosis_new__icontains='MEDI28A')
                )
            else:
                return {'success': False, 'error': 'Unsupported disease_name'}
            # Add year filter if provided
            if year:
                disease_q = disease_q & Q(month__year=year)
                year_val = year
            else:
                year_val = 'all'
            # Add locality filter if provided
            if locality and locality.lower() != 'all':
                disease_q = disease_q & Q(address_locality=locality)
            yes_count = HospitalHealthData.objects.filter(disease_q, pregnant_patient=True).count()
            no_count = HospitalHealthData.objects.filter(disease_q, pregnant_patient=False).count()
            return {
                'success': True,
                'data': {
                    disease_name.lower(): {
                        'year': year_val,
                        'locality': locality if locality else 'all',
                        'yes': yes_count,
                        'no': no_count
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_hotspots_by_locality(self, disease: str = None) -> Dict[str, Any]:
        """Get disease hotspots by locality"""
        try:
            result = {}
            
            if disease == 'diabetes' or disease is None:
                diabetes_df = pd.read_csv(self.diabetes_data_path)
                diabetes_hotspots = diabetes_df.groupby('Address (Locality)').size().sort_values(ascending=False).head(10)
                result['diabetes'] = [
                    {'locality': locality, 'cases': int(count)}
                    for locality, count in diabetes_hotspots.items()
                ]
            
            if disease == 'malaria' or disease is None:
                malaria_df = pd.read_csv(self.malaria_data_path)
                malaria_hotspots = malaria_df.groupby('Address (Locality)').size().sort_values(ascending=False).head(10)
                result['malaria'] = [
                    {'locality': locality, 'cases': int(count)}
                    for locality, count in malaria_hotspots.items()
                ]
            
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_disease_comparison(self, disease1: str, disease2: str) -> Dict[str, Any]:
        """Compare two diseases"""
        try:
            if disease1 == 'diabetes':
                df1 = pd.read_csv(self.diabetes_data_path)
            elif disease1 == 'malaria':
                df1 = pd.read_csv(self.malaria_data_path)
            else:
                return {'success': False, 'error': f'Unknown disease: {disease1}'}
            
            if disease2 == 'diabetes':
                df2 = pd.read_csv(self.diabetes_data_path)
            elif disease2 == 'malaria':
                df2 = pd.read_csv(self.malaria_data_path)
            else:
                return {'success': False, 'error': f'Unknown disease: {disease2}'}
            
            comparison = {
                'disease1': {
                    'name': disease1,
                    'total_cases': len(df1),
                    'localities': df1['Address (Locality)'].nunique(),
                    'avg_age': df1['Age'].str.extract(r'(\d+)').astype(float).mean(),
                    'sex_distribution': self._get_sex_distribution(df1)
                },
                'disease2': {
                    'name': disease2,
                    'total_cases': len(df2),
                    'localities': df2['Address (Locality)'].nunique(),
                    'avg_age': df2['Age'].str.extract(r'(\d+)').astype(float).mean(),
                    'sex_distribution': self._get_sex_distribution(df2)
                }
            }
            
            return {'success': True, 'data': comparison}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_trends_by_locality(self, disease: str, time_range: str = '3M') -> Dict[str, Any]:
        """Get trends by locality over time"""
        try:
            if disease == 'diabetes':
                df = pd.read_csv(self.diabetes_time_series_path)
            elif disease == 'malaria':
                df = pd.read_csv(self.malaria_time_series_path)
            else:
                return {'success': False, 'error': f'Unknown disease: {disease}'}
            
            # Convert Month column to datetime
            df['Month'] = pd.to_datetime(df['Month'])
            
            # Get top localities
            top_localities = df['Address (Locality)'].value_counts().head(3).index.tolist()
            
            # Filter data for top localities
            filtered_df = df[df['Address (Locality)'].isin(top_localities)]
            
            # Group by month and locality
            trends = filtered_df.groupby(['Month', 'Address (Locality)']).size().reset_index(name='cases')
            
            # Pivot to get localities as columns
            trends_pivot = trends.pivot(index='Month', columns='Address (Locality)', values='cases').fillna(0)
            
            # Convert to list format for frontend
            result = {
                'labels': trends_pivot.index.strftime('%Y-%m').tolist(),
                'datasets': []
            }
            
            for locality in top_localities:
                if locality in trends_pivot.columns:
                    result['datasets'].append({
                        'label': locality,
                        'data': trends_pivot[locality].tolist()
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
    
    def _get_age_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get age distribution from dataframe"""
        try:
            # Extract age numbers from Age column
            ages = df['Age'].str.extract(r'(\d+)').astype(float)
            
            # Create age groups
            age_groups = {
                '0-18': len(ages[ages <= 18]),
                '19-35': len(ages[(ages > 18) & (ages <= 35)]),
                '36-60': len(ages[(ages > 35) & (ages <= 60)]),
                '60+': len(ages[ages > 60])
            }
            
            return age_groups
        except:
            return {'0-18': 0, '19-35': 0, '36-60': 0, '60+': 0}
    
    def _get_sex_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get sex distribution from dataframe"""
        try:
            sex_dist = df['Sex'].value_counts()
            return {
                'Male': int(sex_dist.get('Male', 0)),
                'Female': int(sex_dist.get('Female', 0))
            }
        except:
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