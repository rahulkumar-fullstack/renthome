from django.shortcuts import render, redirect
from apps.core.models import CustomUser
from apps.landlord.models import HomeDetails, Rentdetails
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import stripe
from django.conf import settings
from django.http import JsonResponse
from apps.send_email.views import send_email


# Create your views here.
def tenant_home(request):
    is_authenticated = request.user.is_authenticated
    if not is_authenticated:
        return redirect("home")
    else:
        # show user rented home means in rentdetails is pay_status is paid then show here
        user_id = request.user.id
        rented_home_ids = Rentdetails.objects.filter(u_id=user_id).values_list(
            "p_id", flat=True
        )

        homedetails = HomeDetails.objects.filter(id__in=rented_home_ids)
    return render(request, "tenant/tenant_home.html", {"homedetails": homedetails})


# search home view
def search_home(request):
    if request.method == "POST":
        city = request.POST["city"]
        state = request.POST["state"]
        minprice = request.POST["minprice"]
        maxprice = request.POST["maxprice"]
        type = request.POST["type"]
        url = (
            reverse("result")
            + f"?city={city}&state={state}&minprice={minprice}&maxprice={maxprice}&type={type}&sortby=default"
        )
        return redirect(url)
    return render(request, "tenant/search_home.html")


# search result view
def search_result(request):
    data = {}
    # Retrieve data
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
            price__range=(minprice, maxprice),
            state=state,
            status="not rented",
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
    return render(request, "tenant/search_results.html", context=data)


# view full details view
def view_detail(request, pk):
    data={}
    home = HomeDetails.objects.get(id=pk)
    data["home"] =home
    if request.method == "POST":
        startDate = request.POST["sdate"]
        endDate = request.POST["edate"]
        totalDays = request.POST["tdays"]
        totalPrice = request.POST["tprice"]
        msg=""
        if startDate > endDate:
            msg = "Your End Date is less than Start Date choose correctly" 
            data["msg"] = msg
        else:
            url = (
                reverse("checkout")
                + f"?id={pk}&startdate={startDate}&enddate={endDate}&totaldays={totalDays}&totalprice={totalPrice}"
            )
            return redirect(url)
    return render(request, "tenant/view_details.html", context=data)


# checkout view
def user_checkout(request):
    #check if user is logged in or not if not then redirect to login page
    is_authenticated = request.user.is_authenticated
    if not is_authenticated:
        return redirect("login")
    else:
        data={}
        # Retrieve data from url
        id= request.GET.get('id')
        startdate = request.GET.get("startdate")
        enddate = request.GET.get("enddate")
        totaldays = request.GET.get("totaldays")
        totalprice = request.GET.get("totalprice")
        home = HomeDetails.objects.get(id=id)

        #retrive user details
        tenant_id= request.user.id
        t_details = CustomUser.objects.get(id=tenant_id)
        data["t_details"] = t_details

        #retrive landlord details
        landlord_id= home.lid_id
        l_details = CustomUser.objects.get(id=landlord_id)
        data["l_details"] = l_details

        data["home"]= home
        data["sdate"]  = startdate
        data['edate'] = enddate
        data['tdays'] = totaldays
        data['tprice']= totalprice

        if request.method == "POST":
            #save details in rentdetails
            rentdetails = Rentdetails.objects.create(
                start_date=startdate,
                end_date=enddate,
                total_days=totaldays,
                total_price=totalprice,
                u_id=tenant_id,
                p_id=id
            )
            rentdetails.save()

            url = (
                reverse("payment")
                + f"?id={id}&totalprice={totalprice}"
            )
            return redirect(url)
    return render(request, "tenant/checkout.html",context=data)

@login_required
def user_payment(request):
    data={}
    # Retrieve data from url
    id= request.GET.get('id')
    totalprice = request.GET.get("totalprice")
    data["tprice"] = totalprice
    # if request.method == "POST":
    if request.method == "POST":
            url = (
                reverse("create-checkout")
                + f"?id={id}&totalprice={totalprice}"
            )
            return redirect(url)
    return render(request, "tenant/payment.html",context=data)

#stripe payment checkout 

# Set your secret Stripe API key
stripe.api_key = settings.STRIPE_KEY
def create_checkout_session(request):
    rentdetails_id = request.GET.get("id")  # Rentdetails entry ID
    total_price = request.GET.get("totalprice")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {"name": "Home Rental Payment"},
                        "unit_amount": int(float(total_price) * 100),  # Convert ₹ to paise
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("payment-success") + f"?session_id={{CHECKOUT_SESSION_ID}}&id={rentdetails_id}"
            ), 
            cancel_url=request.build_absolute_uri(reverse("payment-failed")),
        )
        return redirect(checkout_session.url)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

#update some details in db
def user_success(request):
    rentdetails_id = request.GET.get("id")  # Rentdetails entry ID
    session_id = request.GET.get("session_id")  # Stripe Session ID

    try:
        # Retrieve the Stripe session
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = session.payment_intent  # Get the payment ID from Stripe

        # Retrieve the Rentdetails entry
        rentdetails = Rentdetails.objects.get(id=rentdetails_id)
        home = HomeDetails.objects.get(id=rentdetails.p_id)

        # Update rentdetails as paid and save the payment ID
        rentdetails.pay_status = "paid"
        rentdetails.payment_id = payment_intent_id  # Save Stripe Payment ID
        rentdetails.save()

        # Mark home as rented
        home.status = "rented"
        home.save()

    except Rentdetails.DoesNotExist:
        return redirect("home")  # Redirect if ID is invalid
    except stripe.error.StripeError as e:
        return redirect("payment-failed")  # Handle Stripe errors
    
    return render(request, "tenant/success.html")

def user_fail(request):
    return render(request, "tenant/failed.html")