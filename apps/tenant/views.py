from django.shortcuts import render,redirect
from apps.core.models import CustomUser
from django.urls import reverse
from asgiref.sync import sync_to_async


# Create your views here.
def tenant_home(request):
    is_authenticated = request.user.is_authenticated
    if not is_authenticated:
        return redirect('home')
    return render(request, "tenant/tenant_home.html")


# search home view
def search_home(request):
    if request.method == "POST":
        city = request.POST["city"]
        state = request.POST["state"]
        minprice = request.POST["minprice"]
        maxprice = request.POST["maxprice"]
        type= request.POST['type']
        url = (
            reverse("result")
            + f"?city={city}&state={state}&minprice={minprice}&maxprice={maxprice}&type={type}&sortby=default"
        )
        return redirect(url)
    return render(request, "tenant/search_home.html")


# search result view
def search_result(request):
    
    return render(request, "tenant/search_results.html")


# view full details view
def view_detail(request):
    return render(request, "tenant/view_details.html")


# checkout view
def user_checkout(request):
    return render(request, "tenant/checkout.html")
