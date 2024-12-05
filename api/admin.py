from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(ESP32)
class ESP32Admin(admin.ModelAdmin):
    list_display = ("id", "user", "code")
    search_fields = ("code", "user")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "datetime_created", "individual","active")
    list_filter = ("active", "individual")
    search_fields = ("code",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "level", "datetime_created", "active")
    list_filter = ("room", "level", "active")


@admin.register(UserRegistration)
class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "get_username", "esp32", "datetime_registration")
    list_filter = ("esp32", "game",)

    @admin.display(description='Username', ordering='esp32__user__username')
    def get_username(self, obj):
        return obj.esp32.user.username
