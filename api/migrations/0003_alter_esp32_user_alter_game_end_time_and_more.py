# Generated by Django 5.1.4 on 2024-12-09 22:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_room_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='esp32',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
        migrations.AlterField(
            model_name='game',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha & Hora de Fin'),
        ),
        migrations.AlterField(
            model_name='game',
            name='sequence',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Secuencia'),
        ),
    ]
