import json
import os
import time
from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .services.dashboard_data import get_dashboard_counts, get_disease_years, get_disease_all
from .services.national_hotspots import get_national_hotspots, get_national_hotspots_summary, get_available_years, get_available_regions, get_available_diseases
from .services.analytics_data import analytics_service
from .services.time_series_forecasting import forecasting_service
from .services.ai_insights import ai_insights_service
from .serializers import DiseaseSerializer, DiseaseYearSerializer, UserRegisterSerializer, UserProfileSerializer, NationalHotspotsSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import (
    DashboardPermission, 
    DiseaseManagementPermission, 
    UserManagementPermission, 
    HotspotsPermission,
    IsAdminUser,
    IsSuperUser
)
from disease_monitor.models import DiabetesData, MeningitisData, CholeraData, NationalHotspots, DiseaseYear, RegionPopulation, Disease, DiseaseTrends
from .services.admin.regional_rates import get_regional_disease_rates, get_available_years_for_rates, get_available_regions_for_rates, get_available_diseases_for_rates, get_rate_statistics
from disease_monitor.serializers import DiseaseTrendsSerializer
from disease_monitor.models import PredictionLog
import pandas as pd
from src.models.disease_monitor import DiseaseMonitor
from datetime import datetime, timedelta
from django.db import models
from disease_monitor.models import HospitalLocalities
from disease_monitor.serializers import (
    HospitalLocalitiesSerializer, 
    HospitalLocalitiesListSerializer,
    HospitalLocalitiesFilterSerializer
)
from disease_monitor.models import Hospital
from disease_monitor.serializers import (
    HospitalSerializer,
    HospitalListSerializer,
    HospitalFilterSerializer
)

# Import rate limiting utilities
from .utils import (
    CustomUserRateThrottle, 
    SensitiveEndpointThrottle, 
    APIRateThrottle, 
    BurstRateThrottle,
    rate_limit_by_ip,
    rate_limit_by_user
)

def get_throttle_classes(*throttle_classes):
    """
    Conditionally return throttle classes based on RATE_LIMITING_ENABLED setting
    """
    if getattr(settings, 'RATE_LIMITING_ENABLED', True):
        return list(throttle_classes)
    return []  # Return empty list when rate limiting is disabled

class CustomLoginView(TokenObtainPairView):
    """
    Custom login view without rate limiting
    """
    # No throttle_classes - removes rate limiting
    pass

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    # Removed throttle_classes to eliminate rate limiting on registration

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [UserManagementPermission]
    throttle_classes = get_throttle_classes(CustomUserRateThrottle)  # Conditional rate limiting

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EpidemicDashboardView(APIView):
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)  # Conditional rate limiting
    
    def get(self, request):
        year = request.query_params.get('year', 2025)
        previous_year = request.query_params.get('prev_year', None)
        disease_name = request.query_params.get('disease_name', None)
        region = request.query_params.get('region', None)
        return Response(get_dashboard_counts(int(year), previous_year, disease_name, region))
    
class DiseaseYearsView(APIView):
    serializer_class = DiseaseYearSerializer
    permission_classes = [DiseaseManagementPermission]
    throttle_classes = [APIRateThrottle]  # General API rate limiting
    
    def get(self, request):
        disease_id = request.query_params.get('disease_id')
        disease_years = get_disease_years(disease_id)
        if isinstance(disease_years, dict) and 'error' in disease_years:
            return Response(disease_years, status=400)
        serializer = self.serializer_class(disease_years, many=True)
        return Response(serializer.data)
    
# class DiseaseYearsOnlyView(APIView):
#     serializer_class = DiseaseYearOnlySerializer
#     def get(self, request):
#         disease_years = get_disease_years_only()
#         serializer = self.serializer_class(disease_years, many=True)
#         return Response(serializer.data)
    
class DiseaseAllView(APIView):
    serializer_class = DiseaseSerializer
    permission_classes = [DiseaseManagementPermission]
    throttle_classes = [APIRateThrottle]  # General API rate limiting
    
    def get(self, request):
        disease_all = get_disease_all()
        serializer = self.serializer_class(disease_all, many=True)
        return Response(serializer.data)

class RegionalDiseaseRatesView(APIView):
    """
    Returns regional disease rates (cases per 1000 population) for a selected disease and year.
    Query params: disease (e.g. 'diabetes'), year (e.g. '2022')
    """
    permission_classes = [DashboardPermission]

    def get(self, request):
        disease = request.query_params.get('disease_name', None)
        year = request.query_params.get('year', None)
        
        if not disease or not year:
            return Response({'error': 'disease and year are required query parameters.'}, status=400)
        
        # Use the service to get regional disease rates
        result = get_regional_disease_rates(disease, year)
        
        if not result['success']:
            return Response({'error': result['error']}, status=result.get('status_code', 500))
        
        return Response(result['data'])

class RegionalDiseaseRatesStatisticsView(APIView):
    """
    Returns statistical summary for regional disease rates.
    Query params: disease (e.g. 'diabetes'), year (e.g. '2022')
    """
    permission_classes = [DashboardPermission]

    def get(self, request):
        disease = request.query_params.get('disease_name', None)
        year = request.query_params.get('year', None)
        
        if not disease or not year:
            return Response({'error': 'disease and year are required query parameters.'}, status=400)
        
        # Use the service to get rate statistics
        result = get_rate_statistics(disease, year)
        
        if not result['success']:
            return Response({'error': result['error']}, status=result.get('status_code', 500))
        
        return Response(result['statistics'])

class RegionalDiseaseRatesFiltersView(APIView):
    """
    Get available filter options for regional disease rates.
    """
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        return Response({
            'years': get_available_years_for_rates(),
            'regions': get_available_regions_for_rates(),
            'diseases': get_available_diseases_for_rates()
        })

class NationalHotspotsView(APIView):
    serializer_class = NationalHotspotsSerializer
    permission_classes = [HotspotsPermission]
    
    def get(self, request):
        # Get query parameters
        year = request.query_params.get('year')
        region = request.query_params.get('region')
        disease = request.query_params.get('disease')
        summary = request.query_params.get('summary', 'false').lower() == 'true'
        
        # Get filtered hotspots using service
        hotspots = get_national_hotspots(year=year, region=region, disease=disease)
        
        # If summary is requested, return aggregated data
        if summary:
            summary_data = get_national_hotspots_summary(hotspots, year=year, disease=disease)
            return Response(summary_data)
        
        # Pass disease filter and year filter as context to serializer
        serializer_context = {}
        if disease and disease != 'all':
            serializer_context['disease_filter'] = disease
        if year:
            serializer_context['year_filter'] = year
        serializer = self.serializer_class(hotspots, many=True, context=serializer_context)
        return Response(serializer.data)

