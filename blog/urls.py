from django.urls import path

from .import views 

app_name = 'blog'

urlpatterns = [    
    path('posts/', views.PostListView.as_view(), name="post_list"),    
    path('posts/add/', views.PostCreateView.as_view(), name="post_add"),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name="update_post"),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name="remove_post"),
    path('posts/category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name="category_posts"),
    path('posts/<slug:post_slug>/', views.PostDetailView.as_view(), name="post_detail"),
    path('posts/tag/<slug:tag_slug>/', views.TagPostsView.as_view(), name="tag_posts"),
    path('',views.MainPageView.as_view(), name='main_page'),
]
