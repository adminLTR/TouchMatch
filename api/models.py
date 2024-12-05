from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ESP32(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Código")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")

    def __str__(self):
        return f"Placa {self.code}"
    
    class Meta:
        verbose_name = "ESP32"
        verbose_name_plural = "ESP32"

class Room(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    individual = models.BooleanField(default=True, verbose_name="Individual")
    active = models.BooleanField(default=True, verbose_name="Activa")

    def __str__(self):
        return f"Sala {self.code}"
    
    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

class Game(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Sala")
    level = models.PositiveSmallIntegerField(default=1, verbose_name="Nivel")
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    begin_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha & Hora de Inicio")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha & Hora de Fiin")
    active = models.BooleanField(default=False, verbose_name="Activo")
    sequence = models.CharField(max_length=300, null=True, blank=True, verbose_name="Secuencia")

    def __str__(self):
        return f"Partida {self.room.code}-{self.pk}"
    
    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"

class UserRegistration(models.Model):
    esp32 = models.ForeignKey(ESP32, on_delete=models.CASCADE, verbose_name="Placa")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="Partida")
    datetime_registration = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    good_points = models.PositiveSmallIntegerField(default=0, null=True, blank=True, verbose_name="Aciertos")
    bad_points = models.PositiveSmallIntegerField(default=0, null=True, blank=True, verbose_name="Errores")
    avg_time_react = models.FloatField(default=0, null=True, blank=True, verbose_name="Tiempo promedio de reacción")

    def __str__(self):
        return f"{self.esp32.user.username} ({self.esp32}) - {self.game}"
    
    class Meta:
        verbose_name = "Partida de usuario"
        verbose_name_plural = "Partidas de usuario"

