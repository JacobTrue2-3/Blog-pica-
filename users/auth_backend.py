from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Добавляем проверку на пустое значение
        if username is None or password is None:
            return None
            
        try:
            # Добавляем регистронезависимый поиск и нормализацию
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Логируем попытку входа для отладки (опционально)
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Обработка случая, если найдено несколько пользователей
            # (может случиться при дубликатах email)
            user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
            
        # Проверяем пароль и возможность аутентификации
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None