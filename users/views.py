from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.views.generic import CreateView, DetailView, View
from django.contrib.auth.views import LoginView
from blog.models import Post
from django.core.paginator import Paginator

User = get_user_model()


# Регистрация
class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('users:profile', user_username=user.username)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile', user_username=request.user.username)
        return super().get(request, *args, **kwargs)


# Вход
class LoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url and next_url.startswith('/'):  # Проверяем, что URL валиден
            return next_url
        return reverse_lazy('users:profile', kwargs={'user_username': self.request.user.username})


# Выход
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('blog:main_page')


# Профиль пользователя
class UserProfileView(DetailView):
    model = User
    template_name = 'users/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'user_username'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем посты пользователя
        posts = Post.objects.filter(author=self.object).order_by('-created_at')
        # Настраиваем пагинацию
        paginator = Paginator(posts, 6)  # 6 постов на страницу
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # Добавляем в контекст
        context['posts'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        return context