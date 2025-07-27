from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('Login') #поменять на профиль 
        else:
            return render(request, 'users/register.html', {'form': form})
    form = UserCreationForm

    return render(request, 'users/register.html', {'form': form})
    

# def login_view(request):
#     if request.method == "POST":
#         form = AuthenticationForm(request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)

#             return redirect('post_list')
#         else:
#             return render(request, 'users/login.html', {'form':form})
#     form = AuthenticationForm()

#     return render(request, 'users/login.html', {'form':form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)  # <-- Исправлено здесь
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('post_list')
        else:
            return render(request, 'users/login.html', {'form': form})
    
    form = AuthenticationForm(request)  # <-- И здесь добавили request
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('post_list')