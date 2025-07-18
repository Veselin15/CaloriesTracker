import os

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from accounts.choices import GENDER_CHOICES
from accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(verbose_name='email', unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    objects = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            old = Profile.objects.get(pk=self.pk)
            if old.profile_picture and self.profile_picture != old.profile_picture:
                if os.path.isfile(old.profile_picture.path):
                    os.remove(old.profile_picture.path)
        except Profile.DoesNotExist:
            pass  # New profile, no old image to remove
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def delete(self, *args, **kwargs):
        # Deactivate the user account
        if self.user:
            self.user.is_active = False
            self.user.save()
        # Delete the image file if it exists
        if self.profile_picture and os.path.isfile(self.profile_picture.path):
            os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)