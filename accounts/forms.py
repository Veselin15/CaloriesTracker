from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .choices import GENDER_CHOICES
from .models import User, Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'bio']

class ProfilePictureForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, label="Profile Picture")

    class Meta:
        model = Profile
        fields = ['profile_picture']