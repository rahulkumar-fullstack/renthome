from django.urls import path
from . import views

urlpatterns = [
    path("", views.tenant_home, name="tenant-home"),
    path('search/', views.search_home, name='search'),
    path('result/', views.search_result, name='result'),
    path('detail/<int:pk>', views.view_detail, name='detail'),
    path('checkout/', views.user_checkout, name='checkout'),
    path('payment/', views.user_payment, name='payment'),
    path('success/', views.user_success, name='success'),
    path('failed/', views.user_fail, name='failed'),

]
