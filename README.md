# Проект на Django

## Установка зависимостей
```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
## Приминиение миграций
```bash
python manage.py makemigrations (не обязательно)
python manage.py migrate
```
## Запуск сервера
```bash
python manage.py runserver
```
##
```bash
pip install django-extensions

INSTALLED_APPS = [
    ...
    'django_extensions',  # Без дефиса!
    ...
]

./manage.py shell_plus --print-sql
```