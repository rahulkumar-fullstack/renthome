from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def s_home(request):
    return JsonResponse({"message": "Hello send mail"})
