from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import *
from faker import Faker
import random
import string

class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        self.__clear()

        self.__seed_users(10)
        self.__seed_esp32(10)
        
        self.stdout.write(self.style.SUCCESS('Seeded database'))
        
    def __clear(self):
        self.stdout.write('Cleanning old data...')
        User.objects.all().delete()
        ESP32.objects.all().delete()
        Room.objects.all().delete()
        Game.objects.all().delete()
        UserRegistration.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted old data'))

    def __seed_users(self, num_users:int):
        faker = Faker()
        User.objects.create_superuser("admin", None, "1234")
        User.objects.create_user("Joa", None, "1234")
        User.objects.create_user("Asthri", None, "1234")
        for _ in range(num_users):
            User.objects.create_user(faker.user_name(), faker.email(), "1234")

    def __seed_esp32(self, num_esp32:int):
        ESP32.objects.create(
            user = User.objects.get(username="Joa"),
            code = "TM-8A1H"
        )
        ESP32.objects.create(
            user = User.objects.get(username="Asthri"),
            code = "TM-7D91"
        )
        existing_codes = {"TM-8A1H","TM-7D91"}
        users = User.objects.all()
        for _ in range(num_esp32):
            code = self.__generate_code(existing_codes)
            ESP32.objects.create(
                user = random.choice(users),
                code = code 
            )
        
    def __generate_code(self, existing_codes:set):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            code = 'TM-' + code
            if code not in existing_codes:
                existing_codes.add(code)
                return code