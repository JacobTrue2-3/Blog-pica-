from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, get_user_model

from config.settings import LOGIN_REDIRECT_URL
from blog.models import Post


User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:post_list') #поменять на профиль 
        else:
            return render(request, 'users/register.html', {'form': form})
    form = UserCreationForm

    return render(request, 'users/register.html', {'form': form})
    

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)  # <-- Исправлено здесь
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # return redirect('post_list') Ниже безопаснее использовать redirect на URL, который был запрошен
            # при попытке входа, если он есть
            # Если next не указан, то будет использоваться LOGIN_REDIRECT_URL из настроек
            next_url = request.GET.get('next', LOGIN_REDIRECT_URL)  # '/post/add/'
            if next_url == LOGIN_REDIRECT_URL:
                return redirect(next_url, request.user.username)  # Переход на профиль пользователя
            else: return redirect(next_url)
        else:
            return render(request, 'users/login.html', {'form': form})
    
    form = AuthenticationForm(request)  
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('blog:post_list')

def user_profile(request, user_username):
    user = get_object_or_404(User, username=user_username)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    context = {
        'user': user,
        'posts': posts,
    }

    return render(request, 'users/profile.html', context)