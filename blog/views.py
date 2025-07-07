from django.shortcuts import render, get_object_or_404, redirect
from .models import Post


def get_post_list(request):
    posts = Post.objects.all()

    return render(request, 'blog/post_list.html', {'posts': posts})


def get_post_detail(request, post_id):
    #post = Post.objects.get(id=post_id) #другой вариант
    post = get_object_or_404(Post, id=post_id)


    context = {'post': post}

    return render(request, 'blog/post_detail.html', context)

def get_post_add(request):
    if request.method == 'GET':
        return render(request, 'blog/post_add.html')
    
    if request.method == 'POST':
        title =request.POST.get('title').strip()
        text = request.POST.get('text').strip()

        errors = {}

        if not title:
            errors['title'] = 'Заполните поле заголовка'
        if not text:
            errors['text'] = 'Заполните поле текста'

        if not errors:
            post = Post.objects.create(title=title, text=text)
            return redirect('post_detail', post_id=post.id)
        else:
            context = {
                'errors': errors,
                'title': title,
                'text': text
            }
            return render(request, 'blog/post_add.html', context=context)

