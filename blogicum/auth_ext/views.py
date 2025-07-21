from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login
from django.urls import reverse_lazy, reverse
from .forms import CustomUserCreationForm, CustomUserEditProfileForm


User = get_user_model()


class UserCreateView(CreateView):
    model = User
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserEditProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.username}
        )
