from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from django.http import StreamingHttpResponse, JsonResponse
import time
from django.core.exceptions import ObjectDoesNotExist
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

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
        last_user_registration.refresh_from_db()

        time_remaining = game.get_time_remaining()

        if not game.active:
            # Envía un evento final al cliente y cierra la conexión
            yield "event: game_end\ndata: {\"message\": \"The game has ended.\"}\n\n"
            time.sleep(0.5)
            continue

        # Enviar datos del juego en curso
        resp = {
            'user_registration': last_user_registration.pk,
            'level': game.level,
            'active': game.active,
            'sequence': game.sequence.split('-')[last_user_registration.good_points + last_user_registration.bad_points],
        }
        yield f"data: {json.dumps(resp)}\n\n"  # Enviar respuesta en formato SSE
        time.sleep(.01)


@csrf_exempt
def game_leaderboard(request, game_id):
    """Vista que responde con Server-Sent Events para un ESP32."""
    try:
        # Validar que el ESP32 existe con el código proporcionado
        game = Game.objects.get(pk=game_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'No Game found with the provided code.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON body.'}, status=400)

    # Crear la respuesta con el flujo de eventos SSE
    response = StreamingHttpResponse(event_stream_game_leaderboard(game), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'  # Evitar caché para mantener actualizaciones en tiempo real
    return response


def event_stream_game_leaderboard(game:Game):
    """Genera un flujo continuo de eventos SSE mientras el juego esté activo."""

    # Mientras el juego esté activo, envía actualizaciones
    while True:
        # Actualiza el estado del objeto desde la base de datos
        game.refresh_from_db()
        sec = 2
        if game.level > 2:
            sec = 1

        user_registrations = UserRegistration.objects.filter(game=game).order_by("total")
        resp = [
            {
                'position' : i+1,
                'user' : {
                    'id' : user_registrations[i].esp32.user.pk,
                    'username' : user_registrations[i].esp32.user.username,
                    'ESP32' : user_registrations[i].esp32.code,
                },
                'good_points' : user_registrations[i].good_points,
                'bad_points' : user_registrations[i].bad_points,
                'total' : user_registrations[i].total,
                'avg_time_react' : user_registrations[i].avg_time_react,
            } for i in range(len(user_registrations))
        ]

        time_remaining = game.get_time_remaining()

        if not game.active:
            # Envía un evento final al cliente y cierra la conexión
            yield 'event: game_end\ndata: {"time_remaining": 0, "leaderboard" : ' + str(json.dumps(resp)) + '}\n\n'
            break   
    
        yield 'data: {"time_remaining": ' + str(time_remaining) + ', "leaderboard" : ' + str(json.dumps(resp)) + '}\n\n'
        time.sleep(sec)


@csrf_exempt
def create_room(request):
    if request.method != "POST":
        return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)

    try:
        # Parsear el cuerpo de la solicitud como JSON
        body = json.loads(request.body)
        user_id = body.get("user_id")
        individual = body.get("individual")
        level = body.get("level")

    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON body.'}, status=400)

    # Validar que los parámetros requeridos estén presentes
    if not user_id or individual is None:
        return JsonResponse({'message': 'Invalid BODY for request. Missing user_id or individual.'}, status=400)

    try:
        # Validar que el usuario existe con el user_id proporcionado
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User does not exist.'}, status=400)
    
    room = Room.objects.filter(user=user, active=True)
    if (room):
        return JsonResponse({'message': 'User can only have one active room'}, status=400)

    # Crear la sala (Room) con los datos proporcionados
    room = Room.objects.create(individual=individual, user=user)
    game = Game.objects.create(room=room, level=level)

    # Devolver la respuesta con la información de la sala creada
    return JsonResponse({
        'id': room.pk,
        'individual': room.individual,
        'active': room.active,
        'creator': {
            'id': room.user.pk,
            'username': room.user.username
        },
        'game_created' : {
            'id' : game.pk,
            'level' : game.level,
            'created_at' : game.datetime_created,
        }
    }, status=201)



@csrf_exempt
def join_room(request):
    if request.method != "POST":
        return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)
    
    try:
        # Parsear el cuerpo de la solicitud como JSON
        body = json.loads(request.body)
        esp32_id = body.get("esp32_id")
        room_id = body.get("room_id")
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON body.'}, status=400)

    try:
        esp32 = ESP32.objects.get(id=esp32_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'ESP32 does not exist'}, status=404)
    
    try:
        room = Room.objects.get(id=room_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'Room does not exist'}, status=404)

    # Verificar si hay un juego asociado con la sala
    last_game = Game.objects.filter(room=room).order_by('-datetime_created').first()
    if not last_game:
        return JsonResponse({'message': 'No games found for the specified room.'}, status=404)

    # Registrar al usuario en el juego
    user_reg = UserRegistration.objects.create(esp32=esp32, game=last_game)
    return JsonResponse({
        'game_registered': {
            'id' : last_game.pk,
            'level': last_game.level,
            'room': last_game.room.pk
        },
    })


@csrf_exempt
def close_room(request):
    if request.method != "POST":
        return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)
    try:
        # Parsear el cuerpo de la solicitud como JSON
        body = json.loads(request.body)
        room_id = body.get("room_id")
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON body.'}, status=400)

    try:
        room = Room.objects.get(id=room_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message' : 'Room does not exist'})
    
    room.active=False
    room.save()
    games = Game.objects.filter(room=room)
    if games.exists():
        games.update(active = False)

    return JsonResponse({
        'message' : 'success'
    }, status=200)
    

@csrf_exempt
def get_esp32_list_from_user(request, user_id:int):
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({"message" : "User does not exist"}, status=400)

    esp32_list = list(ESP32.objects.filter(user=user))
    resp = {'data': [{
        'id' : esp32.pk,
        'code' : esp32.code,
        'user' : {
            'id' : esp32.user.pk,
            'username' : esp32.user.username,
        }
    } for esp32 in esp32_list]}
    return JsonResponse(resp, status=200)

@csrf_exempt
def start_game(request, game_id):
    if request.method != 'PUT':
        return JsonResponse({'message': 'Only PUT method is allowed.'}, status=405)

    try:
        game = Game.objects.get(pk=game_id)
    except ObjectDoesNotExist:
        return JsonResponse({"message" : "Game does not exist"}, status=400)
    
    game.begin_time = datetime.now()
    game.save()  

    return JsonResponse({
        "message": "Game started successfully",
        "game_id": game.pk,
        "begin_time": game.begin_time.isoformat(),  # Devolver la hora en formato ISO 8601
        "end_time": game.end_time.isoformat(),  # Devolver la hora en formato ISO 8601
        "active": game.active,
    }, status=200)

@csrf_exempt
def update_data_game_esp32(request, user_registration_id:int):
    if request.method != "PUT":
        return JsonResponse({'message': 'Only PUT method is allowed.'}, status=405)
    
    try:
        # Parsear el cuerpo de la solicitud como JSON
        body = json.loads(request.body)
        point = body.get("point")
        react = body.get("react")

    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON body.'}, status=400)

    try:
        user_registration = UserRegistration.objects.get(pk=user_registration_id)
    except ObjectDoesNotExist:
        return JsonResponse({"message" : "User Registration does not exist"}, status=400)
    
    if point == 1:
        user_registration.good_points += 1
        user_registration.react_time_sum += react
        user_registration.avg_time_react = user_registration.react_time_sum / (user_registration.good_points)
    else:
        user_registration.bad_points += 1


    user_registration.save()

    return JsonResponse({
        'good_points' : user_registration.good_points,
        'bad_points': user_registration.bad_points,
    }, status=200)