from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid
import json
import re

# Create your models here.

class RegionPopulation(models.Model):
    region = models.CharField(max_length=100)
    periodname = models.CharField(max_length=100)
    population = models.IntegerField()
    
    class Meta:
        db_table = 'region_population'
        verbose_name = 'Region Population'
        verbose_name_plural = 'Region Populations'
        unique_together = ['region', 'periodname']
        ordering = ['-periodname', 'region']

    def __str__(self):
        return f"{self.region} - {self.periodname} ({self.population:,})"

class DiabetesData(models.Model):
    periodname = models.CharField(max_length=100, primary_key=True)
    diabetes_mellitus = models.IntegerField(db_column='Diabetes Mellitus')
    diabetes_mellitus_female = models.IntegerField(db_column='Diabetes Mellitus +AC0- Female')
    diabetes_mellitus_male = models.IntegerField(db_column='Diabetes Mellitus +AC0- Male')
    diabetes_mellitus_deaths = models.IntegerField(db_column='Diabetes mellitus deaths')
    diabetes_mellitus_lab_confirmed_cases = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases')

    class Meta:
        db_table = "diabetes"
        managed = False
        verbose_name = "Diabetes Data"
        verbose_name_plural = "Diabetes Data"
        ordering = ['-periodname']

    def __str__(self):
        return f"Diabetes Data for {self.periodname}"

class MeningitisData(models.Model):
    periodname = models.CharField(max_length=100, primary_key=True)
    meningitis_cases = models.IntegerField(db_column='Meningitis')
    meningitis_cases_female = models.IntegerField(db_column="Meningitis - Female")
    meningitis_cases_male = models.IntegerField(db_column="Meningitis - Male")
    meningitis_case_fatality_rate = models.IntegerField(db_column="Meningitis case fatality rate")
    meningococcal_meningitis_cases_weekly = models.IntegerField(db_column="Meningococcal Meningitis cases (weekly)")
    meningococcal_meningitis_deaths_weekly = models.IntegerField(db_column="Meningococcal Meningitis deaths (weekly)")
    meningococcal_meningitis_lab_confirmed_cases = models.IntegerField(db_column="Meningococcal Meningitis lab confirmed cases")
    meningococcal_meningitis_lab_confirmed_cases_weekly = models.IntegerField(db_column="Meningococcal Meningitis lab confirmed cases (weekly)")
    meningococcal_meningitis_cases_cds = models.IntegerField(db_column="Meningococcal meningitis cases (CDS)")
    meningococcal_meningitis_deaths = models.IntegerField(db_column="Meningococcal meningitis deaths")

    class Meta:
        db_table = 'meningitis'
        verbose_name = 'Meningitis Data'
        verbose_name_plural = 'Meningitis Data'
        managed = False
        ordering = ['-periodname']

    def __str__(self):
        return f"Meningitis Data for {self.periodname}"

class CholeraData(models.Model):
    periodname = models.CharField(max_length=100, primary_key=True)
    cholera_female = models.IntegerField(db_column="Cholera - Female", null=True)
    cholera_male = models.IntegerField(db_column="Cholera - Male", null=True)
    cholera_deaths_cds = models.IntegerField(db_column="Cholera Deaths (CDS)", null=True)
    cholera_cases_cds = models.IntegerField(db_column="Cholera cases (CDS)", null=True)
    cholera_cases_weekly = models.IntegerField(db_column="Cholera cases (weekly)", null=True)
    cholera_deaths_weekly = models.IntegerField(db_column="Cholera deaths (weekly)", null=True)
    cholera_lab_confirmed = models.IntegerField(db_column="Cholera lab confirmed cases", null=True)
    cholera_lab_confirmed_weekly = models.IntegerField(db_column="Cholera lab confirmed cases (weekly)", null=True)
    cholera_waho_cases = models.IntegerField(db_column="WAHO/OOAS Cholera cases", null=True)

    class Meta:
        db_table = 'cholera'
        verbose_name = 'Cholera Data'
        verbose_name_plural = 'Cholera Data'
        managed = False
        ordering = ['-periodname']

    def __str__(self):
        return f"Cholera Data - {self.periodname}"

