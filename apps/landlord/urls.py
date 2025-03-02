from django.urls import path
from . import views

urlpatterns = [
    path("", views.landlord_home, name="landlord-home"),
    path('add-home/',views.add_home, name="add-home"),
    path('edit-home/<int:pk>',views.edit_home, name="edit-home"),
    path('delete-home/<int:pk>',views.delete_home, name="delete-home"),
]
