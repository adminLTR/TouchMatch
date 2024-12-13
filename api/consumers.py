import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import *

class GameConsumer(WebsocketConsumer):
    def connect(self):
        # When client connects
        self.accept()

        self.esp32_code = self.scope['url_route']['kwargs']['esp32_code']
        self.game_group_name = f'esp_room_{self.esp32_code}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.send(text_data=json.dumps({
            'type' : 'connection_established',
            'message' : 'You are now connected!'
        }))

    def disconnect(self, close_code):
        # Salir del grupo de WebSocket
        self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)

        point = data.get("point")
        react = data.get("react")

        esp32 = ESP32.objects.get(code=self.esp32_code)
        game = Game.objects.filter(room__user=esp32.user, active=True).first()
        if game:
            user_registration = UserRegistration.objects.get(esp32=esp32, game=game)
            if point == 1:
                user_registration.good_points += 1
                user_registration.react_time_sum += react
                user_registration.avg_time_react = user_registration.react_time_sum / (user_registration.good_points)
            else:
                user_registration.bad_points += 1

            user_registration.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'good_points' : user_registration.good_points,
                    'bad_points': user_registration.bad_points,
                }
            )

    def chat_message(self, event):
        good_points = event["good_points"]
        bad_points = event["bad_points"]
        self.send(text_data=json.dumps({
            'type' : 'chat',
            'good_points' : good_points,
            'bad_points' : bad_points
        }))