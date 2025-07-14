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

class DiseaseTrendsAPIView(APIView):
    def get(self, request):
        disease_name = request.query_params.get('disease')
        year = request.query_params.get('year')
        if not disease_name or not year:
            return Response({'error': 'disease and year are required query parameters.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            disease = Disease.objects.get(disease_name__iexact=disease_name)
        except Disease.DoesNotExist:
            return Response({'error': 'Disease not found.'}, status=status.HTTP_404_NOT_FOUND)
        trends = DiseaseTrends.objects.filter(disease=disease, year=year).order_by('month')
        serializer = DiseaseTrendsSerializer(trends, many=True)
        return Response(serializer.data)