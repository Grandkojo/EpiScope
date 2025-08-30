from rest_framework import serializers
from .models import DiseaseTrends
from .models import HospitalLocalities
from .models import Hospital
from .models import (
    PredictionHistory, 
    ReinforcementLearningData, 
    ModelTrainingSession,
    PredictionFeedback
)
from .models import GoogleTrendsCache, GoogleTrendsMetrics, GoogleTrendsRequestLog
from .models import ArticleTag, Article, ResearchPaper, ArticleComment, ArticleLike, ArticleBookmark, ArticleView


class DiseaseTrendsSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source='disease.disease_name', read_only=True)

    class Meta:
        model = DiseaseTrends
        fields = ['id', 'disease', 'disease_name', 'year', 'month', 'trend_value']

class HospitalLocalitiesSerializer(serializers.ModelSerializer):
    """
    Serializer for HospitalLocalities model
    """
    class Meta:
        model = HospitalLocalities
        fields = ['id', 'locality', 'orgname', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class HospitalLocalitiesListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing hospital localities
    """
    class Meta:
        model = HospitalLocalities
        fields = ['locality', 'orgname']

class HospitalLocalitiesFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering hospital localities
    """
    locality = serializers.CharField(required=False, help_text="Filter by locality")
    orgname = serializers.CharField(required=False, help_text="Filter by hospital name")
    search = serializers.CharField(required=False, help_text="Search in both locality and orgname")

class HospitalSerializer(serializers.ModelSerializer):
    """
    Serializer for Hospital model
    """
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class HospitalListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing hospitals
    """
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'slug']

class HospitalFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering hospitals
    """
    name = serializers.CharField(required=False, help_text="Filter by hospital name")
    search = serializers.CharField(required=False, help_text="Search in hospital name") 


class PredictionHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for PredictionHistory model
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    prediction_accuracy = serializers.FloatField(read_only=True)
    is_learning_ready = serializers.BooleanField(read_only=True)
    model_learning_score = serializers.FloatField(read_only=True)
    
    # Add debug field to check if confidence_score is being processed
    confidence_score_debug = serializers.SerializerMethodField()
    
    class Meta:
        model = PredictionHistory
        fields = [
            'id', 'prediction_id', 'user', 'user_username', 'timestamp',
            'age', 'gender', 'locality', 'schedule_date', 'pregnant_patient',
            'nhia_patient', 'vertex_ai_enabled', 'disease_type', 'symptoms_description',
            'predicted_disease', 'confidence_score', 'confidence_score_debug', 'status', 'actual_disease',
            'medicine_prescribed', 'cost_of_treatment', 'feedback_timestamp',
            'model_learning_score', 'hospital_name', 'doctor_notes',
            'prediction_accuracy', 'is_learning_ready', 'ai_insights'
        ]
        read_only_fields = [
            'id', 'prediction_id', 'user', 'user_username', 'timestamp',
            'feedback_timestamp', 'model_learning_score', 'prediction_accuracy',
            'is_learning_ready', 'confidence_score_debug'
        ]
    
    def get_confidence_score_debug(self, obj):
        """Debug method to check confidence score value"""
        return {
            'raw_value': obj.confidence_score,
            'type': type(obj.confidence_score).__name__,
            'is_none': obj.confidence_score is None,
            'formatted': f"{obj.confidence_score:.3f}" if obj.confidence_score is not None else None
        }


class PredictionDetailsSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for prediction details display
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    prediction_accuracy = serializers.FloatField(read_only=True)
    is_learning_ready = serializers.BooleanField(read_only=True)
    model_learning_score = serializers.FloatField(read_only=True)
    
    # Formatted fields for display
    formatted_timestamp = serializers.SerializerMethodField()
    formatted_confidence = serializers.SerializerMethodField()
    formatted_cost = serializers.SerializerMethodField()
    formatted_schedule_date = serializers.SerializerMethodField()
    disease_name = serializers.SerializerMethodField()
    actual_disease_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    # Add debug field to check if confidence_score is being processed
    confidence_score_debug = serializers.SerializerMethodField()
    
    class Meta:
        model = PredictionHistory
        fields = [
            'id', 'prediction_id', 'user', 'user_username', 'timestamp', 'formatted_timestamp',
            'age', 'gender', 'locality', 'schedule_date', 'formatted_schedule_date', 
            'pregnant_patient', 'nhia_patient', 'vertex_ai_enabled', 'disease_type', 
            'disease_name', 'symptoms_description', 'predicted_disease', 'actual_disease',
            'actual_disease_name', 'confidence_score', 'confidence_score_debug', 'formatted_confidence', 'status', 
            'status_display', 'medicine_prescribed', 'cost_of_treatment', 'formatted_cost',
            'feedback_timestamp', 'model_learning_score', 'hospital_name', 'doctor_notes',
            'prediction_accuracy', 'is_learning_ready', 'ai_insights'
        ]
        read_only_fields = [
            'id', 'prediction_id', 'user', 'user_username', 'timestamp', 'formatted_timestamp',
            'feedback_timestamp', 'model_learning_score', 'prediction_accuracy',
            'is_learning_ready', 'formatted_confidence', 'formatted_cost', 'formatted_schedule_date',
            'disease_name', 'actual_disease_name', 'status_display', 'confidence_score_debug'
        ]
    
    def get_confidence_score_debug(self, obj):
        """Debug method to check confidence score value"""
        return {
            'raw_value': obj.confidence_score,
            'type': type(obj.confidence_score).__name__,
            'is_none': obj.confidence_score is None,
            'formatted': f"{obj.confidence_score:.3f}" if obj.confidence_score is not None else None
        }
    
    def get_formatted_timestamp(self, obj):
        """Format timestamp for display"""
        if obj.timestamp:
            return obj.timestamp.strftime('%Y-%m-%d %H:%M')
        return None
    
    def get_formatted_confidence(self, obj):
        """Format confidence score as percentage"""
        if obj.confidence_score is not None:
            return f"{obj.confidence_score * 100:.1f}%"
        return None
    
    def get_formatted_cost(self, obj):
        """Format cost with currency"""
        if obj.cost_of_treatment is not None:
            return f"${obj.cost_of_treatment}"
        return None
    
    def get_formatted_schedule_date(self, obj):
        """Format schedule date"""
        if obj.schedule_date:
            return obj.schedule_date.strftime('%Y-%m-%d')
        return None
    
    def get_disease_name(self, obj):
        """Get disease name from predicted_disease"""
        disease_mapping = {
            '1': 'Hypertension',
            '0': 'Diabetes',
            'diabetes': 'Diabetes',
            'hypertension': 'Hypertension'
        }
        return disease_mapping.get(str(obj.predicted_disease), obj.predicted_disease)
    
    def get_actual_disease_name(self, obj):
        """Get actual disease name"""
        if obj.actual_disease:
            disease_mapping = {
                '1': 'Hypertension',
                '0': 'Diabetes',
                'diabetes': 'Diabetes',
                'hypertension': 'Hypertension'
            }
            return disease_mapping.get(str(obj.actual_disease), obj.actual_disease)
        return None
    
    def get_status_display(self, obj):
        """Get formatted status display"""
        status_mapping = {
            'pending': 'Pending',
            'confirmed': 'Confirmed',
            'corrected': 'Corrected',
            'discarded': 'Discarded'
        }
        return status_mapping.get(obj.status, obj.status)


class ReinforcementLearningDataSerializer(serializers.ModelSerializer):
    """
    Serializer for ReinforcementLearningData model
    """
    total_processed = serializers.IntegerField(read_only=True)
    processing_rate = serializers.FloatField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ReinforcementLearningData
        fields = [
            'id', 'period_start', 'period_end', 'disease_type',
            'total_predictions', 'confirmed_predictions', 'corrected_predictions',
            'discarded_predictions', 'avg_confidence_score', 'avg_learning_score',
            'avg_cost_of_treatment', 'common_medicines', 'medicine_frequency',
            'model_accuracy', 'model_precision', 'model_recall', 'model_f1_score',
            'last_training_date', 'training_data_count',
            'total_processed', 'processing_rate', 'success_rate'
        ]
        read_only_fields = [
            'id', 'total_processed', 'processing_rate', 'success_rate'
        ]


class ModelTrainingSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for ModelTrainingSession model
    """
    initiated_by_username = serializers.CharField(source='initiated_by.username', read_only=True)
    duration = serializers.DurationField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ModelTrainingSession
        fields = [
            'id', 'session_id', 'session_name', 'disease_type', 'model_type',
            'training_parameters', 'data_period_start', 'data_period_end',
            'training_data_count', 'status', 'start_time', 'end_time',
            'training_accuracy', 'validation_accuracy', 'test_accuracy',
            'model_file_path', 'scaler_file_path', 'training_logs',
            'error_message', 'initiated_by', 'initiated_by_username',
            'duration', 'is_completed', 'is_failed'
        ]
        read_only_fields = [
            'id', 'session_id', 'initiated_by', 'initiated_by_username',
            'start_time', 'end_time', 'duration', 'is_completed', 'is_failed'
        ]


class PredictionFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for PredictionFeedback model
    """
    provided_by_username = serializers.CharField(source='provided_by.username', read_only=True)
    prediction_id = serializers.CharField(source='prediction.prediction_id', read_only=True)
    
    class Meta:
        model = PredictionFeedback
        fields = [
            'id', 'prediction', 'prediction_id', 'feedback_type', 'feedback_text',
            'rating', 'provided_by', 'provided_by_username', 'timestamp',
            'doctor_notes', 'patient_outcome'
        ]
        read_only_fields = [
            'id', 'provided_by', 'provided_by_username', 'timestamp'
        ]


class PredictionDashboardSerializer(serializers.Serializer):
    """
    Serializer for prediction dashboard data
    """
    user_statistics = serializers.DictField()
    recent_predictions = PredictionHistorySerializer(many=True)
    learning_statistics = serializers.DictField()


class ReinforcementDataSubmissionSerializer(serializers.Serializer):
    """
    Serializer for submitting reinforcement learning data
    """
    prediction_id = serializers.CharField()
    status = serializers.ChoiceField(choices=PredictionHistory.STATUS_CHOICES)
    actual_disease = serializers.CharField(required=False, allow_blank=True)
    medicine_prescribed = serializers.CharField(required=False, allow_blank=True)
    cost_of_treatment = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False
    )
    doctor_notes = serializers.CharField(required=False, allow_blank=True)


class TrainingSessionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating training sessions
    """
    session_name = serializers.CharField()
    disease_type = serializers.CharField()
    model_type = serializers.CharField()
    training_parameters = serializers.DictField(required=False)
    data_period_start = serializers.DateField()
    data_period_end = serializers.DateField() 


class GoogleTrendsCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleTrendsCache
        fields = '__all__'
        read_only_fields = ('last_fetched', 'last_accessed', 'fetch_count', 'retry_count')


class GoogleTrendsMetricsSerializer(serializers.ModelSerializer):
    search_volume_category = serializers.ReadOnlyField()
    
    class Meta:
        model = GoogleTrendsMetrics
        fields = '__all__'
        read_only_fields = ('last_updated',)


class GoogleTrendsRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleTrendsRequestLog
        fields = '__all__'
        read_only_fields = ('timestamp',)


class GoogleTrendsDataSerializer(serializers.Serializer):
    """Serializer for Google Trends API responses"""
    disease_name = serializers.CharField()
    timeframe = serializers.CharField()
    geo = serializers.CharField(allow_blank=True, required=False)
    
    # Interest over time data
    interest_over_time = serializers.ListField(child=serializers.DictField(), required=False)
    
    # Related queries and topics
    related_queries = serializers.DictField(required=False)
    related_topics = serializers.DictField(required=False)
    
    # Geographic data
    interest_by_region = serializers.ListField(child=serializers.DictField(), required=False)
    
    # Metadata
    cache_status = serializers.CharField(required=False)
    last_updated = serializers.DateTimeField(required=False)
    data_source = serializers.CharField(default='google_trends')
    
    # Summary metrics
    total_searches = serializers.IntegerField(required=False)
    peak_interest = serializers.FloatField(required=False)
    trend_direction = serializers.CharField(required=False)
    trend_strength = serializers.FloatField(required=False)


class GoogleTrendsSummarySerializer(serializers.Serializer):
    """Serializer for Google Trends summary data"""
    disease_name = serializers.CharField()
    current_interest = serializers.FloatField()
    trend_direction = serializers.CharField()
    trend_strength = serializers.FloatField()
    total_searches = serializers.IntegerField()
    peak_interest = serializers.FloatField()
    top_related_queries = serializers.ListField(child=serializers.CharField())
    top_regions = serializers.ListField(child=serializers.DictField())
    last_updated = serializers.DateTimeField()
    cache_status = serializers.CharField() 


class ArticleTagSerializer(serializers.ModelSerializer):
    """Serializer for ArticleTag model"""
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ArticleTag
        fields = ['id', 'name', 'description', 'color', 'icon', 'article_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_article_count(self, obj):
        return obj.articles.count()


class ArticleCommentSerializer(serializers.ModelSerializer):
    """Serializer for ArticleComment model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_reply = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ArticleComment
        fields = ['id', 'article', 'user', 'user_username', 'content', 'parent_comment', 
                 'is_approved', 'is_flagged', 'likes_count', 'is_reply', 'reply_count', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'likes_count', 'created_at', 'updated_at']
    
    def get_is_reply(self, obj):
        return obj.parent_comment is not None
    
    def get_reply_count(self, obj):
        return obj.replies.count()


