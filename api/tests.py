from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import User
from .serializers import UserRegisterSerializer, UserProfileSerializer, DiseaseSerializer, DiseaseYearSerializer
from disease_monitor.models import Disease, DiseaseYear
from .services.dashboard_data import get_dashboard_counts, get_disease_data, get_disease_years, get_disease_all
from unittest.mock import patch

class UserRegisterViewTest(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '1234567890',
            'address': '123 Main St'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

class UserProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', phone='1234567890', address='123 Main St')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_profile(self):
        url = reverse('user-profile')
        data = {'username': 'updateduser', 'email': 'updated@example.com', 'phone': '0987654321', 'address': '456 Main St'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

class EpidemicDashboardViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', phone='1234567890', address='123 Main St')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('api.views.get_dashboard_counts')
    def test_dashboard_view(self, mock_dashboard_counts):
        mock_dashboard_counts.return_value = {'diabetes': {'total_count': 10, 'title': 'Diabetes Cases'}}
        url = reverse('disease-dashboard')
        response = self.client.get(url, {'year': 2025, 'disease_name': 'Diabetes'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Diabetes Cases', str(response.data))

class DiseaseYearsViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', phone='1234567890', address='123 Main St')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('api.services.dashboard_data.get_disease_years')
    def test_disease_years_view(self, mock_get_years):
        disease = Disease.objects.create(disease_name='Diabetes', description='desc')
        disease_year = DiseaseYear.objects.create(periodname='2025', disease_id=disease, hot_spots='Yes', summary_data='No', case_count_summary='Yes') 
        mock_get_years.return_value = [disease_year]
        url = reverse('disease-years')
        response = self.client.get(url, {'disease_id': disease.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DiseaseAllViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123', phone='1234567890', address='123 Main St')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('api.services.dashboard_data.get_disease_all')
    def test_disease_all_view(self, mock_get_all):
        mock_get_all.return_value = [Disease(disease_name='Diabetes', description='desc')]
        url = reverse('disease-all')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserSerializerTest(APITestCase):
    def test_user_register_serializer(self):
        data = {'username': 'user', 'email': 'user@example.com', 'password': 'pass', 'phone': '1234567890', 'address': 'addr'}
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_user_profile_serializer(self):
        user = User.objects.create_user(username='user', email='user@example.com', password='pass', phone='1234567890', address='addr')
        serializer = UserProfileSerializer(user)
        self.assertEqual(serializer.data['username'], 'user')

class DiseaseSerializerTest(APITestCase):
    def test_disease_serializer(self):
        disease = Disease.objects.create(disease_name='Diabetes', description='desc')
        serializer = DiseaseSerializer(disease)
        self.assertEqual(serializer.data['disease_name'], 'Diabetes')

class DiseaseYearSerializerTest(APITestCase):
    def test_disease_year_serializer(self):
        disease = Disease.objects.create(disease_name='Diabetes', description='desc')
        year = DiseaseYear.objects.create(periodname='2025', disease_id=disease, hot_spots='Yes', summary_data='No', case_count_summary='Yes')
        serializer = DiseaseYearSerializer(year)
        self.assertEqual(serializer.data['periodname'], '2025')

class DashboardServiceTest(APITestCase):
    @patch('api.services.dashboard_data.DiabetesData')
    @patch('api.services.dashboard_data.Disease')
    def test_get_dashboard_counts_invalid_disease(self, mock_disease, mock_diabetes):
        mock_disease.objects.filter.return_value.values_list.return_value.distinct.return_value.first.return_value = None
        result = get_dashboard_counts(year=2025, disease_name='Invalid')
        self.assertIn('error', result)

    @patch('api.services.dashboard_data.DiabetesData')
    @patch('api.services.dashboard_data.Disease')
    def test_get_dashboard_counts_valid(self, mock_disease, mock_diabetes):
        mock_disease.objects.filter.return_value.values_list.return_value.distinct.return_value.first.return_value = 1
        mock_diabetes.objects.filter.return_value.values_list.return_value.distinct.return_value.first.return_value = 2025
        result = get_dashboard_counts(year=2025, disease_name='Diabetes')
        self.assertTrue(isinstance(result, dict))
