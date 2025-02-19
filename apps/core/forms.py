from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", "name", "role", "is_active", "is_staff")


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "name", "role")