class ArticleLikeSerializer(serializers.ModelSerializer):
    """Serializer for ArticleLike model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ArticleLike
        fields = ['id', 'article', 'user', 'user_username', 'created_at']
        read_only_fields = ['id', 'created_at']


class ArticleBookmarkSerializer(serializers.ModelSerializer):
    """Serializer for ArticleBookmark model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ArticleBookmark
        fields = ['id', 'article', 'user', 'user_username', 'created_at']
        read_only_fields = ['id', 'created_at']


class ArticleViewSerializer(serializers.ModelSerializer):
    """Serializer for ArticleView model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ArticleView
        fields = ['id', 'article', 'user', 'user_username', 'ip_address', 'user_agent', 
                 'session_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""
    tags = ArticleTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=ArticleTag.objects.all(), 
        source='tags', 
        write_only=True,
        required=False
    )
    author_name = serializers.CharField(max_length=255)
    estimated_read_time = serializers.IntegerField(min_value=1)
    reading_time_display = serializers.CharField(read_only=True)
    tag_names = serializers.ListField(child=serializers.CharField(), read_only=True)
    primary_tag = ArticleTagSerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'content', 'article_type', 'status',
            'author_name', 'author_credentials', 'author_affiliation', 'publication_date',
            'estimated_read_time', 'reference_link', 'doi', 'tags', 'tag_ids',
            'likes_count', 'comments_count', 'views_count', 'bookmarks_count',
            'meta_description', 'featured_image', 'is_featured', 'reading_time_display',
            'tag_names', 'primary_tag', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'slug', 'likes_count', 'comments_count', 'views_count', 
            'bookmarks_count', 'reading_time_display', 'tag_names', 'primary_tag',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def validate_publication_date(self, value):
        """Validate that publication date is not in the future"""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Publication date cannot be in the future.")
        return value
    
    def validate(self, data):
        """Validate article data"""
        # Ensure content is not empty
        if not data.get('content', '').strip():
            raise serializers.ValidationError("Article content cannot be empty.")
        
        # Ensure summary is not empty
        if not data.get('summary', '').strip():
            raise serializers.ValidationError("Article summary cannot be empty.")
        
        return data


class ArticleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for article lists"""
    tags = ArticleTagSerializer(many=True, read_only=True)
    reading_time_display = serializers.CharField(read_only=True)
    tag_names = serializers.ListField(child=serializers.CharField(), read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'article_type', 'status',
            'author_name', 'publication_date', 'estimated_read_time', 'reading_time_display',
            'tags', 'tag_names', 'likes_count', 'comments_count', 'views_count',
            'is_featured', 'created_at'
        ]


