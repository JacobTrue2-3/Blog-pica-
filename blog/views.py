from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Category, Tag, Comment
from .forms import PostForm
from django.urls import reverse, reverse_lazy
from django.db.models import Q

# Все посты (удалить после)
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(status='published').order_by('-created_at')
    paginate_by = 16 # Количество постов на страницу

# Посты по категории
class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Post.objects.filter(category=self.category, status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category 
        return context

# Посты по тегу
class TagPostsView(ListView):
    model = Post
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return Post.objects.filter(tags=self.tag, status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

# Пост по id
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'post_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()  # Добавляем комментарии
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        post = self.get_object()
        need_save = False

        # Увеличиваем счетчик просмотров, если пост не просмотрен в сессии
        session_key = f'viewed_post_{post.id}'
        if not request.session.get(session_key, False):
            post.views_count += 1
            request.session[session_key] = True
            need_save = True

        # Добавляем аутентифицированного пользователя в viewed_users
        if request.user.is_authenticated and request.user != post.author:
            post.viewed_users.add(request.user)
            need_save = True

        # Сохраняем изменения, если они есть
        if need_save:
            post.save()

        return response

# Создание поста
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    login_url = reverse_lazy('users:login') 
    extra_context = {
        'title': "Создать пост",
        'submit_button_text': "Создать",
    }

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        tag_names = form.cleaned_data.get('tags_input', [])
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.lower(),
                defaults={'name': tag_name.lower()}
            )
            post.tags.add(tag)
        return redirect('blog:post_detail', post_slug=post.slug)

# Редактирование поста
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    extra_context = {
        'title': "Редактировать пост",
        'submit_button_text': "Сохранить",
    }

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        post.tags.clear()
        tag_names = form.cleaned_data.get('tags_input', [])
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.lower(),
                defaults={'name': tag_name.lower()}
            )
            post.tags.add(tag)
        return redirect('blog:post_detail', post_slug=post.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post'] = post
        context['form'].fields['tags_input'].initial = ', '.join([tag.name for tag in post.tags.all()])
        return context

# Удаление поста
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/confirm_post_delete.html'
    context_object_name = 'post'

    def get_success_url(self):
        return reverse('blog:main_page')

#Главная страница
class MainPageView(ListView):
    model = Post
    template_name = 'blog/main_page.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = Post.objects.filter(status='published').order_by('-created_at')
        query = self.request.GET.get('q')
        search_category = self.request.GET.get('search_category')
        search_tag = self.request.GET.get('search_tag')

        if query and query.strip():
            # Нормализуем запрос: удаляем лишние пробелы
            query = query.strip()
            # Базовые условия поиска
            search_conditions = Q()
            # Если чекбоксы не отмечены, ищем только по заголовку и тексту
            if not (search_category or search_tag):
                search_conditions = Q(title__icontains=query) | Q(text__icontains=query)
            else:
                # Если отмечены чекбоксы, добавляем поиск по категориям и/или тегам
                if search_category:
                    search_conditions |= Q(category__name__icontains=query)
                if search_tag:
                    search_conditions |= Q(tags__name__icontains=query)
            queryset = queryset.filter(search_conditions)
            if search_tag:
                queryset = queryset.distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['search_category'] = self.request.GET.get('search_category', False)
        context['search_tag'] = self.request.GET.get('search_tag', False)
        return context


class LikeDislikePostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        action = request.POST.get('action')

        if action == 'like':
            if user in post.liked_users.all():
                post.liked_users.remove(user)  # Удаляем лайк
                action_taken = 'unliked'
            else:
                post.liked_users.add(user)  # Добавляем лайк
                post.disliked_users.remove(user)  # Удаляем дизлайк, если был
                action_taken = 'liked'
        elif action == 'dislike':
            if user in post.disliked_users.all():
                post.disliked_users.remove(user)  # Удаляем дизлайк
                action_taken = 'undisliked'
            else:
                post.disliked_users.add(user)  # Добавляем дизлайк
                post.liked_users.remove(user)  # Удаляем лайк, если был
                action_taken = 'disliked'
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

        post.save()
        return JsonResponse({
            'status': 'success',
            'action': action_taken,
            'like_count': post.liked_users.count(),
            'dislike_count': post.disliked_users.count(),
        })
    
# Создание комментария
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get('text')
        if not text:
            return JsonResponse({'status': 'error', 'message': 'Комментарий не может быть пустым'}, status=400)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            text=text
        )
        return JsonResponse({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'text': comment.text,
                'author': comment.author.username,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_author': True  # Для управления кнопками редактирования/удаления
            }
        })

# Редактирование комментария
class CommentUpdateView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            if comment.author != request.user:
                return JsonResponse({'status': 'error', 'message': 'Вы не можете редактировать этот комментарий'}, status=403)

            text = request.POST.get('text')
            if not text or not text.strip():
                return JsonResponse({'status': 'error', 'message': 'Комментарий не может быть пустым'}, status=400)

            comment.text = text.strip()
            comment.is_edited = True  # Устанавливаем is_edited=True при редактировании
            comment.save()
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'id': comment.id,
                    'text': comment.text,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_edited': comment.is_edited
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Произошла ошибка: {str(e)}'}, status=500)

# Удаление комментария
class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.author != request.user:
            return JsonResponse({'status': 'error', 'message': 'Вы не можете удалить этот комментарий'}, status=403)

        comment.delete()
        return JsonResponse({'status': 'success', 'comment_id': comment_id})


# Переключение избранного для поста
class PostFavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Требуется авторизация'}, status=401)

        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.favorites_users.all():
            post.favorites_users.remove(user)
            action_taken = 'removed'
        else:
            post.favorites_users.add(user)
            action_taken = 'added'
        post.save()
        return JsonResponse({
            'status': 'success',
            'action': action_taken,
            'favorites_count': post.favorites_users.count(),
        })

# Страница избранных постов пользователя
class FavoritePostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/favorite_posts.html'  # Новый шаблон, создадим ниже
    context_object_name = 'posts'
    paginate_by = 9  # Как на главной, для consistency

    def get_queryset(self):
        return self.request.user.favorite_posts.filter(status='published').order_by('-created_at')