from django.urls import path
from . import views

urlpatterns = [path("", views.landlord_home, name="landlord-home")]
