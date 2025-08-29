from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category
from .forms import PostForm
from django.contrib.auth.decorators import login_required


#Все посты
def get_post_list(request):
    posts = Post.objects.filter(status='published').order_by('-created_at')  # Фильтруем только опубликованные посты и сортируем по дате
    return render(request, 'blog/post_list.html', {'posts': posts})

#Посты по категории
def get_category_posts(request, category_slug): 
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, status='published').order_by('-created_at')

    context = {
        'category': category,
        'posts': posts
    }
    return render(request, 'blog/category_posts.html', context)

#Пост по id
def get_post_detail(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    context = {'post': post}
    return render(request, 'blog/post_detail.html', context)

#Создание поста
@login_required
def create_post(request):
    title = "Создать пост"
    submit_button_text = "Создать"
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)  # Не сохраняем сразу в БД
            post.author = request.user  # Устанавливаем текущего пользователя как автора
            post.save()  # Теперь сохраняем с автором
            return redirect('blog:post_detail', post_slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {
        'form': form, 
        'title': title, 
        'submit_button_text': submit_button_text
    })

#Редактирование поста
def update_post(request, post_id):
    title = "Редактировать пост"
    submit_button_text = "Сохранить"
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_slug=post.slug)
    return render(request, 'blog/post_form.html', {'form': form, 'post': post, 'title': title, 'submit_button_text': submit_button_text})

#Удаление поста
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_list')
    return render(request, 'blog/confirm_post_delete.html', {'post': post})




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

def main_page(request):
    posts = Post.objects.all().order_by('-created_at')  # Получаем все посты, сортируем по дате
    return render(request, 'blog/main_page.html',{'posts': posts})