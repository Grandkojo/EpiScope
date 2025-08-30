#!/usr/bin/env python3
"""
Prediction History and Reinforcement Learning Service

This service handles:
1. Creating and managing prediction history records
2. Processing reinforcement learning data
3. Updating prediction statuses
4. Aggregating data for model training
5. Calculating learning scores and metrics
"""

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Avg, Count, Sum
from django.contrib.auth import get_user_model

from .models import (
    PredictionHistory, 
    ReinforcementLearningData, 
    ModelTrainingSession,
    PredictionFeedback
)

User = get_user_model()
logger = logging.getLogger(__name__)


class PredictionHistoryService:
    """
    Service class for managing prediction history and reinforcement learning
    """
    
    @staticmethod
    def create_prediction(
        user: User,
        age: int,
        gender: str,
        locality: str,
        schedule_date: datetime.date,
        pregnant_patient: bool = False,
        nhia_patient: bool = False,
        vertex_ai_enabled: bool = False,
        disease_type: str = "",
        symptoms_description: str = "",
        predicted_disease: str = "",
        confidence_score: float = 0.0,
        hospital_name: str = None,
        ai_insights: List[str] = None
    ) -> PredictionHistory:
        """
        Create a new prediction history record
        """
        try:
            prediction = PredictionHistory.objects.create(
                user=user,
                age=age,
                gender=gender,
                locality=locality,
                schedule_date=schedule_date,
                pregnant_patient=pregnant_patient,
                nhia_patient=nhia_patient,
                vertex_ai_enabled=vertex_ai_enabled,
                disease_type=disease_type,
                symptoms_description=symptoms_description,
                predicted_disease=predicted_disease,
                confidence_score=confidence_score,
                hospital_name=hospital_name,
                ai_insights=ai_insights
            )
            
            logger.info(f"Created prediction {prediction.prediction_id} for user {user.username}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error creating prediction: {str(e)}")
            raise
    
    @staticmethod
    def update_prediction_status(
        prediction_id: str,
        status: str,
        actual_disease: str = None,
        medicine_prescribed: str = None,
        cost_of_treatment: Decimal = None,
        doctor_notes: str = None
    ) -> PredictionHistory:
        """
        Update prediction status and reinforcement learning data (without triggering training)
        """
        try:
            with transaction.atomic():
                prediction = PredictionHistory.objects.select_for_update().get(
                    prediction_id=prediction_id
                )
                
                # Update status and actual disease
                prediction.status = status
                if actual_disease:
                    prediction.actual_disease = actual_disease
                
                # Update reinforcement learning data
                if medicine_prescribed:
                    prediction.medicine_prescribed = medicine_prescribed
                if cost_of_treatment is not None:
                    prediction.cost_of_treatment = cost_of_treatment
                if doctor_notes:
                    prediction.doctor_notes = doctor_notes
                
                # Set feedback timestamp
                prediction.feedback_timestamp = timezone.now()
                
                # Calculate learning score if reinforcement data is provided (but don't trigger training)
                if prediction.is_learning_ready:
                    prediction.update_learning_score()
                
                prediction.save()
                
                logger.info(f"Updated prediction {prediction_id} status to {status} (reinforcement learning not triggered)")
                return prediction
                
        except PredictionHistory.DoesNotExist:
            logger.error(f"Prediction {prediction_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error updating prediction {prediction_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_user_predictions(
        user: User,
        status: str = None,
        disease_type: str = None,
        limit: int = 50
    ) -> List[PredictionHistory]:
        """
        Get predictions for a specific user with optional filters
        """
        queryset = PredictionHistory.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
        if disease_type:
            queryset = queryset.filter(disease_type=disease_type)
        
        # Apply limit only if specified
        if limit is not None:
            return queryset.order_by('-timestamp')[:limit]
        else:
            return queryset.order_by('-timestamp')
    
    @staticmethod
    def get_prediction_by_id(prediction_id: str) -> Optional[PredictionHistory]:
        """
        Get a specific prediction by ID
        """
        try:
            return PredictionHistory.objects.get(prediction_id=prediction_id)
        except PredictionHistory.DoesNotExist:
            return None
    
    @staticmethod
    def get_predictions_for_learning(
        disease_type: str = None,
        min_confidence: float = 0.0,
        limit: int = 1000
    ) -> List[PredictionHistory]:
        """
        Get predictions that are ready for reinforcement learning
        """
        queryset = PredictionHistory.objects.filter(
            Q(status='confirmed') | Q(status='corrected'),
            medicine_prescribed__isnull=False,
            cost_of_treatment__isnull=False,
            confidence_score__gte=min_confidence
        )
        
        if disease_type:
            queryset = queryset.filter(disease_type=disease_type)
        
        return queryset.order_by('-feedback_timestamp')[:limit]


