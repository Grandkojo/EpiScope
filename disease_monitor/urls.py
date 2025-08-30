from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'predictions', views.PredictionHistoryViewSet, basename='prediction')
router.register(r'reinforcement-learning', views.ReinforcementLearningViewSet, basename='reinforcement-learning')
router.register(r'training-sessions', views.ModelTrainingSessionViewSet, basename='training-session')
router.register(r'feedback', views.PredictionFeedbackViewSet, basename='feedback')

# Add article URLs to the main URL patterns
urlpatterns = [
    # Include router URLs (remove the 'api/' prefix since it's already in the main URLs)
    path('', include(router.urls)),
    
    # Individual API endpoints (remove the 'api/' prefix)
    path('create-prediction/', views.CreatePredictionView.as_view(), name='create-prediction'),
    path('prediction-dashboard/', views.prediction_dashboard, name='prediction-dashboard'),
    path('submit-reinforcement-data/', views.submit_reinforcement_data, name='submit-reinforcement-data'),
]
