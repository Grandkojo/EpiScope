from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    PredictionHistory, 
    ReinforcementLearningData, 
    ModelTrainingSession,
    PredictionFeedback,
    ArticleTag, Article, ResearchPaper, ArticleComment, 
    ArticleLike, ArticleBookmark, ArticleView
)
from .prediction_service import (
    PredictionHistoryService,
    ReinforcementLearningService,
    PredictionFeedbackService
)
from .serializers import (
    PredictionHistorySerializer,
    ReinforcementLearningDataSerializer,
    ModelTrainingSessionSerializer,
    PredictionFeedbackSerializer,
    ArticleTagSerializer, ArticleSerializer, ArticleListSerializer, ArticleDetailSerializer,
    ResearchPaperSerializer, ResearchPaperListSerializer, ArticleCommentSerializer,
    ArticleLikeSerializer, ArticleBookmarkSerializer, ArticleViewSerializer
)
from api.permissions import IsAdminOrReadOnly


class PredictionHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing prediction history
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PredictionHistorySerializer
    
    def get_queryset(self):
        """Filter predictions by current user"""
        return PredictionHistory.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def user_predictions(self, request):
        """Get predictions for the current user with filters"""
        status_filter = request.query_params.get('status')
        disease_type = request.query_params.get('disease_type')
        limit = int(request.query_params.get('limit', 50))
        
        predictions = PredictionHistoryService.get_user_predictions(
            user=request.user,
            status=status_filter,
            disease_type=disease_type,
            limit=limit
        )
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest_predictions(self, request):
        """Get the latest 4 predictions for the current user"""
        predictions = PredictionHistoryService.get_user_predictions(
            user=request.user,
            limit=4
        )
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all_predictions(self, request):
        """Get all predictions for the current user"""
        status_filter = request.query_params.get('status')
        disease_type = request.query_params.get('disease_type')
        
        predictions = PredictionHistoryService.get_user_predictions(
            user=request.user,
            status=status_filter,
            disease_type=disease_type,
            limit=None  # No limit - get all
        )
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def admin_all_users_predictions(self, request):
        """Get all predictions for all users (admin only)"""
        # Check if user is admin/superuser
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_filter = request.query_params.get('status')
        disease_type = request.query_params.get('disease_type')
        user_id = request.query_params.get('user_id')
        limit = int(request.query_params.get('limit', 50))
        
        queryset = PredictionHistory.objects.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if disease_type:
            queryset = queryset.filter(disease_type=disease_type)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if limit:
            predictions = queryset.order_by('-timestamp')[:limit]
        else:
            predictions = queryset.order_by('-timestamp')
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def admin_latest_all_users(self, request):
        """Get the latest 4 predictions for all users (admin only)"""
        # Check if user is admin/superuser
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        predictions = PredictionHistory.objects.order_by('-timestamp')[:4]
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get detailed prediction information for display"""
        try:
            prediction = self.get_object()
            from .serializers import PredictionDetailsSerializer
            serializer = PredictionDetailsSerializer(prediction)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update prediction status and reinforcement learning data"""
        try:
            prediction = self.get_object()
            
            prediction_status = request.data.get('status')
            actual_disease = request.data.get('actual_disease')
            medicine_prescribed = request.data.get('medicine_prescribed')
            cost_of_treatment = request.data.get('cost_of_treatment')
            doctor_notes = request.data.get('doctor_notes')
            
            # Convert cost to Decimal if provided
            if cost_of_treatment is not None:
                cost_of_treatment = Decimal(str(cost_of_treatment))
            
            updated_prediction = PredictionHistoryService.update_prediction_status(
                prediction_id=prediction.prediction_id,
                status=prediction_status,
                actual_disease=actual_disease,
                medicine_prescribed=medicine_prescribed,
                cost_of_treatment=cost_of_treatment,
                doctor_notes=doctor_notes
            )
            
            serializer = self.get_serializer(updated_prediction)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def add_feedback(self, request, pk=None):
        """Add feedback to a prediction"""
        try:
            prediction = self.get_object()
            
            feedback_type = request.data.get('feedback_type')
            feedback_text = request.data.get('feedback_text')
            rating = request.data.get('rating')
            doctor_notes = request.data.get('doctor_notes')
            patient_outcome = request.data.get('patient_outcome')
            
            feedback = PredictionFeedbackService.add_feedback(
                prediction=prediction,
                feedback_type=feedback_type,
                feedback_text=feedback_text,
                provided_by=request.user,
                rating=rating,
                doctor_notes=doctor_notes,
                patient_outcome=patient_outcome
            )
            
            serializer = PredictionFeedbackSerializer(feedback)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def trigger_reinforcement_learning(self, request):
        """Explicitly trigger reinforcement learning training"""
        try:
            disease_type = request.data.get('disease_type')
            min_confidence = float(request.data.get('min_confidence', 0.0))
            force_retrain = request.data.get('force_retrain', False)
            
            result = PredictionHistoryService.trigger_reinforcement_learning(
                disease_type=disease_type,
                min_confidence=min_confidence,
                force_retrain=force_retrain
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReinforcementLearningViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for reinforcement learning data
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReinforcementLearningDataSerializer
    queryset = ReinforcementLearningData.objects.all()
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get learning statistics for dashboard"""
        try:
            disease_type = request.query_params.get('disease_type')
            days_back = int(request.query_params.get('days_back', 30))
            
            stats = ReinforcementLearningService.get_learning_statistics(
                disease_type=disease_type,
                days_back=days_back
            )
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def aggregate_data(self, request):
        """Manually trigger data aggregation"""
        try:
            period_start_str = request.data.get('period_start')
            period_end_str = request.data.get('period_end')
            disease_type = request.data.get('disease_type')
            
            # Convert date strings to date objects
            period_start = datetime.strptime(period_start_str, '%Y-%m-%d').date()
            period_end = datetime.strptime(period_end_str, '%Y-%m-%d').date()
            
            # Aggregate data
            aggregated_data = ReinforcementLearningService.aggregate_learning_data(
                period_start=period_start,
                period_end=period_end,
                disease_type=disease_type
            )
            
            # Save aggregated data
            saved_data = ReinforcementLearningService.save_aggregated_data(aggregated_data)
            
            serializer = self.get_serializer(saved_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ModelTrainingSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing model training sessions
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ModelTrainingSessionSerializer
    
    def get_queryset(self):
        """Filter training sessions by current user"""
        return ModelTrainingSession.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def user_sessions(self, request):
        """Get training sessions for the current user"""
        limit = int(request.query_params.get('limit', 50))
        
        sessions = ReinforcementLearningService.get_user_training_sessions(
            user=request.user,
            limit=limit
        )
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest_session(self, request):
        """Get the latest training session for the current user"""
        session = ReinforcementLearningService.get_latest_user_training_session(
            user=request.user
        )
        
        if session:
            serializer = self.get_serializer(session)
            return Response(serializer.data)
        else:
            return Response(
                {'message': 'No training session found for the current user'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update training session status"""
        try:
            session = self.get_object()
            
            status = request.data.get('status')
            training_accuracy = request.data.get('training_accuracy')
            validation_accuracy = request.data.get('validation_accuracy')
            test_accuracy = request.data.get('test_accuracy')
            model_file_path = request.data.get('model_file_path')
            scaler_file_path = request.data.get('scaler_file_path')
            training_logs = request.data.get('training_logs')
            error_message = request.data.get('error_message')
            
            updated_session = ReinforcementLearningService.update_training_session(
                session_id=session.session_id,
                status=status,
                training_accuracy=training_accuracy,
                validation_accuracy=validation_accuracy,
                test_accuracy=test_accuracy,
                model_file_path=model_file_path,
                scaler_file_path=scaler_file_path,
                training_logs=training_logs,
                error_message=error_message
            )
            
            serializer = self.get_serializer(updated_session)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PredictionFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for prediction feedback
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PredictionFeedbackSerializer
    
    def get_queryset(self):
        """Filter feedback by current user"""
        return PredictionFeedback.objects.filter(provided_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def prediction_feedbacks(self, request):
        """Get feedback for a specific prediction"""
        prediction_id = request.query_params.get('prediction_id')
        
        if not prediction_id:
            return Response(
                {'error': 'prediction_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            prediction = PredictionHistory.objects.get(prediction_id=prediction_id)
            feedbacks = PredictionFeedbackService.get_prediction_feedbacks(prediction)
            
            serializer = self.get_serializer(feedbacks, many=True)
            return Response(serializer.data)
            
        except PredictionHistory.DoesNotExist:
            return Response(
                {'error': 'Prediction not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prediction_analysis(request):
    """
    Get comprehensive prediction analysis data for the current user
    """
    try:
        # Get user's prediction statistics
        user_predictions = PredictionHistory.objects.filter(user=request.user)
        
        # Basic statistics
        total_predictions = user_predictions.count()
        pending_predictions = user_predictions.filter(status='pending').count()
        confirmed_predictions = user_predictions.filter(status='confirmed').count()
        corrected_predictions = user_predictions.filter(status='corrected').count()
        discarded_predictions = user_predictions.filter(status='discarded').count()
        
        # Calculate success rate
        processed_predictions = confirmed_predictions + corrected_predictions + discarded_predictions
        success_rate = (confirmed_predictions / processed_predictions * 100) if processed_predictions > 0 else 0.0
        
        # Get recent predictions (last 10)
        recent_predictions = user_predictions.order_by('-timestamp')[:10]
        
        # Get latest 4 predictions
        latest_predictions = user_predictions.order_by('-timestamp')[:4]
        
        # Disease type analysis
        disease_analysis = {}
        for prediction in user_predictions:
            disease = prediction.disease_type
            if disease not in disease_analysis:
                disease_analysis[disease] = {
                    'total': 0,
                    'confirmed': 0,
                    'corrected': 0,
                    'discarded': 0,
                    'pending': 0,
                    'avg_confidence': 0.0
                }
            disease_analysis[disease]['total'] += 1
            disease_analysis[disease][prediction.status] += 1
            disease_analysis[disease]['avg_confidence'] += prediction.confidence_score
        
        # Calculate average confidence for each disease
        for disease in disease_analysis:
            if disease_analysis[disease]['total'] > 0:
                disease_analysis[disease]['avg_confidence'] /= disease_analysis[disease]['total']
                disease_analysis[disease]['success_rate'] = (
                    disease_analysis[disease]['confirmed'] / 
                    (disease_analysis[disease]['confirmed'] + disease_analysis[disease]['corrected'] + disease_analysis[disease]['discarded']) * 100
                ) if (disease_analysis[disease]['confirmed'] + disease_analysis[disease]['corrected'] + disease_analysis[disease]['discarded']) > 0 else 0.0
        
        # Monthly trends (last 6 months)
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_trends = {}
        
        for i in range(6):
            month_start = six_months_ago + timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            month_key = month_start.strftime('%Y-%m')
            
            month_predictions = user_predictions.filter(
                timestamp__gte=month_start,
                timestamp__lt=month_end
            )
            
            monthly_trends[month_key] = {
                'total': month_predictions.count(),
                'confirmed': month_predictions.filter(status='confirmed').count(),
                'corrected': month_predictions.filter(status='corrected').count(),
                'discarded': month_predictions.filter(status='discarded').count(),
                'pending': month_predictions.filter(status='pending').count(),
                'avg_confidence': month_predictions.aggregate(avg=models.Avg('confidence_score'))['avg'] or 0.0
            }
        
        # Learning statistics
        learning_stats = ReinforcementLearningService.get_learning_statistics(days_back=30)
        
        # Performance insights
        performance_insights = []
        if total_predictions > 0:
            if success_rate >= 80:
                performance_insights.append("Excellent prediction accuracy - model performing very well")
            elif success_rate >= 60:
                performance_insights.append("Good prediction accuracy - model performing well")
            elif success_rate >= 40:
                performance_insights.append("Moderate prediction accuracy - consider model improvements")
            else:
                performance_insights.append("Low prediction accuracy - model needs significant improvements")
        
        if pending_predictions > total_predictions * 0.3:
            performance_insights.append("High number of pending predictions - consider following up on outcomes")
        
        # Top performing disease types
        top_diseases = sorted(
            disease_analysis.items(), 
            key=lambda x: x[1]['success_rate'], 
            reverse=True
        )[:3]
        
        analysis_data = {
            'summary': {
                'total_predictions': total_predictions,
                'pending_predictions': pending_predictions,
                'confirmed_predictions': confirmed_predictions,
                'corrected_predictions': corrected_predictions,
                'discarded_predictions': discarded_predictions,
                'success_rate': round(success_rate, 2),
                'processing_rate': round((processed_predictions / total_predictions * 100) if total_predictions > 0 else 0.0, 2)
            },
            'recent_predictions': PredictionHistorySerializer(recent_predictions, many=True).data,
            'latest_predictions': PredictionHistorySerializer(latest_predictions, many=True).data,
            'disease_analysis': disease_analysis,
            'monthly_trends': monthly_trends,
            'top_performing_diseases': [
                {
                    'disease': disease,
                    'success_rate': data['success_rate'],
                    'total_predictions': data['total'],
                    'avg_confidence': round(data['avg_confidence'], 3)
                }
                for disease, data in top_diseases
            ],
            'performance_insights': performance_insights,
            'learning_statistics': learning_stats
        }
        
        return Response(analysis_data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_reinforcement_data(request):
    """
    Submit reinforcement learning data for a prediction
    """
    try:
        prediction_id = request.data.get('prediction_id')
        status = request.data.get('status')
        actual_disease = request.data.get('actual_disease')
        medicine_prescribed = request.data.get('medicine_prescribed')
        cost_of_treatment = request.data.get('cost_of_treatment')
        doctor_notes = request.data.get('doctor_notes')
        
        # Validate required fields
        if not prediction_id or not status:
            return Response(
                {'error': 'prediction_id and status are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert cost to Decimal if provided
        if cost_of_treatment is not None:
            cost_of_treatment = Decimal(str(cost_of_treatment))
        
        # Update prediction
        updated_prediction = PredictionHistoryService.update_prediction_status(
            prediction_id=prediction_id,
            status=status,
            actual_disease=actual_disease,
            medicine_prescribed=medicine_prescribed,
            cost_of_treatment=cost_of_treatment,
            doctor_notes=doctor_notes
        )
        
        serializer = PredictionHistorySerializer(updated_prediction)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


class ArticleTagViewSet(ListCreateAPIView):
    """
    API endpoint for viewing and creating article tags.
    - GET: List all tags (public access)
    - POST: Create new tag (admin only)
    """
    queryset = ArticleTag.objects.all().annotate(
        article_count=Count('articles')
    ).order_by('name')
    serializer_class = ArticleTagSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'article_count', 'created_at']
    ordering = ['name']


class ArticleTagDetailView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for viewing, updating, and deleting individual article tags.
    - GET: View tag details (public access)
    - PUT/PATCH: Update tag (admin only)
    - DELETE: Delete tag (admin only)
    """
    queryset = ArticleTag.objects.all()
    serializer_class = ArticleTagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'


class ArticleViewSet(ListCreateAPIView):
    """
    API endpoint for viewing and creating articles.
    - GET: List all articles (public access)
    - POST: Create new article (admin only)
    """
    queryset = Article.objects.filter(status='published').select_related().prefetch_related('tags')
    serializer_class = ArticleListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['article_type', 'status', 'is_featured', 'tags', 'author_name']
    search_fields = ['title', 'summary', 'content', 'author_name', 'author_affiliation']
    ordering_fields = ['publication_date', 'created_at', 'views_count', 'likes_count', 'comments_count']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        """Custom queryset with filtering"""
        queryset = super().get_queryset()
        
        # Filter by tag if specified
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__name=tag)
        
        # Filter by article type if specified
        article_type = self.request.query_params.get('article_type', None)
        if article_type:
            queryset = queryset.filter(article_type=article_type)
        
        # Filter by featured articles if specified
        featured = self.request.query_params.get('featured', None)
        if featured is not None:
            featured_bool = featured.lower() == 'true'
            queryset = queryset.filter(is_featured=featured_bool)
        
        return queryset.distinct()


class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for viewing, updating, and deleting individual articles.
    - GET: View article details (public access)
    - PUT/PATCH: Update article (admin only)
    - DELETE: Delete article (admin only)
    """
    queryset = Article.objects.select_related().prefetch_related(
        'tags', 'comments', 'likes', 'bookmarks', 'views'
    )
    serializer_class = ArticleDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to track article views"""
        article = self.get_object()
        
        # Track view
        self.track_article_view(article, request)
        
        # Increment view count
        article.increment_views()
        
        return super().retrieve(request, *args, **kwargs)
    
    def track_article_view(self, article, request):
        """Track article view for analytics"""
        try:
            # Get user info
            user = request.user if request.user.is_authenticated else None
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            session_id = request.session.session_key
            
            # Create view record
            ArticleView.objects.create(
                article=article,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error tracking article view: {e}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ResearchPaperViewSet(ListCreateAPIView):
    """
    API endpoint for viewing and creating research papers.
    - GET: List all research papers (public access)
    - POST: Create new research paper (admin only)
    """
    queryset = ResearchPaper.objects.select_related('article').prefetch_related('article__tags')
    serializer_class = ResearchPaperListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['paper_type', 'journal_name', 'research_quality_score']
    search_fields = ['abstract', 'key_findings', 'conclusions', 'article__title', 'article__author_name']
    ordering_fields = ['citation_count', 'research_quality_score', 'created_at', 'article__publication_date']
    ordering = ['-article__publication_date']
    
    def get_queryset(self):
        """Custom queryset with filtering"""
        queryset = super().get_queryset()
        
        # Filter by paper type if specified
        paper_type = self.request.query_params.get('paper_type', None)
        if paper_type:
            queryset = queryset.filter(paper_type=paper_type)
        
        # Filter by quality score if specified
        min_quality = self.request.query_params.get('min_quality', None)
        if min_quality:
            try:
                min_quality = float(min_quality)
                queryset = queryset.filter(research_quality_score__gte=min_quality)
            except ValueError:
                pass
        
        return queryset


class ResearchPaperDetailView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for viewing, updating, and deleting individual research papers.
    - GET: View research paper details (public access)
    - PUT/PATCH: Update research paper (admin only)
    - DELETE: Delete research paper (admin only)
    """
    queryset = ResearchPaper.objects.select_related('article').prefetch_related('article__tags')
    serializer_class = ResearchPaperSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'


class ArticleCommentViewSet(ListCreateAPIView):
    """
    API endpoint for viewing and creating article comments.
    - GET: List comments for an article (public access)
    - POST: Create new comment (authenticated users only)
    """
    serializer_class = ArticleCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get comments for a specific article"""
        article_id = self.kwargs.get('article_id')
        return ArticleComment.objects.filter(
            article_id=article_id,
            is_approved=True
        ).select_related('user', 'parent_comment').prefetch_related('replies')
    
    def perform_create(self, serializer):
        """Set the user and article when creating a comment"""
        article_id = self.kwargs.get('article_id')
        article = get_object_or_404(Article, id=article_id)
        serializer.save(user=self.request.user, article=article)
        
        # Increment article comment count
        article.increment_comments()


class ArticleLikeView(APIView):
    """
    API endpoint for liking/unliking articles.
    - POST: Like an article (authenticated users only)
    - DELETE: Unlike an article (authenticated users only)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, article_id):
        """Like an article"""
        try:
            article = get_object_or_404(Article, id=article_id)
            
            # Check if user already liked the article
            like, created = ArticleLike.objects.get_or_create(
                user=request.user,
                article=article
            )
            
            if created:
                # Increment article like count
                article.increment_likes()
                return Response({
                    'message': 'Article liked successfully',
                    'liked': True
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Article already liked',
                    'liked': True
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, article_id):
        """Unlike an article"""
        try:
            article = get_object_or_404(Article, id=article_id)
            
            # Remove like if it exists
            like = ArticleLike.objects.filter(
                user=request.user,
                article=article
            ).first()
            
            if like:
                like.delete()
                # Decrement article like count
                article.likes_count = max(0, article.likes_count - 1)
                article.save(update_fields=['likes_count'])
                
                return Response({
                    'message': 'Article unliked successfully',
                    'liked': False
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Article not liked',
                    'liked': False
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ArticleBookmarkView(APIView):
    """
    API endpoint for bookmarking/unbookmarking articles.
    - POST: Bookmark an article (authenticated users only)
    - DELETE: Remove bookmark (authenticated users only)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, article_id):
        """Bookmark an article"""
        try:
            article = get_object_or_404(Article, id=article_id)
            
            # Check if user already bookmarked the article
            bookmark, created = ArticleBookmark.objects.get_or_create(
                user=request.user,
                article=article
            )
            
            if created:
                # Increment article bookmark count
                article.increment_bookmarks()
                return Response({
                    'message': 'Article bookmarked successfully',
                    'bookmarked': True
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Article already bookmarked',
                    'bookmarked': True
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, article_id):
        """Remove bookmark"""
        try:
            article = get_object_or_404(Article, id=article_id)
            
            # Remove bookmark if it exists
            bookmark = ArticleBookmark.objects.filter(
                user=request.user,
                article=article
            ).first()
            
            if bookmark:
                bookmark.delete()
                # Decrement article bookmark count
                article.bookmarks_count = max(0, article.bookmarks_count - 1)
                article.save(update_fields=['bookmarks_count'])
                
                return Response({
                    'message': 'Bookmark removed successfully',
                    'bookmarked': False
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Article not bookmarked',
                    'bookmarked': False
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': str(e)}
            , status=status.HTTP_400_BAD_REQUEST
            )


class UserBookmarksView(APIView):
    """
    API endpoint for viewing user's bookmarked articles.
    - GET: List user's bookmarks (authenticated users only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's bookmarked articles"""
        bookmarks = ArticleBookmark.objects.filter(
            user=request.user
        ).select_related('article').prefetch_related('article__tags').order_by('-created_at')
        
        # Serialize the articles from bookmarks
        articles = [bookmark.article for bookmark in bookmarks]
        serializer = ArticleListSerializer(articles, many=True)
        
        return Response({
            'bookmarks': serializer.data,
            'count': len(articles)
        }, status=status.HTTP_200_OK)


class FeaturedArticlesView(APIView):
    """
    API endpoint for viewing featured articles.
    - GET: List featured articles (public access)
    """
    def get(self, request):
        """Get featured articles"""
        featured_articles = Article.objects.filter(
            status='published',
            is_featured=True
        ).select_related().prefetch_related('tags').order_by('-publication_date')[:10]
        
        serializer = ArticleListSerializer(featured_articles, many=True)
        
        return Response({
            'featured_articles': serializer.data,
            'count': len(featured_articles)
        }, status=status.HTTP_200_OK)


class ArticleSearchView(APIView):
    """
    API endpoint for searching articles.
    - GET: Search articles by query (public access)
    """
    def get(self, request):
        """Search articles by query"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({
                'error': 'Query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in title, summary, content, and author
        articles = Article.objects.filter(
            Q(status='published') &
            (Q(title__icontains=query) |
             Q(summary__icontains=query) |
             Q(content__icontains=query) |
             Q(author_name__icontains=query) |
             Q(tags__name__icontains=query))
        ).select_related().prefetch_related('tags').distinct().order_by('-publication_date')
        
        serializer = ArticleListSerializer(articles, many=True)
        
        return Response({
            'search_results': serializer.data,
            'query': query,
            'count': len(articles)
        }, status=status.HTTP_200_OK)
