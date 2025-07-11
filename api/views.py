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
    permission_classes = [IsAuthenticated]

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
    def get(self, request):
        year = request.query_params.get('year', 2025)
        previous_year = request.query_params.get('prev_year', None)
        disease_name = request.query_params.get('disease_name', None)
        region = request.query_params.get('region', None)
        return Response(get_dashboard_counts(int(year), previous_year, disease_name, region))
    
class DiseaseYearsView(APIView):
    serializer_class = DiseaseYearSerializer
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
    def get(self, request):
        disease_all = get_disease_all()
        serializer = self.serializer_class(disease_all, many=True)
        return Response(serializer.data)

class NationalHotspotsView(APIView):
    serializer_class = NationalHotspotsSerializer
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