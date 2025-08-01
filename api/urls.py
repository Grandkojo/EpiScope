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
    path('auth/user/login/', views.CustomLoginView.as_view(), name='token_obtain_pair'),  # Custom view without rate limiting
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
    path('analytics/orgnames/', views.AnalyticsOrgnamesView.as_view(), name='analytics-orgnames'),
    path('analytics/age-distribution/', views.AnalyticsAgeDistributionView.as_view(), name='analytics-age-distribution'),
    path('analytics/sex-distribution/', views.AnalyticsSexDistributionView.as_view(), name='analytics-sex-distribution'),
    
    # Time Series Forecasting APIs
    path('forecast/', views.TimeSeriesForecastView.as_view(), name='time-series-forecast'),
    path('forecast/multi-locality/', views.TimeSeriesMultiLocalityForecastView.as_view(), name='time-series-multi-locality-forecast'),
    path('forecast/seasonal/', views.TimeSeriesSeasonalForecastView.as_view(), name='time-series-seasonal-forecast'),
    path('forecast/accuracy/', views.TimeSeriesAccuracyMetricsView.as_view(), name='time-series-accuracy-metrics'),
    
    # AI Insights APIs
    path('ai/insights/', views.AIInsightsView.as_view(), name='ai-insights'),
    path('ai/structured-analytics/', views.AIStructuredAnalyticsView.as_view(), name='ai-structured-analytics'),
    path('ai/qa/', views.AIQAView.as_view(), name='ai-qa'),
    path('ai/anomalies/', views.AIAnomalyDetectionView.as_view(), name='ai-anomaly-detection'),
    path('ai/predict-disease/', views.PredictDiseaseView.as_view(), name='ai-predict-disease'),
    
    # Hospital Localities APIs
    path('hospital-localities/', views.HospitalLocalitiesView.as_view(), name='hospital-localities'),
    path('hospital-localities/stats/', views.HospitalLocalitiesStatsView.as_view(), name='hospital-localities-stats'),
    path('hospital-localities/search/', views.HospitalLocalitiesSearchView.as_view(), name='hospital-localities-search'),
    path('hospital-localities/by-hospital/', views.HospitalLocalitiesByHospitalView.as_view(), name='hospital-localities-by-hospital'),
    
    # Hospital APIs
    path('hospitals/', views.HospitalView.as_view(), name='hospitals'),
    path('hospitals/stats/', views.HospitalStatsView.as_view(), name='hospitals-stats'),
    path('hospitals/search/', views.HospitalSearchView.as_view(), name='hospitals-search'),
    path('hospitals/<int:hospital_id>/', views.HospitalDetailView.as_view(), name='hospital-detail'),
    path('hospitals/slug/<str:slug>/', views.HospitalDetailView.as_view(), name='hospital-detail-by-slug'),
    
    # Rate Limiting Test APIs
    path('test/rate-limit/', views.TestRateLimitView.as_view(), name='test-rate-limit'),
    path('test/rate-limit-info/', views.RateLimitInfoView.as_view(), name='rate-limit-info'),
    # Cache Management
    path('caches/status/', views.CacheStatusView.as_view(), name='cache-status'),
    path('caches/manage/', views.CacheManagementView.as_view(), name='cache-management'),
]



