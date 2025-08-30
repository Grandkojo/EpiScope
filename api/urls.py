from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from . import views
from .views import DiseaseTrendsAPIView
from disease_monitor import views as disease_monitor_views

urlpatterns = [
    
    
    # Existing API routes
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
    path('analytics/ai-insights/', views.AnalyticsAIInsightsView.as_view(), name='analytics-ai-insights'),
    
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
    path('ai/predictions/', disease_monitor_views.PredictionHistoryViewSet.as_view({'get': 'list'}), name='predictions-list'),
    path('ai/predictions/latest/', disease_monitor_views.PredictionHistoryViewSet.as_view({'get': 'latest_predictions'}), name='latest-predictions'),
    path('ai/predictions/all/', disease_monitor_views.PredictionHistoryViewSet.as_view({'get': 'all_predictions'}), name='all-predictions'),
    path('ai/predictions/user/', disease_monitor_views.PredictionHistoryViewSet.as_view({'get': 'user_predictions'}), name='user-predictions'),
    path('ai/predictions/<int:pk>/update-status/', disease_monitor_views.PredictionHistoryViewSet.as_view({'post': 'update_status'}), name='update-prediction-status'),
    path('ai/predictions/<int:pk>/add-feedback/', disease_monitor_views.PredictionHistoryViewSet.as_view({'post': 'add_feedback'}), name='add-prediction-feedback'),
    path('ai/predictions/<int:pk>/details/', disease_monitor_views.PredictionHistoryViewSet.as_view({'get': 'details'}), name='prediction-details'),
    path('ai/predictions/trigger-reinforcement-learning/', disease_monitor_views.PredictionHistoryViewSet.as_view({'post': 'trigger_reinforcement_learning'}), name='trigger-reinforcement-learning'),
    # Admin routes for all users
    path('ai/predictions/admin/all-users/', disease_monitor_views.PredictionHistoryViewSet.as_view({'get': 'admin_all_users_predictions'}), name='admin-all-users-predictions'),
    path('ai/predictions/admin/latest-all-users/', disease_monitor_views.PredictionHistoryViewSet.as_view({'get': 'admin_latest_all_users'}), name='admin-latest-all-users'),
    # Prediction History API endpoints
    
    
    # Reinforcement Learning endpoints
    path('ai/reinforcement-learning/', disease_monitor_views.ReinforcementLearningViewSet.as_view({'get': 'list'}), name='reinforcement-learning-list'),
    path('ai/reinforcement-learning/statistics/', disease_monitor_views.ReinforcementLearningViewSet.as_view({'get': 'statistics'}), name='reinforcement-learning-stats'),
    path('ai/reinforcement-learning/aggregate/', disease_monitor_views.ReinforcementLearningViewSet.as_view({'post': 'aggregate_data'}), name='reinforcement-learning-aggregate'),
    
    # Training Sessions endpoints
    path('ai/training-sessions/', disease_monitor_views.ModelTrainingSessionViewSet.as_view({'get': 'list'}), name='training-sessions-list'),
    path('ai/training-sessions/create/', disease_monitor_views.ModelTrainingSessionViewSet.as_view({'post': 'create_session'}), name='create-training-session'),
    path('ai/training-sessions/<int:pk>/update-status/', disease_monitor_views.ModelTrainingSessionViewSet.as_view({'post': 'update_status'}), name='update-training-session-status'),
    
    # Feedback endpoints
    path('feedback/', disease_monitor_views.PredictionFeedbackViewSet.as_view({'get': 'list'}), name='feedback-list'),
    path('feedback/prediction/', disease_monitor_views.PredictionFeedbackViewSet.as_view({'get': 'prediction_feedbacks'}), name='prediction-feedbacks'),
    
    # Prediction Analysis and Reinforcement Data
    path('ai/prediction-analysis/', disease_monitor_views.prediction_analysis, name='prediction-analysis'),
    path('ai/submit-reinforcement-data/', disease_monitor_views.submit_reinforcement_data, name='submit-reinforcement-data'),
    
    # Article and Content Management APIs
    path('articles/tags/', disease_monitor_views.ArticleTagViewSet.as_view(), name='article-tags'),
    path('articles/tags/<int:id>/', disease_monitor_views.ArticleTagDetailView.as_view(), name='article-tag-detail'),
    path('articles/', disease_monitor_views.ArticleViewSet.as_view(), name='articles'),
    path('articles/<slug:slug>/', disease_monitor_views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<int:article_id>/comments/', disease_monitor_views.ArticleCommentViewSet.as_view(), name='article-comments'),
    path('articles/<int:article_id>/like/', disease_monitor_views.ArticleLikeView.as_view(), name='article-like'),
    path('articles/<int:article_id>/bookmark/', disease_monitor_views.ArticleBookmarkView.as_view(), name='article-bookmark'),
    path('articles/featured/', disease_monitor_views.FeaturedArticlesView.as_view(), name='featured-articles'),
    path('articles/search/', disease_monitor_views.ArticleSearchView.as_view(), name='article-search'),
    path('articles/bookmarks/', disease_monitor_views.UserBookmarksView.as_view(), name='user-bookmarks'),
    
    # Research Papers APIs
    path('research-papers/', disease_monitor_views.ResearchPaperViewSet.as_view(), name='research-papers'),
    path('research-papers/<int:id>/', disease_monitor_views.ResearchPaperDetailView.as_view(), name='research-paper-detail'),
    
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
    
    # Google Trends APIs
    path('google-trends/', views.GoogleTrendsDiseaseViewSet.as_view(), name='google-trends-diseases'),
    path('google-trends/summary/', views.GoogleTrendsSummaryView.as_view(), name='google-trends-summary'),
    path('google-trends/cache-status/', views.GoogleTrendsCacheStatusView.as_view(), name='google-trends-cache-status'),
    path('google-trends/clear-cache/', views.GoogleTrendsClearCacheView.as_view(), name='google-trends-clear-cache'),
    path('google-trends/<str:disease_name>/', views.GoogleTrendsDiseaseDetailViewSet.as_view(), name='google-trends-disease-detail'),
    path('google-trends/<str:disease_name>/summary/', views.GoogleTrendsDiseaseSummaryView.as_view(), name='google-trends-disease-summary'),
    path('google-trends/<str:disease_name>/interest-over-time/', views.GoogleTrendsInterestOverTimeView.as_view(), name='google-trends-interest-over-time'),
    path('google-trends/<str:disease_name>/related-queries/', views.GoogleTrendsRelatedQueriesView.as_view(), name='google-trends-related-queries'),
    path('google-trends/<str:disease_name>/related-topics/', views.GoogleTrendsRelatedTopicsView.as_view(), name='google-trends-related-topics'),
    path('google-trends/<str:disease_name>/interest-by-region/', views.GoogleTrendsInterestByRegionView.as_view(), name='google-trends-interest-by-region'),
]



