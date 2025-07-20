from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm


def get_post_list(request):
    posts = Post.objects.all()

    return render(request, 'blog/post_list.html', {'posts': posts})


# def get_post_detail(request, post_id):
#     #post = Post.objects.get(id=post_id) #другой вариант
#     post = get_object_or_404(Post, id=post_id)


#     context = {'post': post}

#     return render(request, 'blog/post_detail.html', context)

# def get_post_add(request):
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


def get_post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {'post': post}
    return render(request, 'blog/post_detail.html', context)

# def get_post_add(request):
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


def get_post_add(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect('post_detail', post_id=post.id)
        # Если форма невалидна, продолжит выполнение и отобразит форму с ошибками
    else:
        form = PostForm()
    
    return render(request, 'blog/post_add.html', {'form': form})
    

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


def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
        # Если форма невалидна, покажем её снова с ошибками
        return render(request, 'blog/update_post.html', {'form': form, 'post': post})
    
    # GET запрос - показываем форму для редактирования
    form = PostForm(instance=post)
    return render(request, 'blog/update_post.html', {'form': form, 'post': post})