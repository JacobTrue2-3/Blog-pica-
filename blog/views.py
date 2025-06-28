from django.shortcuts import render

from .models import Post


def get_post_list(request):
    posts = Post.objects.all()

    return render(request, 'post_list.html', {'posts': posts})