class NationalHotspotsFiltersView(APIView):
    """Get available filter options for national hotspots"""
    permission_classes = [HotspotsPermission]
    
    def get(self, request):
        return Response({
            'years': get_available_years(),
            'regions': get_available_regions(),
            'diseases': get_available_diseases()
        })

class AllRegionsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        regions_path = os.path.join(settings.BASE_DIR, 'api', 'static', 'regions.json')
        with open(regions_path, 'r') as f:
            regions = json.load(f)
        return Response(regions)

# New Analytics Dashboard Views

class AnalyticsDashboardOverviewView(APIView):
    """Get overview statistics for the analytics dashboard"""
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        result = analytics_service.get_dashboard_overview()
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsPrincipalDiagnosesView(APIView):
    """Get top principal diagnoses with counts"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        year = request.query_params.get('year', None)
        orgname = request.query_params.get('orgname', None)
        
        # Validate year parameter if provided
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_principal_diagnoses(disease, year, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsAdditionalDiagnosesView(APIView):
    """Get top additional diagnoses with counts"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        year = request.query_params.get('year', None)
        orgname = request.query_params.get('orgname', None)
        
        # Validate year parameter if provided
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_additional_diagnoses(disease, year, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsNHIAStatusView(APIView):
    """Get NHIA status distribution with disease_name, year, locality, and orgname filters"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease_name = request.query_params.get('disease_name', None)
        year = request.query_params.get('year', None)
        locality = request.query_params.get('locality', None)
        orgname = request.query_params.get('orgname', None)
        
        if not disease_name:
            return Response({'error': 'disease_name is required as a query parameter.'}, status=400)
        
        try:
            year = int(year) if year is not None else None
        except ValueError:
            return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_nhia_status_filtered(disease_name, year, locality, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsPregnancyStatusView(APIView):
    """Get pregnancy status distribution with disease_name, year, locality, and orgname filters"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease_name = request.query_params.get('disease_name', None)
        year = request.query_params.get('year', None)
        locality = request.query_params.get('locality', None)
        orgname = request.query_params.get('orgname', None)
        
        if not disease_name:
            return Response({'error': 'disease_name is required as a query parameter.'}, status=400)
        
        try:
            year = int(year) if year is not None else None
        except ValueError:
            return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_pregnancy_status_filtered(disease_name, year, locality, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsHotspotsView(APIView):
    """Get disease hotspots by locality"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        year = request.query_params.get('year', None)
        orgname = request.query_params.get('orgname', None)
        
        # Validate year parameter if provided
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_hotspots_by_locality(disease, year, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsDiseaseComparisonView(APIView):
    """Compare two diseases"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease1 = request.query_params.get('disease1', 'diabetes')
        disease2 = request.query_params.get('disease2', 'malaria')
        year = request.query_params.get('year', None)
        orgname = request.query_params.get('orgname', None)
        
        # Validate year parameter if provided
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_disease_comparison(disease1, disease2, year, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsTrendsView(APIView):
    """Get trends by locality over time with optional year, orgname, locality, and months filters"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', 'diabetes')
        year = request.query_params.get('year', None)
        orgname = request.query_params.get('orgname', None)
        locality = request.query_params.get('locality', None)
        months = request.query_params.get('months', None)
        
        # Validate year parameter if provided
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'year must be an integer.'}, status=400)
        
        # Parse months parameter if provided
        months_list = None
        if months:
            try:
                # Handle comma-separated string like "3,6,9,10"
                months_list = [int(m.strip()) for m in months.split(',')]
                # Validate month numbers
                for month in months_list:
                    if month < 1 or month > 12:
                        return Response({'error': 'months must be between 1 and 12.'}, status=400)
            except ValueError:
                return Response({'error': 'months must be comma-separated integers (e.g., "3,6,9,10").'}, status=400)
        
        result = analytics_service.get_trends_by_locality(disease, year, orgname, locality, months_list)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

# Time Series Forecasting Views

class TimeSeriesForecastView(APIView):
    """Get time series forecast for disease data"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', 'diabetes')
        forecast_months = int(request.query_params.get('months', 3))
        locality = request.query_params.get('locality', None)
        
        if forecast_months not in [3, 6, 9, 12]:
            return Response({'error': 'Forecast months must be 3, 6, 9, or 12'}, status=400)
        
        result = forecasting_service.get_forecast(disease, forecast_months, locality)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class TimeSeriesMultiLocalityForecastView(APIView):
    """Get forecasts for multiple localities"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', 'diabetes')
        forecast_months = int(request.query_params.get('months', 3))
        top_n = int(request.query_params.get('top_n', 5))
        
        if forecast_months not in [3, 6, 9, 12]:
            return Response({'error': 'Forecast months must be 3, 6, 9, or 12'}, status=400)
        
        result = forecasting_service.get_multi_locality_forecast(disease, forecast_months, top_n)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class TimeSeriesSeasonalForecastView(APIView):
    """Get seasonal forecast with trend and seasonality"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', 'diabetes')
        forecast_months = int(request.query_params.get('months', 12))
        
        result = forecasting_service.get_seasonal_forecast(disease, forecast_months)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class TimeSeriesAccuracyMetricsView(APIView):
    """Get forecast accuracy metrics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', 'diabetes')
        test_months = int(request.query_params.get('test_months', 3))
        
        result = forecasting_service.get_forecast_accuracy_metrics(disease, test_months)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

# AI Insights Views

class AIInsightsView(APIView):
    """Get AI-powered insights for health data"""
    permission_classes = [DashboardPermission]
    throttle_classes = [BurstRateThrottle]  # Resource-intensive AI operations
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        insight_type = request.query_params.get('type', 'general')
        
        result = ai_insights_service.get_ai_insights(disease, insight_type)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AIStructuredAnalyticsView(APIView):
    """Get structured AI insights for analytics data with date/year focus"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(BurstRateThrottle)  # Conditional rate limiting
    
    def post(self, request):
        """
        Get structured AI insights for analytics data
        
        Expected request body:
        {
            "date_range": "2022-03",           // Optional: single month (YYYY-MM)
            "date_range": "2022-03:2022-08",   // Optional: month range (YYYY-MM:YYYY-MM)
            "date_range": "2022-03-01:2022-08-31", // Optional: full date range (YYYY-MM-DD:YYYY-MM-DD)
            "year": "2022",                    // Optional: specific year
            "disease": "diabetes",             // Optional: disease type filter
            "locality": "Kasoa",               // Optional: specific locality
            "hospital": "General Hospital"     // Optional: specific hospital (orgname)
        }
        
        Date range formats supported:
        - Single month: "2022-03" (March 2022 only)
        - Month range: "2022-03:2022-08" (March 2022 to August 2022)
        - Full date range: "2022-03-01:2022-08-31" (specific dates)
        
        If no body is provided, analyzes all available data.
        """
        from django.core.cache import cache
        import hashlib
        import json
        
        # Get parameters (default to None if not provided)
        date_range = request.data.get('date_range', None)
        year = request.data.get('year', None)
        disease = request.data.get('disease', None)
        locality = request.data.get('locality', None)
        hospital = request.data.get('hospital', None)  # New hospital filter
        
        # Create cache key based on parameters
        cache_params = {
            'date_range': date_range,
            'year': year,
            'disease': disease,
            'locality': locality,
            'hospital': hospital  # Include hospital in cache key
        }
        
        # Generate unique cache key
        cache_key = self._generate_cache_key(cache_params)
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response({
                'data': cached_result,
                'cached': True,
                'cache_key': cache_key,
                'message': 'Response served from cache'
            })
        
        # Fetch analytics data from database
        analytics_data = self._get_analytics_data_from_db(
            date_range=date_range,
            year=year,
            disease=disease,
            locality=locality,
            hospital=hospital  # Pass hospital parameter
        )
        
        if not analytics_data:
            # Get debug information about what's available
            from disease_monitor.models import HospitalHealthData
            
            debug_info = {
                'available_localities': list(HospitalHealthData.objects.values('address_locality').distinct()[:10]),
                'available_hospitals': list(HospitalHealthData.objects.values('orgname').distinct()[:10]),
                'available_diseases': list(HospitalHealthData.objects.values('principal_diagnosis_new').distinct()[:10]),
                'requested_filters': {
                    'date_range': date_range,
                    'year': year,
                    'disease': disease,
                    'locality': locality,
                    'hospital': hospital
                }
            }
            
            return Response({
                'error': 'No data found for the specified filters',
                'filters': cache_params,
                'cache_key': cache_key,
                'debug_info': debug_info,
                'suggestions': [
                    'Check if the locality name matches exactly (case-sensitive)',
                    'Check if the hospital name matches exactly',
                    'Try using partial names (e.g., "Ablekuma" instead of "Ablekuma Fanmilk")',
                    'Check if data exists for the specified date range',
                    'Verify the disease name is correct'
                ]
            }, status=404)
        
        result = ai_insights_service.get_structured_analytics_insights(
            analytics_data=analytics_data,
            date_range=date_range,
            year=year,
            disease=disease,
            locality=locality,
            hospital=hospital  # Pass hospital parameter
        )
        
        if not result['success']:
            return Response({
                'error': result['error'],
                'mock_response': result.get('mock_response'),
                'cache_key': cache_key
            }, status=500)
        
        # Cache the successful result
        cache_timeout = self._get_cache_timeout(cache_params)
        cache.set(cache_key, result['data'], cache_timeout)
        
        return Response({
            'data': result['data'],
            'cached': False,
            'cache_key': cache_key,
            'cache_timeout': cache_timeout,
            'message': 'Response generated and cached'
        })
    
    def _generate_cache_key(self, params):
        """Generate a unique cache key based on parameters"""
        import hashlib
        
        # Create a string representation of parameters
        param_string = json.dumps(params, sort_keys=True)
        
        # Generate hash
        hash_object = hashlib.md5(param_string.encode())
        return f"structured_analytics_{hash_object.hexdigest()}"
    
    def _get_cache_timeout(self, params):
        """Determine cache timeout based on parameters"""
        # Shorter cache for specific filters (more likely to change)
        if params['date_range'] or params['locality'] or params['hospital']:
            return 1800  # 30 minutes
        
        # Medium cache for year/disease filters
        if params['year'] or params['disease']:
            return 3600  # 1 hour
        
        # Longer cache for all data (less likely to change frequently)
        return 7200  # 2 hours
    
    def _get_analytics_data_from_db(self, date_range=None, year=None, disease=None, locality=None, hospital=None):
        """
        Fetch analytics data from HospitalHealthData model based on filters
        
        Date range formats supported:
        - Single month: "2022-03" (March 2022 only)
        - Month range: "2022-03:2022-08" (March 2022 to August 2022)
        - Full date range: "2022-03-01:2022-08-31" (specific dates)
        """
        from disease_monitor.models import HospitalHealthData
        from django.db.models import Count, Q
        from datetime import datetime
        import json
        
        try:
            # Start with all data
            queryset = HospitalHealthData.objects.all()
            
            # Apply date filters
            if date_range:
                queryset = self._apply_date_range_filter(queryset, date_range)
            
            elif year:
                # Filter by year
                queryset = queryset.filter(month__year=int(year))
            
            # Apply locality filter with more flexible matching
            if locality:
                # Try exact match first
                locality_queryset = queryset.filter(address_locality__iexact=locality)
                if locality_queryset.count() == 0:
                    # Try partial match
                    locality_queryset = queryset.filter(address_locality__icontains=locality)
                    if locality_queryset.count() == 0:
                        # Try normalized matching (remove spaces, convert to uppercase)
                        normalized_locality = locality.replace(' ', '').upper()
                        locality_queryset = queryset.filter(
                            address_locality__iregex=r'^' + normalized_locality.replace(' ', '.*') + r'$'
                        )
                
                queryset = locality_queryset
            
            # Apply hospital filter with more flexible matching
            if hospital:
                # Try exact match first
                hospital_queryset = queryset.filter(orgname__iexact=hospital)
                if hospital_queryset.count() == 0:
                    # Try partial match
                    hospital_queryset = queryset.filter(orgname__icontains=hospital)
                    if hospital_queryset.count() == 0:
                        # Try normalized matching
                        normalized_hospital = hospital.replace(' ', '').upper()
                        hospital_queryset = queryset.filter(
                            orgname__iregex=r'^' + normalized_hospital.replace(' ', '.*') + r'$'
                        )
                
                queryset = hospital_queryset
            
            if disease:
                # Filter by disease (based on diagnosis)
                disease_keywords = {
                    'diabetes': ['diabetes', 'E08', 'E09', 'E10', 'E11', 'E13'],
                    'malaria': ['malaria', 'B50', 'B51', 'B52', 'B53', 'B54'],
                    'cholera': ['cholera', 'A00'],
                    'meningitis': ['meningitis', 'G00', 'G01', 'G02', 'G03']
                }
                
                if disease.lower() in disease_keywords:
                    keywords = disease_keywords[disease.lower()]
                    disease_filter = Q()
                    for keyword in keywords:
                        disease_filter |= Q(principal_diagnosis_new__icontains=keyword)
                        disease_filter |= Q(additional_diagnosis_new__icontains=keyword)
                    queryset = queryset.filter(disease_filter)
            
            # Get total cases
            total_cases = queryset.count()
            
            # Debug information
            debug_info = {
                'total_cases_after_filters': total_cases,
                'filters_applied': {
                    'date_range': date_range,
                    'year': year,
                    'disease': disease,
                    'locality': locality,
                    'hospital': hospital
                }
            }
            
            # If no data found, try to find what's available
            if total_cases == 0:
                # Check what localities exist
                available_localities = HospitalHealthData.objects.values('address_locality').distinct()
                debug_info['available_localities'] = list(available_localities)[:10]  # First 10
                
                # Check what hospitals exist
                available_hospitals = HospitalHealthData.objects.values('orgname').distinct()
                debug_info['available_hospitals'] = list(available_hospitals)[:10]  # First 10
                
                # Check what diseases exist
                available_diseases = HospitalHealthData.objects.values('principal_diagnosis_new').distinct()
                debug_info['available_diseases'] = list(available_diseases)[:10]  # First 10
                
                print(f"DEBUG: No data found. Debug info: {debug_info}")
                return None
            
            # Age distribution
            age_distribution = {
                "0-18": queryset.filter(age__lte=18).count(),
                "19-35": queryset.filter(age__gt=18, age__lte=35).count(),
                "36-60": queryset.filter(age__gt=35, age__lte=60).count(),
                "60+": queryset.filter(age__gt=60).count()
            }
            
            # Gender distribution
            gender_distribution = dict(queryset.values('sex').annotate(count=Count('sex')).values_list('sex', 'count'))
            
            # Top localities
            top_localities = dict(queryset.values('address_locality').annotate(
                count=Count('address_locality')
            ).order_by('-count')[:10].values_list('address_locality', 'count'))
            
            # NHIA coverage
            nhia_coverage = {
                "insured": queryset.filter(nhia_patient=True).count(),
                "uninsured": queryset.filter(nhia_patient=False).count()
            }
            
            # Pregnancy status
            pregnancy_status = {
                "pregnant": queryset.filter(pregnant_patient=True).count(),
                "not_pregnant": queryset.filter(pregnant_patient=False).count()
            }
            
            # Top diagnoses
            top_diagnoses = dict(queryset.values('principal_diagnosis_new').annotate(
                count=Count('principal_diagnosis_new')
            ).order_by('-count')[:10].values_list('principal_diagnosis_new', 'count'))
            
            # Additional diagnoses (comorbidities)
            additional_diagnoses = dict(queryset.exclude(
                additional_diagnosis_new__isnull=True
            ).exclude(
                additional_diagnosis_new__exact=''
            ).values('additional_diagnosis_new').annotate(
                count=Count('additional_diagnosis_new')
            ).order_by('-count')[:10].values_list('additional_diagnosis_new', 'count'))
            
            # Temporal patterns (monthly distribution)
            temporal_patterns = self._get_temporal_patterns(queryset, date_range, year)
            
            # Geographic distribution
            geographic_distribution = dict(queryset.values('address_locality').annotate(
                count=Count('address_locality')
            ).order_by('-count')[:20].values_list('address_locality', 'count'))
            
            # Facility utilization
            facility_utilization = dict(queryset.values('orgname').annotate(
                count=Count('orgname')
            ).order_by('-count')[:10].values_list('orgname', 'count'))
            
            # Compile analytics data
            analytics_data = {
                "total_cases": total_cases,
                "age_distribution": age_distribution,
                "gender_distribution": gender_distribution,
                "top_localities": top_localities,
                "nhia_coverage": nhia_coverage,
                "pregnancy_status": pregnancy_status,
                "top_diagnoses": top_diagnoses,
                "additional_diagnoses": additional_diagnoses,
                "temporal_patterns": temporal_patterns,
                "geographic_distribution": geographic_distribution,
                "facility_utilization": facility_utilization,
                "filters_applied": {
                    "date_range": date_range,
                    "year": year,
                    "disease": disease,
                    "locality": locality,
                    "hospital": hospital
                },
                "debug_info": debug_info
            }
            
            # Add disease-specific data if disease filter is applied
            if disease:
                analytics_data["disease_specific"] = {
                    "disease_type": disease,
                    "total_cases": total_cases,
                    "age_distribution": age_distribution,
                    "gender_distribution": gender_distribution,
                    "geographic_hotspots": top_localities
                }
            
            return analytics_data
            
        except Exception as e:
            print(f"Error fetching analytics data: {e}")
            return None
    
    def _apply_date_range_filter(self, queryset, date_range):
        """
        Apply date range filter to queryset
        
        Supports multiple formats:
        - Single month: "2022-03"
        - Month range: "2022-03:2022-08"
        - Full date range: "2022-03-01:2022-08-31"
        """
        try:
            if ':' in date_range:
                # Range format: "2022-03:2022-08" or "2022-03-01:2022-08-31"
                start_str, end_str = date_range.split(':', 1)
                
                # Try full date format first (YYYY-MM-DD)
                try:
                    start_date = datetime.strptime(start_str, "%Y-%m-%d")
                    end_date = datetime.strptime(end_str, "%Y-%m-%d")
                    return queryset.filter(month__gte=start_date, month__lte=end_date)
                except ValueError:
                    pass
                
                # Try month format (YYYY-MM)
                try:
                    start_date = datetime.strptime(start_str, "%Y-%m")
                    end_date = datetime.strptime(end_str, "%Y-%m")
                    
                    # For month ranges, include the entire end month
                    # If end_str is "2022-08", include all of August 2022
                    if end_date.month == 12:
                        end_date = datetime(end_date.year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(end_date.year, end_date.month + 1, 1) - timedelta(days=1)
                    
                    return queryset.filter(month__gte=start_date, month__lte=end_date)
                except ValueError:
                    pass
                    
            else:
                # Single month format: "2022-03"
                try:
                    date_obj = datetime.strptime(date_range, "%Y-%m")
                    return queryset.filter(month__year=date_obj.year, month__month=date_obj.month)
                except ValueError:
                    pass
                    
        except Exception as e:
            print(f"Error parsing date range '{date_range}': {e}")
            
        # If parsing fails, return original queryset
        return queryset
    
    def _get_temporal_patterns(self, queryset, date_range, year):
        """
        Get temporal patterns based on date filters
        """
        temporal_patterns = {}
        
        if date_range and ':' in date_range:
            # For date ranges, get monthly breakdown
            try:
                start_str, end_str = date_range.split(':', 1)
                
                # Try month format first
                try:
                    start_date = datetime.strptime(start_str, "%Y-%m")
                    end_date = datetime.strptime(end_str, "%Y-%m")
                    
                    current_date = start_date
                    while current_date <= end_date:
                        month_key = f"{current_date.year}-{current_date.month:02d}"
                        month_count = queryset.filter(
                            month__year=current_date.year, 
                            month__month=current_date.month
                        ).count()
                        
                        if month_count > 0:
                            temporal_patterns[month_key] = month_count
                        
                        # Move to next month
                        if current_date.month == 12:
                            current_date = datetime(current_date.year + 1, 1, 1)
                        else:
                            current_date = datetime(current_date.year, current_date.month + 1, 1)
                            
                except ValueError:
                    pass
                    
            except Exception as e:
                print(f"Error generating temporal patterns: {e}")
                
        elif year:
            # Get monthly data for the year
            for month in range(1, 13):
                month_count = queryset.filter(month__year=int(year), month__month=month).count()
                if month_count > 0:
                    temporal_patterns[f"{year}-{month:02d}"] = month_count
                    
        elif date_range and ':' not in date_range:
            # Single month - just show that month
            try:
                date_obj = datetime.strptime(date_range, "%Y-%m")
                month_count = queryset.count()  # Already filtered for this month
                if month_count > 0:
                    temporal_patterns[date_range] = month_count
            except ValueError:
                pass
        
        return temporal_patterns

class AIQAView(APIView):
    """Get AI-powered Q&A response"""
    permission_classes = [DashboardPermission]
    throttle_classes = [BurstRateThrottle]  # Resource-intensive AI operations
    
    def post(self, request):
        question = request.data.get('question')
        context = request.data.get('context', None)
        
        if not question:
            return Response({'error': 'Question is required'}, status=400)
        
        result = ai_insights_service.get_ai_qa_response(question, context)
        if not result['success']:
            return Response({'error': result['error'], 'mock_response': result.get('mock_response')}, status=500)
        return Response(result['data'])

class AIAnomalyDetectionView(APIView):
    """Detect anomalies in health data using AI"""
    permission_classes = [DashboardPermission]
    throttle_classes = [BurstRateThrottle]  # Resource-intensive AI operations
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        
        result = ai_insights_service.get_anomaly_detection(disease)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsLocalitiesView(APIView):
    """Get all unique localities from HospitalHealthData"""
    permission_classes = [DashboardPermission]
    throttle_classes = [APIRateThrottle]  # General API rate limiting

    def get(self, request):
        result = analytics_service.get_all_localities()
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response({'localities': result['localities']})

class AnalyticsOrgnamesView(APIView):
    """Get all unique orgnames (hospitals) from HospitalHealthData"""
    permission_classes = [DashboardPermission]
    throttle_classes = [APIRateThrottle]  # General API rate limiting

    def get(self, request):
        result = analytics_service.get_available_orgnames()
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response({'orgnames': result['orgnames']})

class AnalyticsAgeDistributionView(APIView):
    """Get age distribution with optional disease, year, and orgname filters"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        year = request.query_params.get('year', None)
        orgname = request.query_params.get('orgname', None)
        
        # Validate year parameter if provided
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_age_distribution(disease, year, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsSexDistributionView(APIView):
    """Get sex distribution with optional disease, year, and orgname filters"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        year = request.query_params.get('year', None)
        orgname = request.query_params.get('orgname', None)
        
        # Validate year parameter if provided
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                return Response({'error': 'year must be an integer.'}, status=400)
        
        result = analytics_service.get_sex_distribution(disease, year, orgname)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class DiseaseTrendsAPIView(APIView):
    throttle_classes = [APIRateThrottle]  # General API rate limiting
    
    def get(self, request):
        disease_trends = DiseaseTrends.objects.all()
        serializer = DiseaseTrendsSerializer(disease_trends, many=True)
        return Response(serializer.data)

class PredictDiseaseView(APIView):
    """Predict disease for a patient using enhanced XGBoost models with Vertex AI integration."""
    permission_classes = [DashboardPermission]
    throttle_classes = [BurstRateThrottle]  # Resource-intensive ML operations
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize DiseaseMonitor with Vertex AI configuration
        project_id = os.getenv('GCP_PROJECT_ID')
        location = os.getenv('GCP_LOCATION')
        model_name = os.getenv('VERTEX_AI_MODEL_NAME')
        
        if project_id:
            self.monitor = DiseaseMonitor(
                project_id=project_id,
                location=location,
                model_name=model_name
            )
        else:
            # Fallback to non-Vertex AI mode
            self.monitor = DiseaseMonitor()
        
        # Load the new v2 models
        models_path = "src/artifacts/models"
        if os.path.exists(models_path):
            self.monitor.load_models(models_path)

    def post(self, request):
        data = request.data
        
        # Required fields with simple snake_case keys
        required_fields = ['age', 'gender', 'pregnant_patient', 'nhia_patient', 'locality', 'schedule_date']
        missing = [f for f in required_fields if data.get(f) is None]
        if missing:
            return Response({'error': f'Missing required fields: {", ".join(missing)}'}, status=400)

        # Extract data with simple keys
        age = data.get('age')  # Now expects numeric value like 25
        gender = data.get('gender')
        pregnant_patient = data.get('pregnant_patient')
        nhia_patient = data.get('nhia_patient')
        locality = data.get('locality')
        schedule_date = data.get('schedule_date')
        medicine_prescribed = data.get('medicine_prescribed', '')
        # Remove diagnosis fields - these are what we're predicting, not input features
        # principal_diagnosis = data.get('principal_diagnosis', '')
        # additional_diagnosis = data.get('additional_diagnosis', '')
        cost_of_treatment = data.get('cost_of_treatment', None)
        disease_type = data.get('disease_type', 'diabetes')  # Default to diabetes
        symptoms_text = data.get('symptoms_text', '')  # Optional: for Vertex AI symptom analysis
        vertex_ai_enabled = data.get('vertex_ai_enabled', True)  # Default to True for new system

        # Validate age is numeric
        try:
            age = int(age) if age is not None else None
        except (ValueError, TypeError):
            return Response({'error': 'Age must be a numeric value (e.g., 25)'}, status=400)

        # Build DataFrame for prediction with CSV column names (internal format)
        input_data = {
            'Age': age,
            'Gender': gender,
            'Pregnant Patient': pregnant_patient,
            'NHIA Patient': nhia_patient,
            'Locality': locality,
            'Schedule Date': schedule_date,
            'Medicine Prescribed': medicine_prescribed
            # Removed diagnosis fields - these are predictions, not inputs
        }
        
        # Add cost if provided (convert to CSV column name)
        if cost_of_treatment is not None:
            input_data['Cost of Treatment (GHS )'] = cost_of_treatment
        
        input_df = pd.DataFrame([input_data])
        
        # Check if model is available
        if disease_type.lower() not in self.monitor.models:
            return Response({
                'error': f'Model for {disease_type} not found. Available models: {list(self.monitor.models.keys())}'
            }, status=400)

        # Make prediction using new enhanced system
        try:
            if vertex_ai_enabled and symptoms_text:
                # Use enhanced prediction with Vertex AI symptom analysis
                results = self.monitor.predict_with_new_models(
                    data=input_df,
                    disease_name=disease_type.lower(),
                    symptoms_text=symptoms_text,
                    cost_optional=True
                )
                
                if results:
                    result = results[0]
                    prediction = result['prediction']
                    base_probability = result['base_probability']
                    symptom_score = result.get('symptom_score')
                    combined_probability = result['combined_probability']
                    locality_used = result.get('locality')
                    cost_included = result.get('cost_included', False)
                    features_used = result.get('features_used', [])
                    
                    # Format symptom score for logging
                    if symptom_score is not None:
                        symptom_text = f"{symptom_score:.3f}"
                    else:
                        symptom_text = "N/A"
                    
                    # Log the prediction
                    log = PredictionLog(
                        orgname=data.get('orgname', 'Unknown'),
                        address_locality=locality,
                        age=age,
                        sex=gender,
                        pregnant_patient=pregnant_patient,
                        nhia_patient=nhia_patient,
                        disease_type=disease_type,
                        prediction=str(prediction),
                        probability=combined_probability,
                        gemini_enabled=vertex_ai_enabled,
                        gemini_recommendation=f"Base: {base_probability:.3f}, Symptoms: {symptom_text}, Combined: {combined_probability:.3f}"
                    )
                    log.save()

                    response_data = {
                        'prediction': prediction,
                        'base_probability': base_probability,
                        'symptom_score': symptom_score,
                        'combined_probability': combined_probability,
                        'vertex_ai_enabled': vertex_ai_enabled,
                        'locality': locality_used,
                        'cost_included': cost_included,
                        'features_used': features_used,
                        'analysis_breakdown': {
                            'demographic_clinical_score': base_probability,
                            'symptom_analysis_score': symptom_score,
                            'final_combined_score': combined_probability,
                            'model_version': 'v2_enhanced'
                        }
                    }
                    
                    # Add dynamic threshold if available
                    if 'dynamic_threshold' in result:
                        response_data['dynamic_threshold'] = result['dynamic_threshold']
                    
                    return Response(response_data)
                else:
                    return Response({'error': 'No prediction results returned'}, status=500)
            else:
                # Use enhanced prediction without symptoms
                results = self.monitor.predict_with_new_models(
                    data=input_df,
                    disease_name=disease_type.lower(),
                    cost_optional=True
                )
                
                if results:
                    result = results[0]
                    prediction = result['prediction']
                    base_probability = result['base_probability']
                    locality_used = result.get('locality')
                    cost_included = result.get('cost_included', False)
                    features_used = result.get('features_used', [])

                    # Log the prediction
                    log = PredictionLog(
                        orgname=data.get('orgname', 'Unknown'),
                        address_locality=locality,
                        age=age,
                        sex=gender,
                        pregnant_patient=pregnant_patient,
                        nhia_patient=nhia_patient,
                        disease_type=disease_type,
                        prediction=str(prediction),
                        probability=base_probability,
                        gemini_enabled=vertex_ai_enabled,
                        gemini_recommendation=f"Enhanced v2 model prediction: {base_probability:.3f}"
                    )
                    log.save()

                    return Response({
                        'prediction': prediction,
                        'probability': base_probability,
                        'vertex_ai_enabled': vertex_ai_enabled,
                        'locality': locality_used,
                        'cost_included': cost_included,
                        'features_used': features_used,
                        'note': 'Using enhanced v2 model (demographic/clinical features only)',
                        'model_version': 'v2_enhanced'
                    })
                else:
                    return Response({'error': 'No prediction results returned'}, status=500)

        except Exception as e:
            return Response({'error': f'Prediction failed: {str(e)}'}, status=500)

# Test Rate Limiting View
class TestRateLimitView(APIView):
    """Test view to demonstrate rate limiting"""
    permission_classes = [AllowAny]
    throttle_classes = [BurstRateThrottle]  # 60 requests per minute
    
    def get(self, request):
        return Response({
            'message': 'Rate limiting test successful',
            'timestamp': time.time(),
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'ip': request.META.get('REMOTE_ADDR', 'unknown')
        })
    
    def post(self, request):
        return Response({
            'message': 'POST rate limiting test successful',
            'data': request.data,
            'timestamp': time.time()
        })

# Rate Limit Info View
class RateLimitInfoView(APIView):
    """Get current rate limit information for debugging"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from .utils import get_rate_limit_info
        
        # Get rate limit info for different throttle classes
        info = {
            'user_throttle': get_rate_limit_info(request, CustomUserRateThrottle),
            'api_throttle': get_rate_limit_info(request, APIRateThrottle),
            'burst_throttle': get_rate_limit_info(request, BurstRateThrottle),
            'sensitive_throttle': get_rate_limit_info(request, SensitiveEndpointThrottle),
        }
        
        return Response({
            'rate_limit_info': info,
            'user': request.user.username,
            'ip': request.META.get('REMOTE_ADDR', 'unknown')
        })

# Cache Management Views

class CacheManagementView(APIView):
    """Manage cache for structured analytics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get cache statistics"""
        from django.core.cache import cache
        from django.core.cache.backends.locmem import LocMemCache
        
        # Get cache info
        cache_info = {
            'cache_backend': str(type(cache)),
            'cache_location': getattr(cache, '_cache', {}),
        }
        
        # Count structured analytics cache entries
        cache_keys = []
        if hasattr(cache, '_cache'):
            cache_keys = [key for key in cache._cache.keys() if key.startswith('structured_analytics_')]
        
        cache_info['structured_analytics_entries'] = len(cache_keys)
        cache_info['cache_keys'] = cache_keys[:10]  # Show first 10 keys
        
        return Response({
            'cache_info': cache_info,
            'message': f'Found {len(cache_keys)} structured analytics cache entries'
        })
    
    def delete(self, request):
        """Clear structured analytics cache"""
        from django.core.cache import cache
        
        # Get specific cache key to clear
        cache_key = request.query_params.get('cache_key')
        
        if cache_key:
            # Clear specific cache entry
            cache.delete(cache_key)
            return Response({
                'message': f'Cleared cache entry: {cache_key}',
                'cleared_key': cache_key
            })
        else:
            # Clear all structured analytics cache entries
            if hasattr(cache, '_cache'):
                keys_to_clear = [key for key in cache._cache.keys() if key.startswith('structured_analytics_')]
                for key in keys_to_clear:
                    cache.delete(key)
                
                return Response({
                    'message': f'Cleared {len(keys_to_clear)} structured analytics cache entries',
                    'cleared_count': len(keys_to_clear)
                })
            else:
                return Response({
                    'message': 'No cache entries found to clear'
                })

class CacheStatusView(APIView):
    """Get cache status for a specific request"""
    permission_classes = [DashboardPermission]
    
    def post(self, request):
        """Check if a request would be served from cache"""
        from django.core.cache import cache
        import hashlib
        import json
        
        # Get parameters
        date_range = request.data.get('date_range', None)
        year = request.data.get('year', None)
        disease = request.data.get('disease', None)
        locality = request.data.get('locality', None)
        hospital = request.data.get('hospital', None)  # Add hospital parameter
        
        # Create cache key
        cache_params = {
            'date_range': date_range,
            'year': year,
            'disease': disease,
            'locality': locality,
            'hospital': hospital  # Include hospital in cache params
        }
        
        # Generate cache key (same logic as main view)
        param_string = json.dumps(cache_params, sort_keys=True)
        hash_object = hashlib.md5(param_string.encode())
        cache_key = f"structured_analytics_{hash_object.hexdigest()}"
        
        # Check if cached
        cached_result = cache.get(cache_key)
        
        # Get cache timeout
        if cache_params['date_range'] or cache_params['locality'] or cache_params['hospital']:
            timeout = 1800  # 30 minutes
        elif cache_params['year'] or cache_params['disease']:
            timeout = 3600  # 1 hour
        else:
            timeout = 7200  # 2 hours
        
        return Response({
            'cache_key': cache_key,
            'is_cached': cached_result is not None,
            'cache_timeout': timeout,
            'parameters': cache_params,
            'message': 'Cache status checked successfully'
        })

class HospitalLocalitiesView(APIView):
    """Get hospital localities for filtering"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)
    
    def get(self, request):
        """
        Get hospital localities with optional filtering
        
        Query parameters:
        - locality: Filter by specific locality
        - orgname: Filter by specific hospital
        - search: Search in both locality and orgname
        """
        # Get query parameters
        locality = request.query_params.get('locality')
        orgname = request.query_params.get('orgname')
        search = request.query_params.get('search')
        
        # Start with all records
        queryset = HospitalLocalities.objects.all()
        
        # Apply filters
        if locality:
            queryset = queryset.filter(locality__icontains=locality)
        
        if orgname:
            queryset = queryset.filter(orgname__icontains=orgname)
        
        if search:
            queryset = queryset.filter(
                models.Q(locality__icontains=search) | 
                models.Q(orgname__icontains=search)
            )
        
        # Serialize data
        serializer = HospitalLocalitiesListSerializer(queryset, many=True)
        
        return Response({
            'data': serializer.data,
            'count': len(serializer.data),
            'filters_applied': {
                'locality': locality,
                'orgname': orgname,
                'search': search
            }
        })

class HospitalLocalitiesStatsView(APIView):
    """Get statistics about hospital localities"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)
    
    def get(self, request):
        """Get statistics about hospital localities"""
        try:
            # Get basic counts
            total_combinations = HospitalLocalities.objects.count()
            unique_localities = HospitalLocalities.objects.values('locality').distinct().count()
            unique_hospitals = HospitalLocalities.objects.values('orgname').distinct().count()
            
            # Get top localities by hospital count
            top_localities = HospitalLocalities.objects.values('locality').annotate(
                hospital_count=models.Count('orgname')
            ).order_by('-hospital_count')[:10]
            
            # Get top hospitals by locality count
            top_hospitals = HospitalLocalities.objects.values('orgname').annotate(
                locality_count=models.Count('locality')
            ).order_by('-locality_count')[:10]
            
            return Response({
                'statistics': {
                    'total_combinations': total_combinations,
                    'unique_localities': unique_localities,
                    'unique_hospitals': unique_hospitals
                },
                'top_localities': list(top_localities),
                'top_hospitals': list(top_hospitals)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error getting statistics: {str(e)}'
            }, status=500)

class HospitalLocalitiesSearchView(APIView):
    """Search hospital localities"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)
    
    def get(self, request):
        """
        Search hospital localities
        
        Query parameters:
        - q: Search query
        - type: 'locality' or 'hospital' (optional)
        """
        query = request.query_params.get('q', '')
        search_type = request.query_params.get('type', 'both')
        
        if not query:
            return Response({
                'error': 'Search query is required'
            }, status=400)
        
        try:
            if search_type == 'locality':
                results = HospitalLocalities.search_localities(query)
                data = [{'locality': locality} for locality in results]
            elif search_type == 'hospital':
                results = HospitalLocalities.search_hospitals(query)
                data = [{'orgname': hospital} for hospital in results]
            else:
                # Search both
                localities = HospitalLocalities.search_localities(query)
                hospitals = HospitalLocalities.search_hospitals(query)
                data = {
                    'localities': list(localities),
                    'hospitals': list(hospitals)
                }
            
            return Response({
                'query': query,
                'type': search_type,
                'results': data,
                'count': len(data) if isinstance(data, list) else len(data.get('localities', [])) + len(data.get('hospitals', []))
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error searching: {str(e)}'
            }, status=500)

class HospitalLocalitiesByHospitalView(APIView):
    """Get localities grouped by hospital"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)
    
    def get(self, request):
        """
        Get localities grouped by hospital
        
        Query parameters:
        - hospital: Filter by specific hospital name (optional)
        - locality: Filter by specific locality (optional)
        - search: Search in hospital names (optional)
        - limit: Limit number of hospitals returned (optional, default: all)
        - sort: Sort order - 'name' (alphabetical) or 'count' (by locality count) (optional, default: 'name')
        """
        # Get query parameters
        hospital_filter = request.query_params.get('hospital')
        locality_filter = request.query_params.get('locality')
        search = request.query_params.get('search')
        limit = request.query_params.get('limit')
        sort = request.query_params.get('sort', 'name')
        
        try:
            # Start with all records
            queryset = HospitalLocalities.objects.all()
            
            # Apply filters
            if hospital_filter:
                queryset = queryset.filter(orgname__icontains=hospital_filter)
            
            if locality_filter:
                queryset = queryset.filter(locality__icontains=locality_filter)
            
            if search:
                queryset = queryset.filter(orgname__icontains=search)
            
            # Group by hospital and get localities
            if sort == 'count':
                # Sort by locality count (descending)
                hospitals_data = queryset.values('orgname').annotate(
                    locality_count=models.Count('locality')
                ).order_by('-locality_count')
            else:
                # Sort alphabetically by hospital name
                hospitals_data = queryset.values('orgname').annotate(
                    locality_count=models.Count('locality')
                ).order_by('orgname')
            
            # Apply limit if specified
            if limit:
                try:
                    limit = int(limit)
                    hospitals_data = hospitals_data[:limit]
                except ValueError:
                    pass
            
            # Build response data
            result = []
            for hospital_info in hospitals_data:
                hospital_name = hospital_info['orgname']
                locality_count = hospital_info['locality_count']
                
                # Get localities for this hospital
                hospital_localities = queryset.filter(orgname=hospital_name).values_list('locality', flat=True).distinct()
                
                result.append({
                    'hospital': hospital_name,
                    'locality_count': locality_count,
                    'localities': sorted(list(hospital_localities))
                })
            
            # Add summary statistics
            total_hospitals = len(result)
            total_localities = sum(item['locality_count'] for item in result)
            unique_localities = queryset.values('locality').distinct().count()
            
            return Response({
                'data': result,
                'summary': {
                    'total_hospitals': total_hospitals,
                    'total_localities': total_localities,
                    'unique_localities': unique_localities,
                    'filters_applied': {
                        'hospital': hospital_filter,
                        'locality': locality_filter,
                        'search': search,
                        'limit': limit,
                        'sort': sort
                    }
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error getting localities by hospital: {str(e)}'
            }, status=500)

class HospitalView(APIView):
    """Get hospitals for filtering and management"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)

    def get(self, request):
        """Get hospitals with optional filtering"""
        try:
            # Get query parameters
            name = request.query_params.get('name', None)
            search = request.query_params.get('search', None)
            limit = request.query_params.get('limit', None)
            
            # Start with all hospitals
            queryset = Hospital.objects.all()
            
            # Apply filters
            filters_applied = {}
            
            if name:
                queryset = queryset.filter(name__icontains=name)
                filters_applied['name'] = name
            
            if search:
                queryset = queryset.filter(name__icontains=search)
                filters_applied['search'] = search
            
            # Apply limit
            if limit:
                try:
                    limit = int(limit)
                    queryset = queryset[:limit]
                    filters_applied['limit'] = limit
                except ValueError:
                    return Response(
                        {'error': 'Invalid limit parameter. Must be a number.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Serialize the data
            serializer = HospitalListSerializer(queryset, many=True)
            
            return Response({
                'data': serializer.data,
                'summary': {
                    'total_hospitals': queryset.count(),
                    'filters_applied': filters_applied
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving hospitals: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HospitalDetailView(APIView):
    """Get detailed information about a specific hospital"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)

    def get(self, request, hospital_id=None, slug=None):
        """Get hospital details by ID or slug"""
        try:
            hospital = None
            
            if hospital_id:
                try:
                    hospital = Hospital.objects.get(id=hospital_id)
                except Hospital.DoesNotExist:
                    return Response(
                        {'error': f'Hospital with ID {hospital_id} not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            elif slug:
                hospital = Hospital.get_by_slug(slug)
                if not hospital:
                    return Response(
                        {'error': f'Hospital with slug "{slug}" not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {'error': 'Either hospital_id or slug parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = HospitalSerializer(hospital)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving hospital details: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HospitalStatsView(APIView):
    """Get statistics about hospitals"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)

    def get(self, request):
        """Get hospital statistics"""
        try:
            total_hospitals = Hospital.objects.count()
            
            # Get hospitals created in the last 30 days
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_hospitals = Hospital.objects.filter(created_at__gte=thirty_days_ago).count()
            
            # Get top hospitals by name (alphabetically)
            top_hospitals = Hospital.objects.all().order_by('name')[:10]
            top_hospitals_data = HospitalListSerializer(top_hospitals, many=True).data
            
            return Response({
                'summary': {
                    'total_hospitals': total_hospitals,
                    'recent_hospitals': recent_hospitals,
                    'recent_period_days': 30
                },
                'top_hospitals': top_hospitals_data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving hospital statistics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HospitalSearchView(APIView):
    """Search hospitals by name"""
    permission_classes = [DashboardPermission]
    throttle_classes = get_throttle_classes(APIRateThrottle)

    def get(self, request):
        """Search hospitals"""
        try:
            query = request.query_params.get('q', '')
            search_type = request.query_params.get('type', 'name')  # 'name' or 'slug'
            limit = request.query_params.get('limit', 10)
            
            if not query:
                return Response(
                    {'error': 'Query parameter "q" is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                limit = int(limit)
            except ValueError:
                return Response(
                    {'error': 'Invalid limit parameter. Must be a number.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform search based on type
            if search_type == 'slug':
                queryset = Hospital.objects.filter(slug__icontains=query)
            else:  # default to name search
                queryset = Hospital.objects.filter(name__icontains=query)
            
            # Apply limit
            queryset = queryset[:limit]
            
            # Serialize results
            serializer = HospitalListSerializer(queryset, many=True)
            
            return Response({
                'data': serializer.data,
                'summary': {
                    'query': query,
                    'search_type': search_type,
                    'total_results': queryset.count(),
                    'limit_applied': limit
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error searching hospitals: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )