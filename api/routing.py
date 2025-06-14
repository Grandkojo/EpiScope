from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/epidemic/dashboard', consumers.EpidemicDashboardConsumer.as_asgi()),
]
