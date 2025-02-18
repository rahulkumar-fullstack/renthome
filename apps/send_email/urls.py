from django.urls import path
from . import views

urlpatterns = [path("", views.s_home, name="sendmail")]
