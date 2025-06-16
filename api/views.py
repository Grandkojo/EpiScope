from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .services.dashboard_data import get_dashboard_counts, get_disease_years, get_disease_all
from .serializers import DiseaseSerializer, DiseaseYearSerializer
# Create your views here.

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