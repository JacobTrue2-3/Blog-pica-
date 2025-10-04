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
    path('posts/<int:post_id>/like-dislike/', views.LikeDislikePostView.as_view(), name="post_like"),
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(), name="comment_create"),
    path('comments/<int:comment_id>/edit/', views.CommentUpdateView.as_view(), name="comment_update"),
    path('comments/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name="comment_delete"),
    path('posts/<int:post_id>/favorite/', views.PostFavoriteToggleView.as_view(), name="post_favorite"),
    path('favorites/', views.FavoritePostsView.as_view(), name="favorite_posts"),
    path('', views.MainPageView.as_view(), name='main_page'),
]