from django.urls import re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r'^ws/socket-server/(?P<esp32_code>[^/]+)/$', GameConsumer.as_asgi())
]

