from django.db import models
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User


User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name= "Заголовок") 
    text = models.TextField(verbose_name= "Текст")
    image = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True) 
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="Автор") #SET_NULL позволяет удалить пользователя, но посты останутся

    class Meta:
        verbose_name= "Пост"
        verbose_name_plural = "Посты"
        db_table = "blog_posts"

    def __str__(self):
        return self.title

