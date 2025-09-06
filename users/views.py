from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings
from django.views.generic import CreateView, FormView, DetailView, View
from blog.models import Post

User = get_user_model()


# Регистрация
class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'user_username': self.object.username})


# Вход
class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = AuthenticationForm

    def get_form_kwargs(self):
        """Передаем request в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.POST or None
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        next_url = self.request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        if next_url == settings.LOGIN_REDIRECT_URL:
            return redirect('users:profile', user_username=user.username)
        return redirect(next_url)


# Выход
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('blog:post_list')


# Профиль пользователя
class UserProfileView(DetailView):
    model = User
    template_name = 'users/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'user_username'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.object).order_by('-created_at')
        return context
