from django.shortcuts import render


# Create your views here.
async def tenant_home(request):
    return render(request, "tenant/tenant_home.html")