class ReinforcementLearningService:
    """
    Service class for handling reinforcement learning data aggregation and model training
    """
    
    @staticmethod
    def aggregate_learning_data(
        period_start: datetime.date,
        period_end: datetime.date,
        disease_type: str = None
    ) -> Dict[str, Any]:
        """
        Aggregate reinforcement learning data for a specific period
        """
        try:
            # Get predictions for the period
            predictions = PredictionHistory.objects.filter(
                timestamp__date__gte=period_start,
                timestamp__date__lte=period_end,
                is_learning_ready=True
            )
            
            if disease_type:
                predictions = predictions.filter(disease_type=disease_type)
            
            # Calculate aggregated metrics
            total_predictions = predictions.count()
            confirmed_predictions = predictions.filter(status='confirmed').count()
            corrected_predictions = predictions.filter(status='corrected').count()
            discarded_predictions = predictions.filter(status='discarded').count()
            
            # Calculate averages
            avg_confidence = predictions.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0.0
            avg_learning_score = predictions.aggregate(Avg('model_learning_score'))['model_learning_score__avg'] or 0.0
            avg_cost = predictions.aggregate(Avg('cost_of_treatment'))['cost_of_treatment__avg'] or Decimal('0.0')
            
            # Analyze medicine patterns
            medicine_data = {}
            for pred in predictions:
                if pred.medicine_prescribed:
                    medicine = pred.medicine_prescribed.strip()
                    if medicine in medicine_data:
                        medicine_data[medicine] += 1
                    else:
                        medicine_data[medicine] = 1
            
            # Get most common medicines
            common_medicines = sorted(medicine_data.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Calculate model performance metrics
            if total_predictions > 0:
                model_accuracy = confirmed_predictions / total_predictions
                model_precision = confirmed_predictions / (confirmed_predictions + corrected_predictions) if (confirmed_predictions + corrected_predictions) > 0 else 0.0
                model_recall = confirmed_predictions / (confirmed_predictions + discarded_predictions) if (confirmed_predictions + discarded_predictions) > 0 else 0.0
                model_f1_score = 2 * (model_precision * model_recall) / (model_precision + model_recall) if (model_precision + model_recall) > 0 else 0.0
            else:
                model_accuracy = model_precision = model_recall = model_f1_score = 0.0
            
            return {
                'period_start': period_start,
                'period_end': period_end,
                'disease_type': disease_type,
                'total_predictions': total_predictions,
                'confirmed_predictions': confirmed_predictions,
                'corrected_predictions': corrected_predictions,
                'discarded_predictions': discarded_predictions,
                'avg_confidence_score': avg_confidence,
                'avg_learning_score': avg_learning_score,
                'avg_cost_of_treatment': avg_cost,
                'common_medicines': [med[0] for med in common_medicines],
                'medicine_frequency': dict(common_medicines),
                'model_accuracy': model_accuracy,
                'model_precision': model_precision,
                'model_recall': model_recall,
                'model_f1_score': model_f1_score
            }
            
        except Exception as e:
            logger.error(f"Error aggregating learning data: {str(e)}")
            raise
    
    @staticmethod
    def save_aggregated_data(aggregated_data: Dict[str, Any]) -> ReinforcementLearningData:
        """
        Save aggregated reinforcement learning data
        """
        try:
            # Check if data already exists for this period
            existing_data, created = ReinforcementLearningData.objects.get_or_create(
                period_start=aggregated_data['period_start'],
                period_end=aggregated_data['period_end'],
                disease_type=aggregated_data['disease_type'] or 'all',
                defaults=aggregated_data
            )
            
            if not created:
                # Update existing record
                for key, value in aggregated_data.items():
                    if hasattr(existing_data, key):
                        setattr(existing_data, key, value)
                existing_data.save()
            
            logger.info(f"{'Created' if created else 'Updated'} aggregated data for {aggregated_data['disease_type']} - {aggregated_data['period_start']} to {aggregated_data['period_end']}")
            return existing_data
            
        except Exception as e:
            logger.error(f"Error saving aggregated data: {str(e)}")
            raise
    
    @staticmethod
    def create_training_session(
        session_name: str,
        disease_type: str,
        model_type: str,
        training_parameters: Dict[str, Any],
        data_period_start: datetime.date,
        data_period_end: datetime.date,
        initiated_by: User = None
    ) -> ModelTrainingSession:
        """
        Create a new model training session
        """
        try:
            session = ModelTrainingSession.objects.create(
                session_name=session_name,
                disease_type=disease_type,
                model_type=model_type,
                training_parameters=training_parameters,
                data_period_start=data_period_start,
                data_period_end=data_period_end,
                initiated_by=initiated_by
            )
            
            logger.info(f"Created training session {session.session_id}: {session_name}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating training session: {str(e)}")
            raise
    
    @staticmethod
    def update_training_session(
        session_id: str,
        status: str,
        training_accuracy: float = None,
        validation_accuracy: float = None,
        test_accuracy: float = None,
        model_file_path: str = None,
        scaler_file_path: str = None,
        training_logs: str = None,
        error_message: str = None
    ) -> ModelTrainingSession:
        """
        Update training session with results
        """
        try:
            with transaction.atomic():
                session = ModelTrainingSession.objects.select_for_update().get(
                    session_id=session_id
                )
                
                session.status = status
                if training_accuracy is not None:
                    session.training_accuracy = training_accuracy
                if validation_accuracy is not None:
                    session.validation_accuracy = validation_accuracy
                if test_accuracy is not None:
                    session.test_accuracy = test_accuracy
                if model_file_path:
                    session.model_file_path = model_file_path
                if scaler_file_path:
                    session.scaler_file_path = scaler_file_path
                if training_logs:
                    session.training_logs = training_logs
                if error_message:
                    session.error_message = error_message
                
                if status in ['completed', 'failed']:
                    session.end_time = timezone.now()
                
                session.save()
                
                logger.info(f"Updated training session {session_id} status to {status}")
                return session
                
        except ModelTrainingSession.DoesNotExist:
            logger.error(f"Training session {session_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error updating training session {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_learning_statistics(
        disease_type: str = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get learning statistics for the dashboard
        """
        try:
            start_date = timezone.now().date() - timedelta(days=days_back)
            
            predictions = PredictionHistory.objects.filter(
                timestamp__date__gte=start_date
            )
            
            if disease_type:
                predictions = predictions.filter(disease_type=disease_type)
            
            # Overall statistics
            total_predictions = predictions.count()
            pending_predictions = predictions.filter(status='pending').count()
            confirmed_predictions = predictions.filter(status='confirmed').count()
            corrected_predictions = predictions.filter(status='corrected').count()
            discarded_predictions = predictions.filter(status='discarded').count()
            
            # Learning ready predictions
            learning_ready = predictions.filter(is_learning_ready=True).count()
            
            # Average metrics
            avg_confidence = predictions.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0.0
            avg_learning_score = predictions.filter(is_learning_ready=True).aggregate(
                Avg('model_learning_score')
            )['model_learning_score__avg'] or 0.0
            
            # Recent training sessions
            recent_sessions = ModelTrainingSession.objects.filter(
                start_time__date__gte=start_date
            ).order_by('-start_time')[:5]
            
            return {
                'total_predictions': total_predictions,
                'pending_predictions': pending_predictions,
                'confirmed_predictions': confirmed_predictions,
                'corrected_predictions': corrected_predictions,
                'discarded_predictions': discarded_predictions,
                'learning_ready_predictions': learning_ready,
                'avg_confidence_score': avg_confidence,
                'avg_learning_score': avg_learning_score,
                'processing_rate': (total_predictions - pending_predictions) / total_predictions * 100 if total_predictions > 0 else 0.0,
                'success_rate': confirmed_predictions / (confirmed_predictions + corrected_predictions + discarded_predictions) * 100 if (confirmed_predictions + corrected_predictions + discarded_predictions) > 0 else 0.0,
                'recent_training_sessions': [
                    {
                        'session_id': session.session_id,
                        'session_name': session.session_name,
                        'disease_type': session.disease_type,
                        'status': session.status,
                        'start_time': session.start_time,
                        'test_accuracy': session.test_accuracy
                    }
                    for session in recent_sessions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting learning statistics: {str(e)}")
            raise

    @staticmethod
    def trigger_reinforcement_learning(
        disease_type: str = None,
        min_confidence: float = 0.0,
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """
        Explicitly trigger reinforcement learning training
        """
        try:
            # Get predictions ready for learning
            learning_predictions = PredictionHistoryService.get_predictions_for_learning(
                disease_type=disease_type,
                min_confidence=min_confidence
            )
            
            if not learning_predictions:
                return {
                    'success': False,
                    'message': 'No predictions ready for reinforcement learning',
                    'predictions_count': 0
                }
            
            # Aggregate learning data
            from datetime import datetime, timedelta
            period_end = datetime.now().date()
            period_start = period_end - timedelta(days=30)  # Last 30 days
            
            aggregated_data = ReinforcementLearningService.aggregate_learning_data(
                period_start=period_start,
                period_end=period_end,
                disease_type=disease_type
            )
            
            # Save aggregated data
            saved_data = ReinforcementLearningService.save_aggregated_data(aggregated_data)
            
            # Create training session
            session_name = f"RL_Training_{disease_type or 'All'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            training_session = ReinforcementLearningService.create_training_session(
                session_name=session_name,
                disease_type=disease_type or 'all',
                model_type='XGBoost',
                training_parameters={
                    'min_confidence': min_confidence,
                    'force_retrain': force_retrain,
                    'learning_rate': 0.1,
                    'max_depth': 6,
                    'n_estimators': 100
                },
                data_period_start=period_start,
                data_period_end=period_end
            )
            
            logger.info(f"Triggered reinforcement learning for {len(learning_predictions)} predictions")
            
            return {
                'success': True,
                'message': f'Reinforcement learning triggered successfully',
                'predictions_count': len(learning_predictions),
                'training_session_id': training_session.session_id,
                'aggregated_data_id': saved_data.id,
                'disease_type': disease_type,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error triggering reinforcement learning: {str(e)}")
            return {
                'success': False,
                'message': f'Error triggering reinforcement learning: {str(e)}',
                'predictions_count': 0
            }


class PredictionFeedbackService:
    """
    Service class for handling prediction feedback
    """
    
    @staticmethod
    def add_feedback(
        prediction: PredictionHistory,
        feedback_type: str,
        feedback_text: str,
        provided_by: User,
        rating: int = None,
        doctor_notes: str = None,
        patient_outcome: str = None
    ) -> PredictionFeedback:
        """
        Add feedback to a prediction
        """
        try:
            feedback = PredictionFeedback.objects.create(
                prediction=prediction,
                feedback_type=feedback_type,
                feedback_text=feedback_text,
                provided_by=provided_by,
                rating=rating,
                doctor_notes=doctor_notes,
                patient_outcome=patient_outcome
            )
            
            logger.info(f"Added feedback to prediction {prediction.prediction_id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error adding feedback: {str(e)}")
            raise
    
    @staticmethod
    def get_prediction_feedbacks(prediction: PredictionHistory) -> List[PredictionFeedback]:
        """
        Get all feedback for a specific prediction
        """
        return PredictionFeedback.objects.filter(prediction=prediction).order_by('-timestamp')
    
    @staticmethod
    def get_user_feedbacks(user: User, limit: int = 50) -> List[PredictionFeedback]:
        """
        Get feedback provided by a specific user
        """
        return PredictionFeedback.objects.filter(provided_by=user).order_by('-timestamp')[:limit] 