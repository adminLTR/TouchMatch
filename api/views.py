from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from django.http import StreamingHttpResponse, JsonResponse
import time
from django.core.exceptions import ObjectDoesNotExist
import json
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def esp32_game_info(request, code):
    """Vista que responde con Server-Sent Events para un ESP32."""
    # if request.method != "POST":
    #     return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)
    # code = request.GET.get("code")
    if not code:
        return JsonResponse({'message': 'No ESP32 code provided.'}, status=400)

    try:
        # Validar que el ESP32 existe con el código proporcionado
        esp32 = ESP32.objects.get(code=code)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'No ESP32 found with the provided code.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON body.'}, status=400)

    # Crear la respuesta con el flujo de eventos SSE
    response = StreamingHttpResponse(event_stream_esp32_game_info(esp32), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'  # Evitar caché para mantener actualizaciones en tiempo real
    return response


def event_stream_esp32_game_info(esp32):
    """Genera un flujo continuo de eventos SSE mientras el juego esté activo."""
    try:
        # Obtener el registro más reciente del usuario relacionado con el ESP32
        last_user_registration = UserRegistration.objects.filter(esp32=esp32).latest('datetime_registration')
    except ObjectDoesNotExist:
        yield "event: error\ndata: {\"message\": \"No user registration found for the ESP32.\"}\n\n"
        return

    try:
        # Obtener el juego relacionado con el último registro del usuario
        game = last_user_registration.game
    except ObjectDoesNotExist:
        yield "event: error\ndata: {\"message\": \"No game found for the user registration.\"}\n\n"
        return

    # Mientras el juego esté activo, envía actualizaciones
    while True:
        # Actualiza el estado del objeto desde la base de datos
        game.refresh_from_db()

        if not game.active:
            # Envía un evento final al cliente y cierra la conexión
            yield "event: game_end\ndata: {\"message\": \"The game has ended.\"}\n\n"
            break

        # Enviar datos del juego en curso
        resp = {
            'user_registration': last_user_registration.pk,
            'level': game.level,
            'active': game.active,
            'sequence': game.sequence,
        }
        yield f"data: {json.dumps(resp)}\n\n"  # Enviar respuesta en formato SSE
        time.sleep(0.5)
