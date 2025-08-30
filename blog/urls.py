from django.urls import path

from .import views 

app_name = 'blog'

urlpatterns = [    
    path('posts/', views.get_post_list, name="post_list"),    
    path('posts/add/', views.create_post, name="post_add"),
    path('posts/<int:post_id>/edit/', views.update_post, name="update_post"),
    path('posts/<int:post_id>/delete/', views.delete_post, name="remove_post"),
    path('posts/category/<slug:category_slug>/', views.get_category_posts, name="category_posts"),
    path('posts/<slug:post_slug>/', views.get_post_detail, name="post_detail"),
    path('posts/tag/<slug:tag_slug>/', views.get_tag_posts, name="tag_posts"),
    path('',views.main_page, name='main_page'),
]
