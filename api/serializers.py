from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class ESP32Serializer(serializers.ModelSerializer):
    class Meta:
        model = ESP32
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        fields = "__all__"

