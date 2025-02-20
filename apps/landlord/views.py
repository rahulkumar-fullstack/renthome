from django.shortcuts import render


# Create your views here.
async def landlord_home(request):
    return render(request, "landlord/landlord_home.html")
