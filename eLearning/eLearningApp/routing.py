from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/global/", consumers.ChatConsumer.as_asgi()),
]