from django.db import models
from django.utils import timezone
import uuid

class ChatSession(models.Model):
    """Model for storing chat sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('ended', 'Ended'),
            ('archived', 'Archived')
        ],
        default='active'
    )
    user_id = models.CharField(max_length=255, null=True, blank=True)
    total_messages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-start_time']

    def __str__(self):
        return f"Session {self.session_id} - {self.status}"

    def get_duration(self):
        """Get session duration in minutes"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 60
        return None

    def get_message_count(self):
        """Get total message count"""
        return self.chatmessage_set.count()

class ChatMessage(models.Model):
    """Model for storing individual chat messages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User'),
            ('assistant', 'Assistant'),
            ('system', 'System')
        ]
    )
    content = models.TextField()
    user_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('quick_question', 'Quick Question'),
            ('error', 'Error'),
            ('system', 'System Message')
        ],
        default='text'
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

    def get_response_time(self):
        """Get response time if this is an assistant message"""
        if self.role == 'assistant':
            # Find the previous user message
            prev_user_msg = ChatMessage.objects.filter(
                session=self.session,
                role='user',
                timestamp__lt=self.timestamp
            ).order_by('-timestamp').first()
            
            if prev_user_msg:
                response_time = self.timestamp - prev_user_msg.timestamp
                return response_time.total_seconds()
        return None

class ChatAnalytics(models.Model):
    """Model for storing chat analytics and insights"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(ChatSession, on_delete=models.CASCADE)
    total_questions = models.IntegerField(default=0)
    disease_related_questions = models.IntegerField(default=0)
    diabetes_questions = models.IntegerField(default=0)
    malaria_questions = models.IntegerField(default=0)
    average_response_time = models.FloatField(null=True, blank=True)
    user_satisfaction_score = models.FloatField(null=True, blank=True)
    common_topics = models.JSONField(default=list, blank=True)
    sentiment_analysis = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_analytics'
        verbose_name_plural = 'Chat Analytics'

    def __str__(self):
        return f"Analytics for Session {self.session.session_id}"

class DiseaseQuery(models.Model):
    """Model for storing disease-specific queries for fine-tuning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    disease_name = models.CharField(max_length=100)
    query_text = models.TextField()
    response_text = models.TextField()
    confidence_score = models.FloatField(null=True, blank=True)
    query_type = models.CharField(
        max_length=50,
        choices=[
            ('trends', 'Trends'),
            ('prediction', 'Prediction'),
            ('symptoms', 'Symptoms'),
            ('prevention', 'Prevention'),
            ('treatment', 'Treatment'),
            ('general', 'General')
        ]
    )
    user_feedback = models.CharField(
        max_length=20,
        choices=[
            ('positive', 'Positive'),
            ('negative', 'Negative'),
            ('neutral', 'Neutral'),
            ('not_provided', 'Not Provided')
        ],
        default='not_provided'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'disease_queries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.disease_name}: {self.query_text[:50]}..."

class FineTuningDataset(models.Model):
    """Model for storing data for Vertex AI fine-tuning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease_name = models.CharField(max_length=100)
    instruction = models.TextField()  # The prompt/instruction
    input_text = models.TextField(blank=True)  # Context or input
    output_text = models.TextField()  # Expected response
    source = models.CharField(
        max_length=50,
        choices=[
            ('chat_history', 'Chat History'),
            ('manual_curation', 'Manual Curation'),
            ('expert_knowledge', 'Expert Knowledge'),
            ('medical_literature', 'Medical Literature')
        ]
    )
    quality_score = models.FloatField(default=1.0)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fine_tuning_dataset'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.disease_name}: {self.instruction[:50]}..."

    def to_training_format(self):
        """Convert to Vertex AI fine-tuning format"""
        return {
            "instruction": self.instruction,
            "input": self.input_text,
            "output": self.output_text
        } 