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
    path('', include(router.urls)),
    path('esp32/game/info/<str:code>', esp32_game_info),
    path('room/create', create_room),
    path('room/join', join_room),
    path('room/close', close_room),
    path('esp32/all/<int:user_id>', get_esp32_list_from_user),
    path('game/start/<int:game_id>', start_game),
    # path('game/leaderboard/<int:game_id>', game_leaderboard),
]