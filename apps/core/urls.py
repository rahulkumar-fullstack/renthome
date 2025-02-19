from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("privacy", views.privacy_policy, name="privacy"),
    path("terms", views.terms, name="terms"),
    path("auth/login", views.user_login, name="login"),
    path("auth/logout", views.user_logout, name="logout"),
    path("auth/forgotpassword", views.user_forgot_password, name="forgot-password"),
    path("auth/resetpassword", views.user_reset_password, name="reset-password"),
    path("auth/register", views.user_type, name="user-type"),
    path("auth/register/user", views.user_register, name="register"),
]
