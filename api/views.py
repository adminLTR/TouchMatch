from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class ESP32ViewSet(viewsets.ModelViewSet):
    serializer_class = ESP32Serializer
    queryset = ESP32.objects.all()

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer
    queryset = Game.objects.all()

class UserRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = UserRegistrationSerializer
    queryset = UserRegistration.objects.all()