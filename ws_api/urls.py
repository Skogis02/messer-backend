from django.urls import re_path
from .consumers import APIConsumer

websocket_urlpatterns = [
    re_path('ws/ws-api/', APIConsumer.as_asgi())
]