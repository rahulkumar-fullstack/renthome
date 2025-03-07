from django.shortcuts import render,redirect, get_object_or_404
from apps.core.models import CustomUser
from .models import HomeDetails , Rentdetails
from apps.send_email.views import send_email
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async
from datetime import datetime
from django.utils.timezone import now


@login_required
def landlord_home(request):
    user_id = request.user.id

    # Fetch all homes listed by the landlord
    homedetails = HomeDetails.objects.filter(lid_id=user_id)

    # Fetch currently rented homes
    rented_homes = Rentdetails.objects.filter(
        p__lid_id=user_id, pay_status="paid"
    ).select_related("p")  # Optimized query with related property

    today = now().date()
    rented_home_data = []

    for rent in rented_homes:
        home = rent.p  # Related home details

        # Ensure dates are `date` type
        start_date = rent.start_date.date() if isinstance(rent.start_date, datetime) else rent.start_date
        end_date = rent.end_date.date() if isinstance(rent.end_date, datetime) else rent.end_date

        # Calculate remaining days
        remaining_days = max((end_date - today).days, 0) + 1

        # Total rental duration
        total_days = (end_date - start_date).days + 1

        # Append details to list
        rented_home_data.append({
            "home": home,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "remaining_days": remaining_days,
            "total_price": rent.total_price,
        })

    return render(request, "landlord/landlord_home.html", {
        "homedetails": homedetails,
        "rented_home_data": rented_home_data,
    })

def view_homes_deatils(request):
    user_id=request.user.id
    homedetails =HomeDetails.objects.filter(lid_id=user_id)

    return render(request, "landlord/view_all_homes.html", {"homedetails": homedetails})

#add home here
@login_required
async def add_home(request):
    if request.method == 'POST':
        add = request.POST.get('add')
        add1 = request.POST.get('add1')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        price = request.POST.get('price')
        people = request.POST.get('people')
        about = request.POST.get('about')
        type = request.POST.get('type')
        condition = request.POST.get('condition')
        image_file = request.FILES.get('image')

        # Get landlord (user) ID async-safe
        user_id = await sync_to_async(lambda: request.user.id)() 

        # Async DB Operation
        await HomeDetails.objects.acreate(
            image=image_file, add=add, add1=add1, state=state, city=city,
            pincode=pincode, about=about, condition=condition,type=type,
            price=price, people=people, lid_id=user_id
        )

        user_detail = await CustomUser.objects.aget(id=user_id)

        # Send login notification email asynchronously
        email_msg = "Home added successfully"
        email_msg1 = f"You home added successfully on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. If this wasn't you, please click the button below to reset your password."
        email_msg2 = "Thank you for being with us!"
        forgot_password_url = "http://127.0.0.1:8000/auth/forgot-password/"
        context = {
            "name": user_detail.name,
            "message": email_msg,
            "message1": email_msg1,
            "message2": email_msg2,
            "url": forgot_password_url,
        }
        await send_email(
            subject="Home Added Successful | RentHome",
            recipient_email=user_detail.email,
            context=context,
        )
        return redirect('landlord-home')
    return await sync_to_async(render)(request, 'landlord/add_home.html')


#edit home here
@login_required
async def edit_home(request, pk):
    """Asynchronous view to edit home details."""
    
    # Fetch home asynchronously
    homedetails = await HomeDetails.objects.filter(id=pk).afirst()
    if not homedetails:
        # Redirect if home not found
        return redirect('landlord-home')  

    # If GET request, render form with home details
    if request.method == 'GET':
        return await sync_to_async(render)(
            request, 'landlord/edit_home.html', {"home": homedetails}
        )

    # If POST request, update home details
    add = request.POST.get('add')
    add1 = request.POST.get('add1')
    state = request.POST.get('state')
    city = request.POST.get('city')
    pincode = request.POST.get('pincode')
    price = request.POST.get('price')
    people = request.POST.get('people')
    about = request.POST.get('about')
    condition = request.POST.get('condition')
    type = request.POST.get('type')

    # Update image if uploaded
    if 'image' in request.FILES:
        homedetails.image = request.FILES['image']

    # Update fields asynchronously
    homedetails.add = add
    homedetails.add1 = add1
    homedetails.state = state
    homedetails.city = city
    homedetails.pincode = pincode
    homedetails.price = price
    homedetails.people = people
    homedetails.about = about
    homedetails.condition = condition
    homedetails.type = type

    # Save changes asynchronously
    await sync_to_async(homedetails.save)()

    # Get landlord (user) ID async-safe
    user_id = await sync_to_async(lambda: request.user.id)() 
    user_detail = await CustomUser.objects.aget(id=user_id)

    # Send login notification email asynchronously
    email_msg = "Home updated successfully"
    email_msg1 = f"You home was updated successfully on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. If this wasn't you, please click the button below to reset your password."
    email_msg2 = "Thank you for being with us!"
    forgot_password_url = "http://127.0.0.1:8000/auth/forgot-password/"
    context = {
        "name": user_detail.name,
        "message": email_msg,
        "message1": email_msg1,
        "message2": email_msg2,
        "url": forgot_password_url,
    }
    await send_email(
        subject="Home Updated Successful | RentHome",
        recipient_email=user_detail.email,
        context=context,
    )

    return redirect('landlord-home')


#delete home here
async def delete_home(request,pk):
    homedetails= await sync_to_async(get_object_or_404)(HomeDetails, id=pk)
    await sync_to_async(homedetails.delete)()
   
    # Get landlord (user) ID async-safe
    user_id = await sync_to_async(lambda: request.user.id)() 
    user_detail = await CustomUser.objects.aget(id=user_id)

    # Send login notification email asynchronously
    email_msg = "Home deleted successfully"
    email_msg1 = (
        f"Your home was deleted successfully on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
        "If this wasn't you, please click the button below to reset your password."
    )
    email_msg2 = "Thank you for being with us!"
    forgot_password_url = "http://127.0.0.1:8000/auth/forgot-password/"
    context = {
        "name": user_detail.name,
        "message": email_msg,
        "message1": email_msg1,
        "message2": email_msg2,
        "url": forgot_password_url,
    }
    await send_email(
        subject="Home Deleted Successful | RentHome",
        recipient_email=user_detail.email,
        context=context,
    )

    return redirect('landlord-home')
   