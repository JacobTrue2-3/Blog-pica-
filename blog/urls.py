from django.urls import path

from .import views 


urlpatterns = [
    path('posts/', views.get_post_list, name="post_list"),
    path('posts/<int:post_id>/', views.get_post_detail, name="post_detail"),
    path('posts/add/', views.create_post, name="post_add"),
    path('posts/<int:post_id>/edit/', views.update_post, name="update_post"),
    path('posts/<int:post_id>/delete/', views.delete_post, name="remove_post"),
]
