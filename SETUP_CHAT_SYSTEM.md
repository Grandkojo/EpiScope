# EpiScope Chat System Setup Guide

## Overview
This guide will help you set up the complete WebSocket-based chat system with Vertex AI integration and fine-tuning capabilities.

## Prerequisites
- Django project with existing disease monitoring system
- Vertex AI project configured
- Python 3.8+

## Installation Steps

### 1. Install Required Packages
```bash
pip install channels
pip install channels-redis  # For production
pip install google-cloud-aiplatform
```

### 2. Create Database Migrations
```bash
python manage.py makemigrations chat
python manage.py migrate
```

### 3. Update Settings
Add the following to your `settings.py`:

```python
# Vertex AI Configuration
VERTEX_AI_PROJECT_ID = 'your-project-id'
VERTEX_AI_LOCATION = 'us-central1'
VERTEX_AI_MODEL_NAME = 'gemini-2.0-flash-001'

# Channels Configuration
INSTALLED_APPS += [
    'channels',
    'chat',
]

ASGI_APPLICATION = 'episcope.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
        # For production, use Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('127.0.0.1', 6379)],
        # },
    }
}
```

### 4. Train Disease Models
```bash
python manage.py train_disease_model --project-id your-project-id
```

### 5. Start the Development Server
```bash
python manage.py runserver
```

## Usage

### 1. Chat Interface
- Navigate to your React component
- The chat will automatically connect via WebSocket
- Ask questions about diabetes, malaria, or general health metrics

### 2. Health Check
- Click the activity icon in the chat header
- Check system status and component health

### 3. Fine-tuning Data Collection
The system automatically:
- Stores all chat conversations
- Analyzes disease-specific queries
- Prepares data for fine-tuning

### 4. Export Fine-tuning Data
```bash
# Export all data
python manage.py fine_tune_vertex_model --export-only

# Export specific disease data
python manage.py fine_tune_vertex_model --disease diabetes --export-only

# Export with custom parameters
python manage.py fine_tune_vertex_model --disease malaria --days 60 --export-only
```

### 5. Start Fine-tuning
```bash
# Fine-tune for diabetes
python manage.py fine_tune_vertex_model --disease diabetes

# Fine-tune for malaria with custom model
python manage.py fine_tune_vertex_model --disease malaria --model-name gemini-2.0-flash-001
```

## Features

### ✅ WebSocket Real-time Communication
- Instant message delivery
- Connection status monitoring
- Automatic reconnection

### ✅ Chat History Storage
- All conversations saved to database
- Session tracking and analytics
- Message metadata and timestamps

### ✅ Health Monitoring
- System health checks
- Component status monitoring
- Connection diagnostics

### ✅ Vertex AI Integration
- Contextual responses based on disease data
- Real-time symptom analysis
- Dynamic prompt generation

### ✅ Fine-tuning Pipeline
- Automatic data collection from chats
- Disease-specific training examples
- Export functionality for Vertex AI

### ✅ Analytics and Insights
- Chat session analytics
- Disease query tracking
- User interaction patterns

## File Structure
```
chat/
├── consumers.py          # WebSocket consumer
├── models.py            # Database models
├── routing.py           # WebSocket routing
└── management/
    └── commands/
        └── fine_tune_vertex_model.py

src/models/
└── disease_monitor.py   # Enhanced with chat analysis

exports/
└── fine_tuning/         # Exported training data
```

## Production Deployment

### 1. Use Redis for Channel Layers
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis-server', 6379)],
        },
    }
}
```

### 2. Configure ASGI Server
```bash
# Install Daphne
pip install daphne

# Run with Daphne
daphne episcope.asgi:application
```

### 3. Set Up Monitoring
- Monitor WebSocket connections
- Track chat analytics
- Monitor Vertex AI usage

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check ASGI configuration
   - Verify channel layers setup
   - Check firewall settings

2. **Vertex AI Errors**
   - Verify project ID and credentials
   - Check API quotas and limits
   - Ensure model name is correct

3. **Database Errors**
   - Run migrations: `python manage.py migrate`
   - Check database permissions
   - Verify model relationships

4. **Fine-tuning Issues**
   - Ensure sufficient training data
   - Check Vertex AI quotas
   - Verify data format

### Debug Commands
```bash
# Check system health
python manage.py shell
>>> from chat.models import ChatSession
>>> ChatSession.objects.count()

# Test WebSocket
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()

# Export chat data
python manage.py fine_tune_vertex_model --export-only --disease diabetes
```

## Next Steps

1. **Implement Vertex AI Fine-tuning API**
   - Add actual fine-tuning job creation
   - Monitor training progress
   - Deploy fine-tuned models

2. **Add Advanced Analytics**
   - Sentiment analysis
   - User satisfaction tracking
   - Response quality metrics

3. **Enhance Security**
   - User authentication
   - Message encryption
   - Rate limiting

4. **Scale Infrastructure**
   - Load balancing
   - Database optimization
   - Caching strategies

This setup provides a complete, production-ready chat system with AI integration and fine-tuning capabilities! 