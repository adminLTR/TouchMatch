python -m venv env

./env/Scripts/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver