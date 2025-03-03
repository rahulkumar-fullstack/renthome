from django.shortcuts import render,redirect,get_object_or_404
from apps.core.models import CustomUser
from apps.landlord.models import HomeDetails ,Rentdetails
from django.urls import reverse
from apps.send_email.views import send_email
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async
from datetime import datetime


# Create your views here.
def tenant_home(request):
    is_authenticated = request.user.is_authenticated
    if not is_authenticated:
        return redirect('home')
    else:
        user_id=request.user.id
        rented_home_ids = Rentdetails.objects.filter(u_id=user_id).values_list('p_id', flat=True)
        # Fetch all home details matching the rented home IDs
        homedetails = HomeDetails.objects.filter(id__in=rented_home_ids)
    return render(request, "tenant/tenant_home.html" , {"homedetails": homedetails})


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
    data = {}
    # Retrieve data from find home form
    city = request.GET.get("city")
    state = request.GET.get("state")
    minprice = request.GET.get("minprice")
    maxprice = request.GET.get("maxprice")
    type = request.GET.get("type")
    sortby = request.GET.get("sortby")

    # filter data
    home_data = HomeDetails.objects.filter(
        city__icontains=city,
        state=state,
        type=type,
        price__range=(minprice, maxprice),
        status="not rented",
    )
    # __range to find between values
    # __icontain ignore case to get value

    home_count = home_data.count()  # get result count from database

    # if data is not found according to user but it similar to location
    if not home_data:
        home = HomeDetails.objects.filter(
            type=type,
            price__range=(minprice, maxprice),
            state=state, 
            status="not rented"
        )
        if not home:
            data["msg"] = "No homes found at your city !!"
        else:
            data["msg"] = (
                "No homes found based on given values but we found on nearby location !!"
            )
    else:
        home = home_data

    # sorting by price
    if sortby == "high":
        home = home.order_by("-price")  #'-' for descending order
    elif sortby == "low":
        home = home.order_by("price")
    else:
        home = home

    # send data from sortby form to get sorted results
    if request.method == "POST":
        sort_by = request.POST["sortby"]
        url = (
            reverse("result")
            + f"?city={city}&state={state}&minprice={minprice}&maxprice={maxprice}&type={type}&sortby={sort_by}"
        )
        return redirect(url)

    data["count"] = home_count
    data["homes"] = home
    data["sort"] = sortby
    return render(request, "tenant/search_results.html",context=data)


# view full details view
def view_detail(request,pk):
    home = HomeDetails.objects.get(id=pk)
    if request.method == "POST":
        startDate = request.POST["sdate"]
        endDate = request.POST["edate"]
        totalDays = request.POST["tdays"]
        totalPrice = request.POST["tprice"]
        url = (
            reverse("checkout")
            + f"?id={pk}&startdate={startDate}&enddate={endDate}&totaldays={totalDays}&totalprice={totalPrice}"
        )
        return redirect(url)
    return render(request, "tenant/view_details.html",{"home":home})


# checkout view
def user_checkout(request):
    return render(request, "tenant/checkout.html")
