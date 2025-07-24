import json
import os
from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
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

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

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
    
    def get(self, request):
        year = request.query_params.get('year', 2025)
        previous_year = request.query_params.get('prev_year', None)
        disease_name = request.query_params.get('disease_name', None)
        region = request.query_params.get('region', None)
        return Response(get_dashboard_counts(int(year), previous_year, disease_name, region))
    
class DiseaseYearsView(APIView):
    serializer_class = DiseaseYearSerializer
    permission_classes = [DiseaseManagementPermission]
    
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
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        result = analytics_service.get_principal_diagnoses(disease)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsAdditionalDiagnosesView(APIView):
    """Get top additional diagnoses with counts"""
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        result = analytics_service.get_additional_diagnoses(disease)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsNHIAStatusView(APIView):
    """Get NHIA status distribution with disease_name, year, and locality filters"""
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease_name = request.query_params.get('disease_name', None)
        year = request.query_params.get('year', None)
        locality = request.query_params.get('locality', None)
        if not disease_name:
            return Response({'error': 'disease_name is required as a query parameter.'}, status=400)
        try:
            year = int(year) if year is not None else None
        except ValueError:
            return Response({'error': 'year must be an integer.'}, status=400)
        result = analytics_service.get_nhia_status_filtered(disease_name, year, locality)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsPregnancyStatusView(APIView):
    """Get pregnancy status distribution with disease_name, year, and locality filters"""
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease_name = request.query_params.get('disease_name', None)
        year = request.query_params.get('year', None)
        locality = request.query_params.get('locality', None)
        if not disease_name:
            return Response({'error': 'disease_name is required as a query parameter.'}, status=400)
        try:
            year = int(year) if year is not None else None
        except ValueError:
            return Response({'error': 'year must be an integer.'}, status=400)
        result = analytics_service.get_pregnancy_status_filtered(disease_name, year, locality)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsHotspotsView(APIView):
    """Get disease hotspots by locality"""
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        result = analytics_service.get_hotspots_by_locality(disease)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsDiseaseComparisonView(APIView):
    """Compare two diseases"""
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease1 = request.query_params.get('disease1', 'diabetes')
        disease2 = request.query_params.get('disease2', 'malaria')
        result = analytics_service.get_disease_comparison(disease1, disease2)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsTrendsView(APIView):
    """Get trends by locality over time"""
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease = request.query_params.get('disease', 'diabetes')
        time_range = request.query_params.get('time_range', '3M')
        result = analytics_service.get_trends_by_locality(disease, time_range)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

# Time Series Forecasting Views

class TimeSeriesForecastView(APIView):
    """Get time series forecast for disease data"""
    permission_classes = [DashboardPermission]
    
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
    permission_classes = [DashboardPermission]
    
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
    permission_classes = [DashboardPermission]
    
    def get(self, request):
        disease = request.query_params.get('disease', 'diabetes')
        forecast_months = int(request.query_params.get('months', 12))
        
        result = forecasting_service.get_seasonal_forecast(disease, forecast_months)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class TimeSeriesAccuracyMetricsView(APIView):
    """Get forecast accuracy metrics"""
    permission_classes = [DashboardPermission]
    
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
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        insight_type = request.query_params.get('type', 'general')
        
        result = ai_insights_service.get_ai_insights(disease, insight_type)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AIQAView(APIView):
    """Get AI-powered Q&A response"""
    permission_classes = [DashboardPermission]
    
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
    
    def get(self, request):
        disease = request.query_params.get('disease', None)
        
        result = ai_insights_service.get_anomaly_detection(disease)
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response(result['data'])

class AnalyticsLocalitiesView(APIView):
    """Get all unique localities from HospitalHealthData"""
    permission_classes = [DashboardPermission]

    def get(self, request):
        result = analytics_service.get_all_localities()
        if not result['success']:
            return Response({'error': result['error']}, status=500)
        return Response({'localities': result['localities']})

class DiseaseTrendsAPIView(APIView):
    def get(self, request):
        disease_trends = DiseaseTrends.objects.all()
        serializer = DiseaseTrendsSerializer(disease_trends, many=True)
        return Response(serializer.data)

class PredictDiseaseView(APIView):
    """Predict disease for a patient, optionally using Gemini for recommendations, and log the request/result."""
    permission_classes = [DashboardPermission]
    monitor = DiseaseMonitor()  # Use a class-level instance for efficiency

    def post(self, request):
        data = request.data
        # Required fields
        age = data.get('age')
        sex = data.get('sex')
        pregnant_patient = data.get('pregnant_patient')
        nhia_patient = data.get('nhia_patient')
        orgname = data.get('orgname')
        address_locality = data.get('address_locality')
        disease_type = data.get('disease_type')
        symptoms = data.get('symptoms', [])
        gemini_enabled = data.get('gemini_enabled', False)

        # Validate required fields
        missing = [f for f in ['age', 'sex', 'pregnant_patient', 'nhia_patient', 'orgname', 'address_locality', 'disease_type'] if data.get(f) is None]
        if missing:
            return Response({'error': f'Missing required fields: {", ".join(missing)}'}, status=400)

        # Build DataFrame for prediction
        input_df = pd.DataFrame([{**data, 'symptoms': symptoms}])
        # Load model and encoders for the disease if not already loaded
        model_dir = os.path.join('models', disease_type.lower())
        if disease_type.lower() not in self.monitor.models:
            self.monitor.load_models(path=model_dir)
        # Preprocess and predict
        X, _, _ = self.monitor.preprocess_data(input_df, disease_type)
        model = self.monitor.models[disease_type.lower()]
        prediction = model.predict(X)[0]
        probability = float(model.predict_proba(X)[0][1])  # Probability of positive class

        # Gemini recommendation (optional)
        gemini_recommendation = None
        if gemini_enabled:
            gemini_recommendation = ai_insights_service.get_ai_insights(disease_type, 'recommendation', input_data=data, prediction=prediction)

        # Log the prediction
        log = PredictionLog(
            orgname=orgname,
            address_locality=address_locality,
            age=age,
            sex=sex,
            pregnant_patient=pregnant_patient,
            nhia_patient=nhia_patient,
            disease_type=disease_type,
            prediction=prediction,
            probability=probability,
            gemini_enabled=gemini_enabled,
            gemini_recommendation=gemini_recommendation or ''
        )
        log.set_symptoms(symptoms)
        log.save()

        return Response({
            'prediction': prediction,
            'probability': probability,
            'gemini_enabled': gemini_enabled,
            'gemini_recommendation': gemini_recommendation
        })