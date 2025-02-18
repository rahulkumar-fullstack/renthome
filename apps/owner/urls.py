from django.urls import path
from . import views

urlpatterns = [path("", views.owner_home, name="owner")]
