from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Category, Tag, Comment
from .forms import PostForm
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Все посты (удалить после)
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(status='published').order_by('-created_at')
    paginate_by = 16  # Количество постов на страницу

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
        post = self.object
        
        # Получаем ВСЕ корневые комментарии отсортированные от старых к новым
        all_root_comments = post.comments.filter(parent__isnull=True).order_by('created_at')
        total_comments = post.comments.count()
        
        # Определяем, какие комментарии показывать
        if all_root_comments.count() > 5:
            # Показываем последние 5 комментариев (пропускаем старые)
            start_index = all_root_comments.count() - 5
            latest_comments = all_root_comments[start_index:]
        else:
            # Если комментариев 5 или меньше, показываем все
            latest_comments = all_root_comments
        
        # Получаем комментарии с ответами
        comments_with_replies = self.get_comments_with_replies(latest_comments)
        
        context['comments'] = comments_with_replies
        context['total_comments'] = total_comments
        context['has_older_comments'] = all_root_comments.count() > 5
        context['loaded_comments_count'] = latest_comments.count()
        context['older_comments_count'] = all_root_comments.count() - latest_comments.count()
        return context
    
    def get_comments_with_replies(self, comments):
        """Рекурсивно получаем комментарии с ответами для шаблона"""
        result = []
        for comment in comments:
            replies = self.get_comments_with_replies(comment.replies.all().order_by('created_at'))
            result.append({
                'comment': comment,
                'replies': replies
            })
        return result

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

# Главная страница
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

# Создание комментария (обновленный)
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get('text')
        parent_id = request.POST.get('parent_id')
        
        if not text:
            return JsonResponse({'status': 'error', 'message': 'Комментарий не может быть пустым'}, status=400)
        
        parent_comment = None
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Родительский комментарий не найден'}, status=400)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            text=text,
            parent=parent_comment
        )
        
        # Получаем ответы для нового комментария
        replies_data = self.get_replies_data(comment.replies.all(), request.user)
        
        return JsonResponse({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'text': comment.text,
                'author': comment.author.username,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_edited': comment.is_edited,
                'is_author': True,
                'level': comment.level,
                'parent_id': parent_comment.id if parent_comment else None,
                'replies': replies_data
            }
        })
    
    def get_replies_data(self, replies, user):
        """Рекурсивно получаем данные ответов"""
        result = []
        for reply in replies.order_by('created_at'):  # Сортируем ответы
            result.append({
                'id': reply.id,
                'text': reply.text,
                'author': reply.author.username,
                'created_at': reply.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_edited': reply.is_edited,
                'is_author': user.is_authenticated and reply.author == user,
                'level': reply.level,
                'replies': self.get_replies_data(reply.replies.all(), user)
            })
        return result

# Загрузка дополнительных комментариев (обновленный)
class MoreCommentsView(View):
    def get(self, request, post_slug):
        try:
            post = get_object_or_404(Post, slug=post_slug)
            offset = int(request.GET.get('offset', 0))
            limit = 5
            
            # Получаем корневые комментарии отсортированные от старых к новым
            all_root_comments = post.comments.filter(parent__isnull=True).order_by('created_at')
            
            # Загружаем старые комментарии (те, что идут до уже загруженных)
            # offset - это количество уже показанных комментариев (последние 5)
            # Значит старые комментарии начинаются с 0 до (all_count - 5)
            comments = all_root_comments[offset:offset + limit]
            
            comments_data = self.get_comments_with_replies(comments, request.user)
            
            total_older_comments = all_root_comments.count() - 5  # Всего старых комментариев
            has_more = (offset + limit) < total_older_comments
            
            return JsonResponse({
                'status': 'success',
                'comments': comments_data,
                'has_more': has_more,
                'next_offset': offset + limit,
                'older_comments_count': total_older_comments - (offset + limit)
            })
        except Post.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'Пост с slug={post_slug} не найден'
            }, status=404)
        except Exception as e:
            print(f"Error in MoreCommentsView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Ошибка при загрузке комментариев: {str(e)}'
            }, status=500)
    
    def get_comments_with_replies(self, comments, user):
        """Рекурсивно получаем комментарии с ответами"""
        result = []
        for comment in comments:
            author_username = comment.author.username if comment.author else "Deleted User"
            comment_data = {
                'id': comment.id,
                'text': comment.text,
                'author': author_username,
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_edited': comment.is_edited,
                'is_author': user.is_authenticated and comment.author == user,
                'can_quote': user.is_authenticated,
                'level': comment.level,
                'replies': self.get_comments_with_replies(comment.replies.all().order_by('created_at'), user)
            }
            result.append(comment_data)
        return result

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