class NationalHotspots(models.Model):
    organisationunitname = models.CharField(db_column='organisationunitname', max_length=100, primary_key=True)
    cholera_lab_confirmed_cases_2020 = models.IntegerField(db_column='Cholera lab confirmed cases 2020', null=True)
    cholera_lab_confirmed_cases_2021 = models.IntegerField(db_column='Cholera lab confirmed cases 2021', null=True)
    cholera_lab_confirmed_cases_2022 = models.IntegerField(db_column='Cholera lab confirmed cases 2022', null=True)
    cholera_lab_confirmed_cases_2023 = models.IntegerField(db_column='Cholera lab confirmed cases 2023', null=True)
    cholera_lab_confirmed_cases_2024 = models.IntegerField(db_column='Cholera lab confirmed cases 2024', null=True)
    cholera_lab_confirmed_cases_2025 = models.IntegerField(db_column='Cholera lab confirmed cases 2025', null=True)
    diabetes_mellitus_lab_confirmed_cases_2020 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2020', null=True)
    diabetes_mellitus_lab_confirmed_cases_2021 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2021', null=True)
    diabetes_mellitus_lab_confirmed_cases_2022 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2022', null=True)
    diabetes_mellitus_lab_confirmed_cases_2023 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2023', null=True)
    diabetes_mellitus_lab_confirmed_cases_2024 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2024', null=True)
    diabetes_mellitus_lab_confirmed_cases_2025 = models.IntegerField(db_column='Diabetes mellitus lab confirmed cases 2025', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2020 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2020', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2021 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2021', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2022 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2022', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2023 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2023', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2024 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2024', null=True)
    meningococcal_meningitis_lab_confirmed_cases_2025 = models.IntegerField(db_column='Meningococcal Meningitis lab confirmed cases 2025', null=True)

    class Meta:
        managed = False
        db_table = 'national_hotspots'
        verbose_name = 'National Hotspots'
        verbose_name_plural = 'National Hotspots'

    def __str__(self):
        return f"National Hotspots - {self.organisationunitname}"

class Disease(models.Model):
    disease_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"Disease {self.disease_name}"

class DiseaseYear(models.Model):
    periodname = models.CharField(max_length=100)
    disease_id = models.ForeignKey(Disease, on_delete=models.CASCADE)
    hot_spots = models.CharField(max_length=3)
    summary_data = models.CharField(max_length=3)
    case_count_summary = models.CharField(max_length=3)

    class Meta:
        verbose_name = "Disease Year"
        verbose_name_plural = "Disease Years"
        ordering = ['-periodname']

    def __str__(self):
        return f"Disease Year {self.periodname}"

class DiseaseTrends(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='trends')
    year = models.IntegerField()
    month = models.IntegerField()  # 1=Jan, 12=Dec
    trend_value = models.FloatField()

    class Meta:
        unique_together = ('disease', 'year', 'month')
        verbose_name = 'Disease Trend'
        verbose_name_plural = 'Disease Trends'
        ordering = ['disease', 'year', 'month']

    def __str__(self):
        return f"{self.disease.disease_name} - {self.year}-{self.month:02d}: {self.trend_value}"

class CommonSymptom(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='common_symptoms')
    symptom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    rank = models.PositiveIntegerField(default=1)  

    class Meta:
        unique_together = ('disease', 'symptom')
        ordering = ['disease', 'rank']

    def __str__(self):
        return f"{self.disease.disease_name}: {self.symptom} (#{self.rank})"


class HospitalHealthData(models.Model):
    orgname = models.CharField(max_length=100) 
    address_locality = models.CharField(max_length=255)
    age = models.IntegerField()
    sex = models.CharField(max_length=10) 
    principal_diagnosis_new = models.CharField(max_length=255)
    additional_diagnosis_new = models.CharField(max_length=255, blank=True, null=True)
    pregnant_patient = models.BooleanField()
    nhia_patient = models.BooleanField()
    month = models.DateField() 
    
    # New fields added for merged data
    data_source = models.CharField(max_length=20, default='legacy', blank=True, null=True)
    medicine_prescribed = models.TextField(blank=True, null=True)
    cost_of_treatment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    schedule_date = models.DateField(blank=True, null=True)
    locality_encoded = models.IntegerField(blank=True, null=True)


    class Meta:
        indexes = [
            models.Index(fields=['orgname', 'month']),
        ]
        verbose_name = 'Hospital Health Data'
        verbose_name_plural = 'Hospital Health Data'

class PredictionLog(models.Model):
    orgname = models.CharField(max_length=100)
    address_locality = models.CharField(max_length=255)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    pregnant_patient = models.BooleanField()
    nhia_patient = models.BooleanField()
    disease_type = models.CharField(max_length=50)
    symptoms = models.TextField()  # Store as JSON string
    prediction = models.CharField(max_length=100)
    probability = models.FloatField()
    gemini_enabled = models.BooleanField(default=False)
    gemini_recommendation = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_symptoms(self, symptoms_list):
        self.symptoms = json.dumps(symptoms_list)

    def get_symptoms(self):
        return json.loads(self.symptoms)

    def __str__(self):
        return f"{self.orgname} | {self.disease_type} | {self.prediction} | {self.timestamp}"

class HospitalLocalities(models.Model):
    """
    Model to store hospital-locality combinations for filtering
    """
    id = models.AutoField(primary_key=True)
    locality = models.CharField(max_length=255, help_text="Patient's residential area")
    orgname = models.CharField(max_length=255, help_text="Healthcare facility name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hospital_localities'
        verbose_name = 'Hospital Locality'
        verbose_name_plural = 'Hospital Localities'
        unique_together = ['locality', 'orgname']
        ordering = ['locality', 'orgname']
        indexes = [
            models.Index(fields=['locality']),
            models.Index(fields=['orgname']),
            models.Index(fields=['locality', 'orgname']),
        ]
    
    def __str__(self):
        return f"{self.locality} - {self.orgname}"
    
    @classmethod
    def get_localities_for_hospital(cls, orgname):
        """Get all localities for a specific hospital"""
        return cls.objects.filter(orgname__icontains=orgname).values_list('locality', flat=True).distinct()
    
    @classmethod
    def get_hospitals_for_locality(cls, locality):
        """Get all hospitals for a specific locality"""
        return cls.objects.filter(locality__icontains=locality).values_list('orgname', flat=True).distinct()
    
    @classmethod
    def get_all_localities(cls):
        """Get all unique localities"""
        return cls.objects.values_list('locality', flat=True).distinct().order_by('locality')
    
    @classmethod
    def get_all_hospitals(cls):
        """Get all unique hospitals"""
        return cls.objects.values_list('orgname', flat=True).distinct().order_by('orgname')
    
    @classmethod
    def search_localities(cls, query):
        """Search localities by partial match"""
        return cls.objects.filter(locality__icontains=query).values_list('locality', flat=True).distinct()
    
    @classmethod
    def search_hospitals(cls, query):
        """Search hospitals by partial match"""
        return cls.objects.filter(orgname__icontains=query).values_list('orgname', flat=True).distinct()

class PredictionHistory(models.Model):
    """
    Model to store prediction history tied to users with reinforcement learning data
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('corrected', 'Corrected'),
        ('discarded', 'Discarded'),
    ]
    
    # User relationship
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='predictions')
    
    # Prediction details
    prediction_id = models.CharField(max_length=50, unique=True, help_text="Unique identifier for this prediction")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Patient data
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    locality = models.CharField(max_length=255)
    schedule_date = models.DateField()
    pregnant_patient = models.BooleanField(default=False)
    nhia_patient = models.BooleanField(default=False)
    vertex_ai_enabled = models.BooleanField(default=False)
    
    # Disease and symptoms
    disease_type = models.CharField(max_length=50)
    symptoms_description = models.TextField()
    
    # Prediction results
    predicted_disease = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    actual_disease = models.CharField(max_length=100, blank=True, null=True, help_text="Actual disease diagnosed by doctor")
    
    # Reinforcement learning data
    medicine_prescribed = models.TextField(blank=True, null=True, help_text="Medicine prescribed by doctor")
    cost_of_treatment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cost of treatment in GHS")
    
    # Model learning feedback
    feedback_timestamp = models.DateTimeField(blank=True, null=True, help_text="When reinforcement data was submitted")
    model_learning_score = models.FloatField(blank=True, null=True, help_text="Score for model learning (0-1)")
    
    # Additional metadata
    hospital_name = models.CharField(max_length=255, blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    ai_insights = models.JSONField(blank=True, null=True, help_text="AI-generated insights for this prediction")
    
    class Meta:
        db_table = 'prediction_history'
        verbose_name = 'Prediction History'
        verbose_name_plural = 'Prediction Histories'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['status', 'timestamp']),
            models.Index(fields=['predicted_disease', 'status']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.predicted_disease} ({self.confidence_score:.1%}) - {self.status}"
    
    def save(self, *args, **kwargs):
        # Generate prediction ID if not provided
        if not self.prediction_id:
            import uuid
            self.prediction_id = f"pred_{uuid.uuid4().hex[:12]}"
        
        # Update feedback timestamp when reinforcement data is provided
        if self.medicine_prescribed and not self.feedback_timestamp:
            self.feedback_timestamp = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_learning_ready(self):
        """Check if this prediction has enough data for reinforcement learning"""
        return (
            self.status in ['confirmed', 'corrected'] and
            self.medicine_prescribed and
            self.cost_of_treatment is not None
        )
    
    @property
    def prediction_accuracy(self):
        """Calculate prediction accuracy based on status"""
        if self.status == 'confirmed':
            return 1.0
        elif self.status == 'corrected':
            return 0.0
        elif self.status == 'discarded':
            return None
        else:
            return None
    
    def calculate_learning_score(self):
        """Calculate a learning score for reinforcement learning"""
        if not self.is_learning_ready:
            return None
        
        # Base score from prediction accuracy
        accuracy_score = self.prediction_accuracy if self.prediction_accuracy is not None else 0.5
        
        # Confidence adjustment
        confidence_factor = min(self.confidence_score, 1.0)
        
        # Cost efficiency factor (lower cost = higher score, but with diminishing returns)
        cost_factor = 1.0 / (1.0 + (float(self.cost_of_treatment or 0) / 1000.0))
        
        # Calculate final learning score
        learning_score = (accuracy_score * 0.6 + confidence_factor * 0.3 + cost_factor * 0.1)
        
        return min(max(learning_score, 0.0), 1.0)
    
    def update_learning_score(self):
        """Update the model learning score"""
        self.model_learning_score = self.calculate_learning_score()
        self.save(update_fields=['model_learning_score'])


class ReinforcementLearningData(models.Model):
    """
    Model to store aggregated reinforcement learning data for model training
    """
    # Data aggregation period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Disease type
    disease_type = models.CharField(max_length=50)
    
    # Aggregated metrics
    total_predictions = models.IntegerField(default=0)
    confirmed_predictions = models.IntegerField(default=0)
    corrected_predictions = models.IntegerField(default=0)
    discarded_predictions = models.IntegerField(default=0)
    
    # Average metrics
    avg_confidence_score = models.FloatField(default=0.0)
    avg_learning_score = models.FloatField(default=0.0)
    avg_cost_of_treatment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Treatment patterns
    common_medicines = models.JSONField(default=list, help_text="List of commonly prescribed medicines")
    medicine_frequency = models.JSONField(default=dict, help_text="Frequency of each medicine")
    
    # Model performance metrics
    model_accuracy = models.FloatField(default=0.0)
    model_precision = models.FloatField(default=0.0)
    model_recall = models.FloatField(default=0.0)
    model_f1_score = models.FloatField(default=0.0)
    
    # Training metadata
    last_training_date = models.DateTimeField(blank=True, null=True)
    training_data_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'reinforcement_learning_data'
        verbose_name = 'Reinforcement Learning Data'
        verbose_name_plural = 'Reinforcement Learning Data'
        unique_together = ['period_start', 'period_end', 'disease_type']
        ordering = ['-period_end', 'disease_type']
        indexes = [
            models.Index(fields=['disease_type', 'period_end']),
            models.Index(fields=['model_accuracy']),
        ]
    
    def __str__(self):
        return f"{self.disease_type} - {self.period_start} to {self.period_end} (Accuracy: {self.model_accuracy:.2%})"
    
    @property
    def total_processed(self):
        """Total predictions that have been processed (confirmed + corrected + discarded)"""
        return self.confirmed_predictions + self.corrected_predictions + self.discarded_predictions
    
    @property
    def processing_rate(self):
        """Percentage of predictions that have been processed"""
        if self.total_predictions == 0:
            return 0.0
        return (self.total_processed / self.total_predictions) * 100
    
    @property
    def success_rate(self):
        """Percentage of confirmed predictions"""
        if self.total_processed == 0:
            return 0.0
        return (self.confirmed_predictions / self.total_processed) * 100


class ModelTrainingSession(models.Model):
    """
    Model to track model training sessions using reinforcement learning data
    """
    TRAINING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Session identification
    session_id = models.CharField(max_length=50, unique=True)
    session_name = models.CharField(max_length=255)
    
    # Training parameters
    disease_type = models.CharField(max_length=50)
    model_type = models.CharField(max_length=50, help_text="Type of model (LSTM, ARIMA, etc.)")
    training_parameters = models.JSONField(default=dict, help_text="Model training parameters")
    
    # Data used for training
    data_period_start = models.DateField()
    data_period_end = models.DateField()
    training_data_count = models.IntegerField(default=0)
    
    # Training status and results
    status = models.CharField(max_length=20, choices=TRAINING_STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    
    # Performance metrics
    training_accuracy = models.FloatField(blank=True, null=True)
    validation_accuracy = models.FloatField(blank=True, null=True)
    test_accuracy = models.FloatField(blank=True, null=True)
    
    # Model artifacts
    model_file_path = models.CharField(max_length=500, blank=True, null=True)
    scaler_file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Training logs
    training_logs = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # User who initiated training
    initiated_by = models.ForeignKey('api.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'model_training_sessions'
        verbose_name = 'Model Training Session'
        verbose_name_plural = 'Model Training Sessions'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['disease_type', 'status']),
            models.Index(fields=['start_time']),
            models.Index(fields=['model_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.session_name} - {self.disease_type} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Generate session ID if not provided
        if not self.session_id:
            import uuid
            self.session_id = f"train_{uuid.uuid4().hex[:12]}"
        
        super().save(*args, **kwargs)
    
    @property
    def duration(self):
        """Calculate training duration"""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def is_completed(self):
        """Check if training is completed"""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """Check if training failed"""
        return self.status == 'failed'


class PredictionFeedback(models.Model):
    """
    Model to store detailed feedback for predictions
    """
    FEEDBACK_TYPE_CHOICES = [
        ('accuracy', 'Accuracy Feedback'),
        ('treatment', 'Treatment Feedback'),
        ('cost', 'Cost Feedback'),
        ('general', 'General Feedback'),
    ]
    
    # Link to prediction
    prediction = models.ForeignKey(PredictionHistory, on_delete=models.CASCADE, related_name='feedbacks')
    
    # Feedback details
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    feedback_text = models.TextField()
    rating = models.IntegerField(blank=True, null=True, help_text="Rating from 1-5")
    
    # Feedback metadata
    provided_by = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='provided_feedbacks')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    doctor_notes = models.TextField(blank=True, null=True)
    patient_outcome = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'prediction_feedback'
        verbose_name = 'Prediction Feedback'
        verbose_name_plural = 'Prediction Feedbacks'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['prediction', 'feedback_type']),
            models.Index(fields=['provided_by', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Feedback on {self.prediction.prediction_id} - {self.feedback_type}"


class GoogleTrendsCache(models.Model):
    """
    Model to cache Google Trends data to avoid rate limiting
    """
    CACHE_STATUS_CHOICES = [
        ('fresh', 'Fresh'),
        ('stale', 'Stale'),
        ('expired', 'Expired'),
    ]
    
    # Cache identification
    cache_key = models.CharField(max_length=255, unique=True, help_text="Unique cache key for this request")
    disease_name = models.CharField(max_length=100, help_text="Disease name (diabetes, malaria, meningitis, cholera)")
    data_type = models.CharField(max_length=50, help_text="Type of data (interest_over_time, related_queries, related_topics, etc.)")
    timeframe = models.CharField(max_length=50, help_text="Timeframe for the data (e.g., 'today 12-m', '2020-01-01 2025-12-31')")
    geo = models.CharField(max_length=10, blank=True, null=True, help_text="Geographic location (e.g., 'GH' for Ghana)")
    
    # Cached data
    cached_data = models.JSONField(help_text="The actual cached Google Trends data")
    last_fetched = models.DateTimeField(auto_now_add=True, help_text="When this data was last fetched from Google")
    cache_expiry = models.DateTimeField(help_text="When this cache expires")
    
    # Cache status
    status = models.CharField(max_length=20, choices=CACHE_STATUS_CHOICES, default='fresh')
    fetch_count = models.IntegerField(default=0, help_text="Number of times this data has been fetched from Google")
    last_accessed = models.DateTimeField(auto_now=True, help_text="Last time this cache was accessed")
    
    # Error tracking
    last_error = models.TextField(blank=True, null=True, help_text="Last error encountered when fetching")
    retry_count = models.IntegerField(default=0, help_text="Number of retry attempts")
    
    class Meta:
        db_table = 'google_trends_cache'
        verbose_name = 'Google Trends Cache'
        verbose_name_plural = 'Google Trends Cache'
        ordering = ['-last_fetched']
        indexes = [
            models.Index(fields=['disease_name', 'data_type']),
            models.Index(fields=['cache_key']),
            models.Index(fields=['status', 'cache_expiry']),
        ]
    
    def __str__(self):
        return f"{self.disease_name} - {self.data_type} ({self.status})"
    
    @property
    def is_expired(self):
        """Check if cache has expired"""
        return timezone.now() > self.cache_expiry
    
    @property
    def is_stale(self):
        """Check if cache is stale (older than 24 hours)"""
        from datetime import timedelta
        return timezone.now() > self.last_fetched + timedelta(hours=24)
    
    def update_status(self):
        """Update cache status based on expiry and staleness"""
        if self.is_expired:
            self.status = 'expired'
        elif self.is_stale:
            self.status = 'stale'
        else:
            self.status = 'fresh'
        self.save(update_fields=['status'])
    
    def should_refresh(self):
        """Check if cache should be refreshed"""
        return self.is_expired or self.is_stale
    
    def mark_accessed(self):
        """Mark cache as accessed"""
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])


class GoogleTrendsMetrics(models.Model):
    """
    Model to store aggregated Google Trends metrics for diseases
    """
    disease_name = models.CharField(max_length=100, help_text="Disease name")
    date = models.DateField(help_text="Date of the metrics")
    
    # Search interest metrics
    search_interest = models.FloatField(help_text="Average search interest score (0-100)")
    peak_interest = models.FloatField(help_text="Peak search interest for the day")
    total_searches = models.BigIntegerField(help_text="Estimated total searches (derived from interest)")
    
    # Trend metrics
    trend_direction = models.CharField(max_length=20, choices=[
        ('rising', 'Rising'),
        ('falling', 'Falling'),
        ('stable', 'Stable'),
        ('volatile', 'Volatile'),
    ], help_text="Overall trend direction")
    trend_strength = models.FloatField(help_text="Strength of the trend (-1 to 1)")
    
    # Related queries and topics
    top_related_queries = models.JSONField(default=list, help_text="Top related search queries")
    top_related_topics = models.JSONField(default=list, help_text="Top related topics")
    
    # Geographic data
    top_regions = models.JSONField(default=list, help_text="Top regions by search interest")
    regional_distribution = models.JSONField(default=dict, help_text="Regional search distribution")
    
    # Metadata
    data_source = models.CharField(max_length=20, default='google_trends', help_text="Source of the data")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'google_trends_metrics'
        verbose_name = 'Google Trends Metrics'
        verbose_name_plural = 'Google Trends Metrics'
        unique_together = ['disease_name', 'date']
        ordering = ['-date', 'disease_name']
        indexes = [
            models.Index(fields=['disease_name', 'date']),
            models.Index(fields=['trend_direction']),
            models.Index(fields=['search_interest']),
        ]
    
    def __str__(self):
        return f"{self.disease_name} - {self.date} (Interest: {self.search_interest})"
    
    @property
    def search_volume_category(self):
        """Categorize search volume based on interest score"""
        if self.search_interest >= 80:
            return 'Very High'
        elif self.search_interest >= 60:
            return 'High'
        elif self.search_interest >= 40:
            return 'Medium'
        elif self.search_interest >= 20:
            return 'Low'
        else:
            return 'Very Low'


class GoogleTrendsRequestLog(models.Model):
    """
    Model to log Google Trends API requests for monitoring and debugging
    """
    REQUEST_STATUS_CHOICES = [
        ('success', 'Success'),
        ('rate_limited', 'Rate Limited'),
        ('error', 'Error'),
        ('cached', 'Served from Cache'),
    ]
    
    # Request details
    timestamp = models.DateTimeField(auto_now_add=True)
    disease_name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50)
    timeframe = models.CharField(max_length=50)
    geo = models.CharField(max_length=10, blank=True, null=True)
    
    # Response details
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES)
    response_time = models.FloatField(help_text="Response time in seconds", null=True, blank=True)
    cache_hit = models.BooleanField(default=False, help_text="Whether data was served from cache")
    
    # Error details
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    # Rate limiting info
    rate_limit_remaining = models.IntegerField(null=True, blank=True, help_text="Remaining requests in current window")
    rate_limit_reset = models.DateTimeField(null=True, blank=True, help_text="When rate limit resets")
    
    class Meta:
        db_table = 'google_trends_request_log'
        verbose_name = 'Google Trends Request Log'
        verbose_name_plural = 'Google Trends Request Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['disease_name', 'status']),
            models.Index(fields=['status', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.disease_name} - {self.status} at {self.timestamp}"


class Hospital(models.Model):
    """
    Model to store hospitals in the system
    """
    id = models.AutoField(primary_key=True)
    hospital_id = models.CharField(max_length=16, null=True, blank=True, unique=True, editable=False, db_index=True, help_text="System-generated unique hospital identifier")
    name = models.CharField(max_length=255, unique=True, help_text="Hospital name")
    slug = models.CharField(max_length=255, unique=True, help_text="URL-friendly identifier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hospitals'
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['name']
        indexes = [
            models.Index(fields=['hospital_id']),
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        if not self.hospital_id:
            self.hospital_id = self._generate_hospital_id()
        super().save(*args, **kwargs)

    def _generate_slug(self):
        """Generate a URL-friendly slug from the hospital name"""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', self.name.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return slug

    def _generate_hospital_id(self):
        """Generate a short unique hospital id like HSP-1A2B3C4D"""
        import uuid
        candidate = f"HSP-{uuid.uuid4().hex[:8].upper()}"
        # Ensure uniqueness without extra query loops during save migrations
        while Hospital.objects.filter(hospital_id=candidate).exists():
            candidate = f"HSP-{uuid.uuid4().hex[:8].upper()}"
        return candidate

    @classmethod
    def get_by_slug(cls, slug):
        """Get hospital by slug"""
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None

    @classmethod
    def search_by_name(cls, query):
        """Search hospitals by name"""
        return cls.objects.filter(name__icontains=query)

    @classmethod
    def get_all_hospitals(cls):
        """Get all hospitals ordered by name"""
        return cls.objects.all().order_by('name')

class ArticleTag(models.Model):
    """
    Model to store article tags/categories
    """
    TAG_CHOICES = [
        ('diabetes', 'Diabetes'),
        ('malaria', 'Malaria'),
        ('research', 'Research'),
    ]
    
    name = models.CharField(max_length=50, choices=TAG_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code for tag display")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class for tag display")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'article_tags'
        verbose_name = 'Article Tag'
        verbose_name_plural = 'Article Tags'
    
    def __str__(self):
        return self.name
    
    def get_article_count(self):
        """Get the number of articles using this tag"""
        return self.article_set.count()
    get_article_count.short_description = 'Article Count'


class Article(models.Model):
    """
    Model to store health articles and blog posts
    """
    ARTICLE_TYPE_CHOICES = [
        ('article', 'Article'),
        ('blog', 'Blog Post'),
        ('research', 'Research Paper'),
        ('guideline', 'Guideline'),
        ('case_study', 'Case Study'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic information
    title = models.CharField(max_length=255, help_text="Article title")
    slug = models.CharField(max_length=255, unique=True, help_text="URL-friendly identifier")
    summary = models.TextField(help_text="Brief summary/abstract of the article")
    content = models.TextField(help_text="Full article content")
    
    # Article metadata
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPE_CHOICES, default='article')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Author information
    author_name = models.CharField(max_length=255, help_text="Author's full name")
    author_credentials = models.CharField(max_length=255, blank=True, null=True, help_text="Author's credentials/qualifications")
    author_affiliation = models.CharField(max_length=255, blank=True, null=True, help_text="Author's institution/organization")
    
    # Publication details
    publication_date = models.DateField(help_text="Date when article was published")
    estimated_read_time = models.PositiveIntegerField(help_text="Estimated reading time in minutes")
    
    # Reference and source
    reference_link = models.URLField(help_text="Link to the original source/reference")
    doi = models.CharField(max_length=100, blank=True, null=True, help_text="Digital Object Identifier if available")
    
    # Tags and categories
    tags = models.ManyToManyField(ArticleTag, related_name='articles', help_text="Article tags/categories")
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0, help_text="Number of likes")
    comments_count = models.PositiveIntegerField(default=0, help_text="Number of comments")
    views_count = models.PositiveIntegerField(default=0, help_text="Number of views")
    bookmarks_count = models.PositiveIntegerField(default=0, help_text="Number of bookmarks")
    
    # SEO and display
    meta_description = models.TextField(blank=True, null=True, help_text="Meta description for SEO")
    featured_image = models.ImageField(upload_to='articles/images/', blank=True, null=True, help_text="Featured image for the article")
    is_featured = models.BooleanField(default=False, help_text="Whether this article is featured on the homepage")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True, help_text="When the article was published")
    
    class Meta:
        db_table = 'articles'
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-publication_date', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'publication_date']),
            models.Index(fields=['article_type', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['author_name']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = self._generate_slug()
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def _generate_slug(self):
        """Generate a URL-friendly slug from the title"""
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        
        # Ensure uniqueness
        while Article.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def get_absolute_url(self):
        """Get the absolute URL for this article"""
        return f"/articles/{self.slug}/"
    
    def increment_views(self):
        """Increment the view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_likes(self):
        """Increment the like count"""
        self.likes_count += 1
        self.save(update_fields=['likes_count'])
    
    def increment_comments(self):
        """Increment the comment count"""
        self.comments_count += 1
        self.save(update_fields=['comments_count'])
    
    def increment_bookmarks(self):
        """Increment the bookmark count"""
        self.bookmarks_count += 1
        self.save(update_fields=['bookmarks_count'])
    
    @property
    def is_published(self):
        """Check if the article is published"""
        return self.status == 'published'
    
    @property
    def reading_time_display(self):
        """Get formatted reading time"""
        if self.estimated_read_time == 1:
            return "1 min read"
        return f"{self.estimated_read_time} min read"
    
    @property
    def tag_names(self):
        """Get list of tag names"""
        return [tag.name for tag in self.tags.all()]
    
    @property
    def primary_tag(self):
        """Get the primary tag (first tag)"""
        return self.tags.first()


class ResearchPaper(models.Model):
    """
    Model specifically for research papers with additional academic fields
    """
    PAPER_TYPE_CHOICES = [
        ('systematic_review', 'Systematic Review'),
        ('meta_analysis', 'Meta-Analysis'),
        ('randomized_trial', 'Randomized Controlled Trial'),
        ('cohort_study', 'Cohort Study'),
        ('case_control', 'Case-Control Study'),
        ('cross_sectional', 'Cross-Sectional Study'),
        ('qualitative', 'Qualitative Study'),
        ('mixed_methods', 'Mixed Methods Study'),
        ('other', 'Other'),
    ]
    
    # Link to base article
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='research_paper')
    
    # Research-specific fields
    paper_type = models.CharField(max_length=30, choices=PAPER_TYPE_CHOICES, help_text="Type of research paper")
    abstract = models.TextField(help_text="Research abstract")
    keywords = models.JSONField(default=list, help_text="List of research keywords")
    
    # Methodology
    methodology = models.TextField(help_text="Research methodology description")
    sample_size = models.PositiveIntegerField(blank=True, null=True, help_text="Sample size of the study")
    study_duration = models.CharField(max_length=100, blank=True, null=True, help_text="Duration of the study")
    
    # Results and findings
    key_findings = models.TextField(help_text="Key findings of the research")
    conclusions = models.TextField(help_text="Research conclusions")
    limitations = models.TextField(blank=True, null=True, help_text="Study limitations")
    
    # Academic metadata
    journal_name = models.CharField(max_length=255, blank=True, null=True, help_text="Journal where paper was published")
    volume_issue = models.CharField(max_length=100, blank=True, null=True, help_text="Journal volume and issue")
    page_numbers = models.CharField(max_length=50, blank=True, null=True, help_text="Page numbers in journal")
    impact_factor = models.FloatField(blank=True, null=True, help_text="Journal impact factor if available")
    
    # Citations and references
    citation_count = models.PositiveIntegerField(default=0, help_text="Number of citations")
    references = models.JSONField(default=list, help_text="List of references cited")
    
    # Research metrics
    h_index = models.PositiveIntegerField(default=0, help_text="H-index of the research")
    research_quality_score = models.FloatField(blank=True, null=True, help_text="Quality score (0-100)")
    
    # Funding and ethics
    funding_source = models.CharField(max_length=255, blank=True, null=True, help_text="Source of research funding")
    ethical_approval = models.CharField(max_length=255, blank=True, null=True, help_text="Ethical approval details")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'research_papers'
        verbose_name = 'Research Paper'
        verbose_name_plural = 'Research Papers'
        ordering = ['-article__publication_date']
        indexes = [
            models.Index(fields=['paper_type']),
            models.Index(fields=['journal_name']),
            models.Index(fields=['citation_count']),
        ]
    
    def __str__(self):
        return f"Research Paper: {self.article.title}"
    
    @property
    def title(self):
        """Get the title from the linked article"""
        return self.article.title
    
    @property
    def author_name(self):
        """Get the author name from the linked article"""
        return self.article.author_name
    
    @property
    def publication_date(self):
        """Get the publication date from the linked article"""
        return self.article.publication_date
    
    @property
    def tags(self):
        """Get the tags from the linked article"""
        return self.article.tags.all()
    
    @property
    def reference_link(self):
        """Get the reference link from the linked article"""
        return self.article.reference_link


class ArticleComment(models.Model):
    """
    Model to store comments on articles
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='article_comments')
    
    # Comment content
    content = models.TextField(help_text="Comment content")
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', help_text="Parent comment for replies")
    
    # Moderation
    is_approved = models.BooleanField(default=True, help_text="Whether comment is approved by moderators")
    is_flagged = models.BooleanField(default=False, help_text="Whether comment has been flagged for review")
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0, help_text="Number of likes on this comment")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'article_comments'
        verbose_name = 'Article Comment'
        verbose_name_plural = 'Article Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['parent_comment', 'created_at']),
            models.Index(fields=['is_approved', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"
    
    def increment_likes(self):
        """Increment the like count"""
        self.likes_count += 1
        self.save(update_fields=['likes_count'])
    
    @property
    def is_reply(self):
        """Check if this is a reply to another comment"""
        return self.parent_comment is not None
    
    @property
    def reply_count(self):
        """Get the number of replies to this comment"""
        return self.replies.count()


class ArticleLike(models.Model):
    """
    Model to track article likes by users
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='article_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'article_likes'
        verbose_name = 'Article Like'
        verbose_name_plural = 'Article Likes'
        unique_together = ['article', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'user']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} liked {self.article.title}"


class ArticleBookmark(models.Model):
    """
    Model to track article bookmarks by users
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='article_bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'article_bookmarks'
        verbose_name = 'Article Bookmark'
        verbose_name_plural = 'Article Bookmarks'
        unique_together = ['article', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'user']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title}"


class ArticleView(models.Model):
    """
    Model to track article views for analytics
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='article_views', null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="IP address of the viewer")
    user_agent = models.TextField(blank=True, null=True, help_text="User agent string")
    session_id = models.CharField(max_length=100, blank=True, null=True, help_text="Session ID for anonymous users")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'article_views'
        verbose_name = 'Article View'
        verbose_name_plural = 'Article Views'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
        ]
    
    def __str__(self):
        viewer = self.user.username if self.user else f"Anonymous ({self.ip_address})"
        return f"{viewer} viewed {self.article.title}"