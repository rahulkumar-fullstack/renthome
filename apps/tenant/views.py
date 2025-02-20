from django.shortcuts import render
from asgiref.sync import sync_to_async


# Create your views here.
async def tenant_home(request):
    return render(request, "tenant/tenant_home.html")
