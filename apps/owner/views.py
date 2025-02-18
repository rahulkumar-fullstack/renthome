from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def owner_home(request):
    return JsonResponse({"message": "Hello Owner"})