class ResearchPaperSerializer(serializers.ModelSerializer):
    """Serializer for ResearchPaper model"""
    article = ArticleSerializer(read_only=True)
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        source='article',
        write_only=True
    )
    
    class Meta:
        model = ResearchPaper
        fields = [
            'id', 'article', 'article_id', 'paper_type', 'abstract', 'keywords',
            'methodology', 'sample_size', 'study_duration', 'key_findings',
            'conclusions', 'limitations', 'journal_name', 'volume_issue',
            'page_numbers', 'impact_factor', 'citation_count', 'references',
            'h_index', 'research_quality_score', 'funding_source',
            'ethical_approval', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_research_quality_score(self, value):
        """Validate research quality score is between 0 and 100"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Research quality score must be between 0 and 100.")
        return value
    
    def validate_citation_count(self, value):
        """Validate citation count is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Citation count cannot be negative.")
        return value


class ResearchPaperListSerializer(serializers.ModelSerializer):
    """Simplified serializer for research paper lists"""
    article_title = serializers.CharField(source='article.title', read_only=True)
    article_author = serializers.CharField(source='article.author_name', read_only=True)
    article_publication_date = serializers.DateField(source='article.publication_date', read_only=True)
    article_tags = ArticleTagSerializer(source='article.tags', many=True, read_only=True)
    
    class Meta:
        model = ResearchPaper
        fields = [
            'id', 'article_title', 'article_author', 'article_publication_date',
            'article_tags', 'paper_type', 'abstract', 'journal_name', 'citation_count',
            'research_quality_score', 'created_at'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual articles"""
    tags = ArticleTagSerializer(many=True, read_only=True)
    comments = ArticleCommentSerializer(many=True, read_only=True)
    likes = ArticleLikeSerializer(many=True, read_only=True)
    bookmarks = ArticleBookmarkSerializer(many=True, read_only=True)
    views = ArticleViewSerializer(many=True, read_only=True)
    research_paper = ResearchPaperSerializer(read_only=True)
    reading_time_display = serializers.CharField(read_only=True)
    tag_names = serializers.ListField(child=serializers.CharField(), read_only=True)
    primary_tag = ArticleTagSerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'content', 'article_type', 'status',
            'author_name', 'author_credentials', 'author_affiliation', 'publication_date',
            'estimated_read_time', 'reference_link', 'doi', 'tags', 'tag_names',
            'primary_tag', 'likes_count', 'comments_count', 'views_count', 'bookmarks_count',
            'meta_description', 'featured_image', 'is_featured', 'reading_time_display',
            'comments', 'likes', 'bookmarks', 'views', 'research_paper',
            'created_at', 'updated_at', 'published_at'
        ] 