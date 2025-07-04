from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from . import views

urlpatterns = [
    path('diseases/dashboard/', views.EpidemicDashboardView.as_view(), name='disease-dashboard'),
    path('diseases/years/', views.DiseaseYearsView.as_view(), name='disease-years'),
    # path('diseases/years/only/', views.DiseaseYearsOnlyView.as_view(), name='disease-years-only'),

    path('diseases/all/', views.DiseaseAllView.as_view(), name='disease-all'),
    path('auth/user/register/', views.UserRegisterView.as_view(), name='register'),
    path('user/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('auth/user/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/user/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    # path('auth/google/', views.GoogleLoginView.as_view(), name='google-login'),
    path('hotspots/national/', views.NationalHotspotsView.as_view(), name='national-hotspots'),
    path('hotspots/national/filters/', views.NationalHotspotsFiltersView.as_view(), name='national-hotspots-filters'),
    path('regions/all/', views.AllRegionsView.as_view(), name='all-regions'),
]


