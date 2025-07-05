from django.urls import path

from .views import get_post_list, get_post_detail, get_post_add



urlpatterns = [
    path('posts/', get_post_list, name="post_list"),
    path('posts/<int:post_id>/', get_post_detail, name="post_detail"),
    path('posts/add/', get_post_add, name="post_add")
]
