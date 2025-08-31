from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Все посты
# def get_post_list(request):
#     posts = Post.objects.filter(status='published').order_by('-created_at')
#     return render(request, 'blog/post_list.html', {'posts': posts})

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(status='published').order_by('-created_at')

# Посты по категории
# def get_category_posts(request, category_slug): 
#     category = get_object_or_404(Category, slug=category_slug)
#     posts = Post.objects.filter(category=category, status='published').order_by('-created_at')

#     context = {
#         'category': category,
#         'posts': posts
#     }
#     return render(request, 'blog/category_posts.html', context)
    
class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Post.objects.filter(category=self.category, status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category  # Используем уже сохранённый self.category
        return context

# Посты по тегу
# def get_tag_posts(request, tag_slug):
#     tag = get_object_or_404(Tag, slug=tag_slug)
#     posts = Post.objects.filter(tags=tag, status='published').order_by('-created_at')
#     context = {'tag': tag, 'posts': posts}
#     return render(request, 'blog/tag_posts.html', context)

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
# def get_post_detail(request, post_slug):
#     post = get_object_or_404(Post, slug=post_slug)
#     context = {'post': post}
#     return render(request, 'blog/post_detail.html', context)

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'post_slug'

# Создание поста
# @login_required
# def create_post(request):
#     title = "Создать пост"
#     submit_button_text = "Создать"
    
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()  # Сохраняем пост сначала
            
#             # Обрабатываем теги вручную
#             tag_names = form.cleaned_data.get('tags_input', [])
#             for tag_name in tag_names:
#                 tag, created = Tag.objects.get_or_create(
#                     name=tag_name.lower(),  # Приводим к нижнему регистру
#                     defaults={'name': tag_name.lower()}
#                 )
#                 post.tags.add(tag)
            
#             return redirect('blog:post_detail', post_slug=post.slug)
#     else:
#         form = PostForm()
    
#     return render(request, 'blog/post_form.html', {
#         'form': form, 
#         'title': title, 
#         'submit_button_text': submit_button_text
#     })
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
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
# @login_required
# def update_post(request, post_id):
#     title = "Редактировать пост"
#     submit_button_text = "Сохранить"
#     post = get_object_or_404(Post, id=post_id)
    
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES, instance=post)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.save()  # Сохраняем пост сначала
            
#             # Очищаем текущие теги и добавляем новые
#             post.tags.clear()
#             tag_names = form.cleaned_data.get('tags_input', [])
#             for tag_name in tag_names:
#                 tag, created = Tag.objects.get_or_create(
#                     name=tag_name.lower(),  # Приводим к нижнему регистру
#                     defaults={'name': tag_name.lower()}
#                 )
#                 post.tags.add(tag)
            
#             return redirect('blog:post_detail', post_slug=post.slug)
#     else:
#         # Инициализируем форму с текущими данными
#         form = PostForm(instance=post)
#         # Устанавливаем начальное значение для tags_input
#         form.fields['tags_input'].initial = ', '.join([tag.name for tag in post.tags.all()])
    
#     return render(request, 'blog/post_form.html', {
#         'form': form, 
#         'post': post, 
#         'title': title, 
#         'submit_button_text': submit_button_text
#     })
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

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
        context['title'] = "Редактировать пост"
        context['submit_button_text'] = "Сохранить"
        post = self.get_object()
        context['post'] = post
        context['form'].fields['tags_input'].initial = ', '.join([tag.name for tag in post.tags.all()])
        return context

# Удаление поста
# @login_required
# def delete_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     if request.method == 'POST':
#         post.delete()
#         return redirect('blog:post_list')
#     return render(request, 'blog/confirm_post_delete.html', {'post': post})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/confirm_post_delete.html'
    context_object_name = 'post'

    def get_success_url(self):
        return reverse('blog:post_list')

#Главная страница
# def main_page(request):
#     posts = Post.objects.all().order_by('-created_at')  # Получаем все посты, сортируем по дате
#     return render(request, 'blog/main_page.html',{'posts': posts})

class MainPageView(TemplateView):
    template_name = 'blog/main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all().order_by('-created_at')
        return context

#Функции другими способами

# def get_post_add(request):
#     if request.method == 'GET':
#         return render(request, 'blog/post_add.html')
    
#     if request.method == 'POST':
#         title =request.POST.get('title').strip()
#         text = request.POST.get('text').strip()

#         errors = {}

#         if not title:
#             errors['title'] = 'Заполните поле заголовка'
#         if not text:
#             errors['text'] = 'Заполните поле текста'

#         if not errors:
#             post = Post.objects.create(title=title, text=text)
#             return redirect('post_detail', post_id=post.id)
#         else:
#             context = {
#                 'errors': errors,
#                 'title': title,
#                 'text': text
#             }
#             return render(request, 'blog/post_add.html', context=context)

# def update_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id)

#     if request.method == 'POST':
#         form = PostForm(request.POST, instance=post)
#         if form.is_valid():
#             update_post = form.save()
#             return redirect('post_detail', post_id=update_post.id)
    
#     form = PostForm(instance=post)
#     return render(request, 'blog/update_post.html', {'form': form})


# def update_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
    
#     if request.method == 'POST':
#         form = PostForm(request.POST, instance=post)
#         if form.is_valid():
#             form.save()
#             return redirect('post_detail', post_id=post.id)
#         # Если форма невалидна, покажем её снова с ошибками
#         return render(request, 'blog/update_post.html', {'form': form, 'post': post})
    
#     # GET запрос - показываем форму для редактирования
#     form = PostForm(instance=post)
#     return render(request, 'blog/update_post.html', {'form': form, 'post': post})

# def create_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = Post.objects.create(
#                 title=form.cleaned_data['title'], 
#                 text=form.cleaned_data['text']
#             )
#             return redirect('post_detail', post_id=post.id)
#         # Если форма невалидна, продолжит выполнение и отобразит форму с ошибками
#     else:
#         form = PostForm()
    
#     return render(request, 'blog/post_add.html', {'form': form})

# def get_post_detail(request, post_id):
#     #post = Post.objects.get(id=post_id) #другой вариант
#     post = get_object_or_404(Post, id=post_id)


#     context = {'post': post}

#     return render(request, 'blog/post_detail.html', context)

# def create_post(request):
#     if request.method == 'GET':
#         form = PostForm()
#         return render(request, 'blog/post_add.html', {'form': form})

#     if request.method == 'POST':
#         form = PostForm(request.POST)

#         if form.is_valid():
#             post = Post.objects.create(
#                 title=form.cleaned_data['title'], 
#                 text=form.cleaned_data['text'])
            
#             return redirect('post_detail', post_id=post.id)

