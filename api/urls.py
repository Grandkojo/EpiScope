from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from . import views
from .views import DiseaseTrendsAPIView

urlpatterns = [
    path('diseases/dashboard/', views.EpidemicDashboardView.as_view(), name='disease-dashboard'),
    path('diseases/years/', views.DiseaseYearsView.as_view(), name='disease-years'),
    # path('diseases/years/only/', views.DiseaseYearsOnlyView.as_view(), name='disease-years-only'),

    path('diseases/all/', views.DiseaseAllView.as_view(), name='disease-all'),
    path('diseases/region-rates/', views.RegionalDiseaseRatesView.as_view(), name='regional-disease-rates'),
    path('diseases/region-rates/statistics/', views.RegionalDiseaseRatesStatisticsView.as_view(), name='regional-disease-rates-statistics'),
    path('diseases/region-rates/filters/', views.RegionalDiseaseRatesFiltersView.as_view(), name='regional-disease-rates-filters'),
    path('auth/user/register/', views.UserRegisterView.as_view(), name='register'),
    path('user/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('auth/user/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/user/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    # path('auth/google/', views.GoogleLoginView.as_view(), name='google-login'),
    path('hotspots/national/', views.NationalHotspotsView.as_view(), name='national-hotspots'),
    path('hotspots/national/filters/', views.NationalHotspotsFiltersView.as_view(), name='national-hotspots-filters'),
    path('regions/all/', views.AllRegionsView.as_view(), name='all-regions'),
    path('disease-trends/', DiseaseTrendsAPIView.as_view(), name='disease_trends'),
    
    # Analytics Dashboard APIs
    path('analytics/overview/', views.AnalyticsDashboardOverviewView.as_view(), name='analytics-overview'),
    path('analytics/principal-diagnoses/', views.AnalyticsPrincipalDiagnosesView.as_view(), name='analytics-principal-diagnoses'),
    path('analytics/additional-diagnoses/', views.AnalyticsAdditionalDiagnosesView.as_view(), name='analytics-additional-diagnoses'),
    path('analytics/nhia-status/', views.AnalyticsNHIAStatusView.as_view(), name='analytics-nhia-status'),
    path('analytics/pregnancy-status/', views.AnalyticsPregnancyStatusView.as_view(), name='analytics-pregnancy-status'),
    path('analytics/hotspots/', views.AnalyticsHotspotsView.as_view(), name='analytics-hotspots'),
    path('analytics/disease-comparison/', views.AnalyticsDiseaseComparisonView.as_view(), name='analytics-disease-comparison'),
    path('analytics/trends/', views.AnalyticsTrendsView.as_view(), name='analytics-trends'),
    path('analytics/localities/', views.AnalyticsLocalitiesView.as_view(), name='analytics-localities'),
    
    # Time Series Forecasting APIs
    path('forecast/', views.TimeSeriesForecastView.as_view(), name='time-series-forecast'),
    path('forecast/multi-locality/', views.TimeSeriesMultiLocalityForecastView.as_view(), name='time-series-multi-locality-forecast'),
    path('forecast/seasonal/', views.TimeSeriesSeasonalForecastView.as_view(), name='time-series-seasonal-forecast'),
    path('forecast/accuracy/', views.TimeSeriesAccuracyMetricsView.as_view(), name='time-series-accuracy-metrics'),
    
    # AI Insights APIs
    path('ai/insights/', views.AIInsightsView.as_view(), name='ai-insights'),
    path('ai/qa/', views.AIQAView.as_view(), name='ai-qa'),
    path('ai/anomalies/', views.AIAnomalyDetectionView.as_view(), name='ai-anomaly-detection'),
    path('ai/predict-disease/', views.PredictDiseaseView.as_view(), name='ai-predict-disease'),
]



