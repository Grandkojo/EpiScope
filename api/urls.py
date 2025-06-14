from django.urls import path
from . import views

urlpatterns = [
    path('diseases/dashboard/', views.EpidemicDashboardView.as_view(), name='disease-dashboard'),
    path('diseases/years/', views.DiseaseYearsView.as_view(), name='disease-years'),
    # path('diseases/years/only/', views.DiseaseYearsOnlyView.as_view(), name='disease-years-only'),

    path('diseases/all/', views.DiseaseAllView.as_view(), name='disease-all'),
]
