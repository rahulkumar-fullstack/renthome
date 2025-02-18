from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def user_home(request):
    return JsonResponse({"message": "Hello user"})
