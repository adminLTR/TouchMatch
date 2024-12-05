from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'esp32', ESP32ViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'games', GameViewSet)
router.register(r'user-registrations', UserRegistrationViewSet)

urlpatterns = [
    path('', include(router.urls))
]