from asgiref.sync import sync_to_async
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


# ✅ Async tenant home
async def tenant_home(request):
    user_id = await sync_to_async(lambda: request.user.id)()
    auth_user =  await sync_to_async(lambda: request.user.is_authenticated)()
    if not auth_user:
        return redirect("home")

    rented_home_ids = await sync_to_async(
        lambda: list(Rentdetails.objects.filter(u_id=user_id, pay_status="paid").values_list("p_id", flat=True))
    )()
    
    homedetails = await sync_to_async(lambda: list(HomeDetails.objects.filter(id__in=rented_home_ids, status="rented")))()
    
    return await sync_to_async(render)(request, "tenant/tenant_home.html", {"homedetails": homedetails})


#search home
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


# ✅ Async search result
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


async def view_detail(request, pk):
    home = await HomeDetails.objects.aget(id=pk)

    if request.method == "POST":
        startDate = request.POST["sdate"]
        endDate = request.POST["edate"]
        totalDays = request.POST["tdays"]
        totalPrice = request.POST["tprice"]

        # Convert string dates to datetime objects
        start_date_obj = datetime.strptime(startDate, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(endDate, "%Y-%m-%d").date()

        if start_date_obj >= end_date_obj:
            return await sync_to_async(render)(
                request, "tenant/view_details.html", {"home": home, "msg": "End Date must be after Start Date!"}
            )

        url = (
            reverse("checkout")
            + f"?id={pk}&startdate={startDate}&enddate={endDate}&totaldays={totalDays}&totalprice={totalPrice}"
        )
        return redirect(url)

    return await sync_to_async(render)(request, "tenant/view_details.html", {"home": home})

async def user_checkout(request):
    # ✅ Fetch user safely in an async view
    user_id = await sync_to_async(lambda: request.user.id)()
    id = request.GET.get('id')
    startdate = request.GET.get("startdate")
    enddate = request.GET.get("enddate")
    totaldays = request.GET.get("totaldays")
    totalprice = request.GET.get("totalprice")

    # ✅ Fetch all DB objects asynchronously
    home = await HomeDetails.objects.aget(id=id)
    tenant = await CustomUser.objects.aget(id=user_id)
    landlord = await CustomUser.objects.aget(id=home.lid_id)

    if request.method == "POST":
        rentdetails = Rentdetails(
            start_date=startdate,
            end_date=enddate,
            total_days=totaldays,
            total_price=totalprice,
            u_id=tenant.id,
            p_id=id
        )
        await sync_to_async(rentdetails.save)()

        return redirect(reverse("payment") + f"?id={id}&totalprice={totalprice}")

    return await sync_to_async(render)(request, "tenant/checkout.html", {
        "home": home,
        "t_details": tenant,
        "l_details": landlord,
        "sdate": startdate,
        "edate": enddate,
        "tdays": totaldays,
        "tprice": totalprice
    })

@login_required
async def user_payment(request):
    data = {}

    # Retrieve data from URL
    id = request.GET.get('id')
    totalprice = request.GET.get("totalprice")
    data["tprice"] = totalprice

    if request.method == "POST":
        url = reverse("create-checkout") + f"?id={id}&totalprice={totalprice}"
        return redirect(url)  # ✅ No need to await redirect()

    return await sync_to_async(render)(request, "tenant/payment.html", data)


# ✅ Async Stripe payment checkout
stripe.api_key = settings.STRIPE_KEY

async def create_checkout_session(request):
    rentdetails_id = request.GET.get("id")
    total_price = request.GET.get("totalprice")

    try:
        # Convert Stripe API call to async
        checkout_session = await sync_to_async(stripe.checkout.Session.create)(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": "Home Rental Payment"},
                    "unit_amount": int(float(total_price) * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("payment-success") + f"?id={rentdetails_id}"),
            cancel_url=request.build_absolute_uri(reverse("payment-failed")),
        )

        # Since `redirect()` is synchronous, wrap it in `sync_to_async`
        return await sync_to_async(redirect)(checkout_session.url)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ Async payment success
async def user_success(request):
    rentdetails_id = request.GET.get("id")
    try:
        rentdetails = await Rentdetails.objects.aget(id=rentdetails_id)
        home = await HomeDetails.objects.aget(id=rentdetails.p_id)
        tenant = await CustomUser.objects.aget(id=rentdetails.u_id)
        landlord = await CustomUser.objects.aget(id=home.lid_id)

        rentdetails.pay_status = "paid"
        await sync_to_async(rentdetails.save)()

        home.status = "rented"
        await sync_to_async(home.save)()

        # Email Notifications
        await send_email(
            subject="🏡 Booking Confirmed | RentHome",
            recipient_email=tenant.email,
            context={
                "name": tenant.name,
                "message": "Your booking was successful!",
                "message1": f"Your booking for {home.add}, {home.city} is confirmed. 🏡\nTotal Price: ₹{rentdetails.total_price}",
                "message2": "Enjoy your stay! 😊",
                "url": "http://127.0.0.1:8000/tenant/home/"
            }
        )

        await send_email(
            subject="🏡 Your Home Has Been Rented | RentHome",
            recipient_email=landlord.email,
            context={
                "name": landlord.name,
                "message": "Your home has been rented!",
                "message1": f"Property at {home.add}, {home.city} rented by {tenant.name}. Total: ₹{rentdetails.total_price}",
                "message2": "Thank you for listing with RentHome!",
                "url": "http://127.0.0.1:8000/landlord/home/"
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return redirect("payment-failed")

    return await sync_to_async(render)(request, "tenant/success.html")


# ✅ Async payment failure
async def user_fail(request):
    return await sync_to_async(render)(request, "tenant/failed.html")
