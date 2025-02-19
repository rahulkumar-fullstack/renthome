from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# custom manager
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# Custom User Model using AbstractUser
class CustomUser(AbstractUser):
    # make username unique=false
    username = models.CharField(max_length=150, unique=False)

    # make email=true and using it for login purpose
    email = models.EmailField(unique=True)

    # add role to determine users
    role = models.CharField(max_length=20, default="Renter")

    # user's fullname
    name = models.CharField(max_length=200)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name


class ResetPassword(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Verification code is {self.code_hash}"
