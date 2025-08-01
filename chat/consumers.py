import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatSession, ChatMessage
from src.models.disease_monitor import DiseaseMonitor
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class HealthChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None
        self.chat_session = None
        self.disease_monitor = None
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Create or get chat session
        self.chat_session = await self.get_or_create_chat_session()
        
        # Initialize disease monitor
        await self.initialize_disease_monitor()

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to EpiScope Health AI',
            'session_id': str(self.chat_session.id),
            'timestamp': timezone.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Update session end time
        if self.chat_session:
            await self.update_session_end_time()

    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')
            message_content = text_data_json.get('message', '')
            user_id = text_data_json.get('user_id', 'anonymous')

            if message_type == 'chat_message':
                await self.handle_chat_message(message_content, user_id)
            elif message_type == 'health_check':
                await self.handle_health_check()
            elif message_type == 'quick_question':
                await self.handle_quick_question(message_content, user_id)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred while processing your message'
            }))

    async def handle_chat_message(self, message_content, user_id):
        """Handle regular chat messages"""
        # Save user message
        user_message = await self.save_message('user', message_content, user_id)

        # Send user message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'role': 'user',
                'timestamp': timezone.now().isoformat(),
                'message_id': str(user_message.id)
            }
        )

        # Get AI response asynchronously
        asyncio.create_task(self.get_ai_response(message_content, user_id))

    async def handle_quick_question(self, question, user_id):
        """Handle quick question buttons"""
        await self.handle_chat_message(question, user_id)

    async def handle_health_check(self):
        """Handle health check requests"""
        health_status = await self.check_system_health()
        await self.send(text_data=json.dumps({
            'type': 'health_status',
            'status': health_status,
            'timestamp': timezone.now().isoformat()
        }))

    async def get_ai_response(self, user_message, user_id):
        """Get AI response using disease monitor and Vertex AI"""
        try:
            # Run AI processing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            ai_response = await loop.run_in_executor(
                self.executor,
                self.process_ai_response,
                user_message
            )

            # Save AI response
            ai_message = await self.save_message('assistant', ai_response, 'ai_assistant')

            # Send AI response to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_response,
                    'role': 'assistant',
                    'timestamp': timezone.now().isoformat(),
                    'message_id': str(ai_message.id)
                }
            )

        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            error_response = "I apologize, but I'm experiencing technical difficulties. Please try again later."
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': error_response,
                    'role': 'assistant',
                    'timestamp': timezone.now().isoformat(),
                    'message_id': 'error'
                }
            )

    def process_ai_response(self, user_message):
        """Process AI response using disease monitor and Vertex AI"""
        try:
            if not self.disease_monitor:
                return "I'm sorry, but the disease monitoring system is not available at the moment."

            # Analyze message for disease-related queries
            response = self.disease_monitor.analyze_chat_message(user_message)
            return response

        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
            return "I apologize, but I encountered an error while processing your request."

    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'role': event['role'],
            'timestamp': event['timestamp'],
            'message_id': event.get('message_id', '')
        }))

    @database_sync_to_async
    def get_or_create_chat_session(self):
        """Get or create a chat session"""
        session, created = ChatSession.objects.get_or_create(
            session_id=self.room_name,
            defaults={
                'start_time': timezone.now(),
                'status': 'active'
            }
        )
        return session

    @database_sync_to_async
    def save_message(self, role, content, user_id):
        """Save chat message to database"""
        return ChatMessage.objects.create(
            session=self.chat_session,
            role=role,
            content=content,
            user_id=user_id,
            timestamp=timezone.now()
        )

    @database_sync_to_async
    def update_session_end_time(self):
        """Update session end time"""
        self.chat_session.end_time = timezone.now()
        self.chat_session.status = 'ended'
        self.chat_session.save()

    async def initialize_disease_monitor(self):
        """Initialize disease monitor asynchronously"""
        try:
            # Initialize disease monitor in thread pool
            loop = asyncio.get_event_loop()
            self.disease_monitor = await loop.run_in_executor(
                self.executor,
                self._initialize_disease_monitor_sync
            )
        except Exception as e:
            logger.error(f"Error initializing disease monitor: {e}")
            self.disease_monitor = None

    def _initialize_disease_monitor_sync(self):
        """Synchronous initialization of disease monitor"""
        try:
            from django.conf import settings
            monitor = DiseaseMonitor(
                project_id=settings.VERTEX_AI_PROJECT_ID,
                location=settings.VERTEX_AI_LOCATION,
                model_name=settings.VERTEX_AI_MODEL_NAME
            )
            monitor.load_models(path='models')
            return monitor
        except Exception as e:
            logger.error(f"Error in disease monitor initialization: {e}")
            return None

    async def check_system_health(self):
        """Check system health status"""
        try:
            # Check disease monitor
            monitor_status = self.disease_monitor is not None
            
            # Check database connection
            db_status = await self.check_database_connection()
            
            # Check Vertex AI connection
            vertex_status = await self.check_vertex_ai_connection()

            return {
                'overall_status': 'healthy' if all([monitor_status, db_status, vertex_status]) else 'degraded',
                'components': {
                    'disease_monitor': monitor_status,
                    'database': db_status,
                    'vertex_ai': vertex_status
                },
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }

    @database_sync_to_async
    def check_database_connection(self):
        """Check database connection"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def check_vertex_ai_connection(self):
        """Check Vertex AI connection"""
        try:
            if not self.disease_monitor:
                return False
            
            # Test Vertex AI with a simple query
            loop = asyncio.get_event_loop()
            test_result = await loop.run_in_executor(
                self.executor,
                self._test_vertex_ai_sync
            )
            return test_result
        except Exception:
            return False

    def _test_vertex_ai_sync(self):
        """Synchronous Vertex AI test"""
        try:
            if self.disease_monitor and self.disease_monitor.vertex_client:
                # Simple test query
                response = self.disease_monitor.vertex_client.generate_content("Hello")
                return response is not None
            return False
        except Exception:
            return False 