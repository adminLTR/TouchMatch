from django.db import models
from django.contrib.auth.models import User
import random

# Create your models here.
class ESP32(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")

    def __str__(self):
        return f"Placa {self.code}"
    
    class Meta:
        verbose_name = "ESP32"
        verbose_name_plural = "ESP32"

class Room(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    individual = models.BooleanField(default=True, verbose_name="Individual")
    active = models.BooleanField(default=True, verbose_name="Activa")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Sala #{self.pk}"
    
    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

class Game(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Sala")
    level = models.PositiveSmallIntegerField(default=1, verbose_name="Nivel")
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    begin_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha & Hora de Inicio")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Fecha & Hora de Fin")
    active = models.BooleanField(default=False, verbose_name="Activo")
    sequence = models.CharField(max_length=500, null=True, blank=True, verbose_name="Secuencia")

    def save(self, *args, **kwargs):
        if not self.pk:
            # 1212-2131-2112-1121-2121-1221-1232-1222-1233-1233
            seq = ''
            for i in range(100):
                master_color = random.randint(0, 2)
                master_num = random.randint(1, 2)
                color = random.randint(0, 2)
                num = random.randint(1, 2)
                if self.level == 1:
                    master_num = num = 2
                seq += f'{master_color}{master_num}{color}{num}-'
            self.sequence = seq
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Partida #{self.room.pk}-{self.pk}"
    
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

