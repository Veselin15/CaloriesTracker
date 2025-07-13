from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView

from .forms import UserRegisterForm, UserLoginForm, ProfileEditForm, ProfilePictureForm
from .models import Profile

UserModel = get_user_model()


class RegisterView(CreateView):
    model = UserModel
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)

        if response.status_code in [301, 302]:
            login(self.request, self.object)
        return response


# def register_view(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, "Registration successful.")
#             return redirect("home")
#     else:
#         form = UserRegisterForm()
#     return render(request, "accounts/register.html", {"form": form})

# class LoginView(LoginView):
#     template_name = "accounts/login.html"
#
# class LogoutView(LogoutView):
#     template_name = "home.html"
#     next_page = reverse_lazy('home')


# def login_view(request):
#     if request.method == "POST":
#         form = UserLoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             messages.success(request, "Login successful.")
#             return redirect("home")
#     else:
#         form = UserLoginForm()
#     return render(request, "accounts/login.html", {"form": form})
#
#
# @login_required
# def logout_view(request):
#     logout(request)
#     messages.info(request, "Logged out successfully.")
#     return redirect("login")
#
#
# from django.shortcuts import render

# Create your views here.
class ProfileDetailsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profile/profile_details.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        user_id = self.kwargs['pk']
        profile, created = Profile.objects.get_or_create(user_id=user_id)
        return profile


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'profile/profile_edit.html'

    def get_object(self, queryset=None):
        user_id = self.kwargs['pk']
        profile, created = Profile.objects.get_or_create(user_id=user_id)
        return profile

    def test_func(self):
        profile = self.get_object()
        return self.request.user.id == profile.user.id

    def get_success_url(self):
        return reverse_lazy('profile-details', kwargs={'pk': self.object.user.id})

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile_form = ProfileEditForm(instance=self.object)
        picture_form = ProfilePictureForm(instance=self.object)
        return render(request, self.template_name, {
            'form': profile_form,
            'picture_form': picture_form,
            'profile': self.object,
        })

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile_form = ProfileEditForm(request.POST, instance=self.object)
        picture_form = ProfilePictureForm(request.POST, request.FILES, instance=self.object)
        if profile_form.is_valid() and picture_form.is_valid():
            profile_form.save()
            picture_form.save()
            return redirect(self.get_success_url())
        return render(request, self.template_name, {
            'form': profile_form,
            'picture_form': picture_form,
            'profile': self.object,
        })
class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Profile
    template_name = 'profile/profile_delete.html'
    context_object_name = 'profile'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        user_id = self.kwargs['pk']
        return Profile.objects.get(user_id=user_id)

    def test_func(self):
        profile = self.get_object()
        return self.request.user.id == profile.user.id