from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from config.settings import LOGIN_REDIRECT_URL

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list') #поменять на профиль 
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
            return redirect(next_url)
        else:
            return render(request, 'users/login.html', {'form': form})
    
    form = AuthenticationForm(request)  # <-- И здесь добавили request
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('post_list')