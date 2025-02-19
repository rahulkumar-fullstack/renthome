from django.shortcuts import render, redirect
from .models import CustomUser, ResetPassword
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from apps.send_email.views import send_email
import random
from datetime import datetime
import asyncio
from asgiref.sync import sync_to_async

# get current date and time from system
dateandtime = datetime.now().strftime("%I:%M %p, %d-%m-%Y")


# Create your views here.
def home_page(request):
    return render(request, "core/home_page.html")


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def terms(request):
    return render(request, "core/terms.html")


# users login view
async def user_login(request):
    msg = ""
    success = ""
    check_registered = request.GET.get("register", "")
    check_reset_password = request.GET.get("resetpassword", "")

    if check_registered:
        success = (
            "Congratulation, your account is created successfully. Now you can Login"
        )
    elif check_reset_password:
        success = (
            "Congratulation, your password is reset successfully. Now you can Login"
        )

    if request.method == "POST":
        # Fetch data from form
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user (use sync_to_async for blocking call)
        user_auth = await sync_to_async(authenticate)(
            request, email=email, password=password
        )
        if user_auth is None:
            msg = "Enter correct email or password"
        else:
            # Log in user
            await sync_to_async(login)(request, user_auth)

            # Sending email asynchronously
            email_msg = "Welcome Back to RentHome!"
            email_msg1 = f"You have successfully logged in on {dateandtime}. If this wasn't you, please click on below button to reset your password."
            email_msg2 = "Thank you for being with us!"
            forgot_password_url = "http://127.0.0.1:8000/auth/forgot-password/"
            context = {
                "name": user_auth.name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": forgot_password_url,
            }

            # Use a custom async function to send the email asynchronously
            await send_email(
                subject="Login successfully | RentHome",
                recipient_email=user_auth.email,
                context=context,
            )

            # Redirect based on user role
            if hasattr(user_auth, "role"):  # Ensure role attribute exists
                if user_auth.role == "Renter":
                    return redirect("home")
                else:
                    return redirect("owner-home")
            else:
                # Redirect to sign-in if role is not defined
                return redirect("login")
    return render(request, "core/login.html", {"success": success, "msg": msg})


# Forgot password view
async def user_forgot_password(request):
    msg = ""
    if request.method == "POST":
        # Fetch data from form
        email = request.POST.get("email")

        # Authenticate user
        user_email = ""
        try:
            # Run synchronous database query in an async-friendly way
            user_detail = await asyncio.to_thread(CustomUser.objects.get, email=email)
            user_email = user_detail.email
        except CustomUser.DoesNotExist:
            pass

        if not user_email:
            msg = "User does not exist, enter correct Email ID"
        else:
            # Delete previous generated code
            try:
                # Again, using asyncio.to_thread to offload synchronous operation
                code_generated = await asyncio.to_thread(
                    ResetPassword.objects.get, user_id=user_detail.id
                )
                await asyncio.to_thread(code_generated.delete)
            except ResetPassword.DoesNotExist:
                pass

            # Generate verification code using random
            verification_code = random.randint(100000, 999999)
            dateandtime = datetime.now()

            # Save verification code in the database
            save_verification = ResetPassword(
                user_id=user_detail.id,
                code_hash=verification_code,
                created_at=dateandtime,
            )
            # Save the record asynchronously
            await asyncio.to_thread(save_verification.save)

            # Prepare the email content
            email_msg = f"Your Reset code is {verification_code}. Timestamp: {dateandtime}. Use the button below to reset your password."
            email_msg1 = "Do not share this code with anyone."
            email_msg2 = "Thank you for being a part of our RentHome!"
            reset_password_url = "http://127.0.0.1:8000/auth/reset-password/"
            context = {
                "name": user_detail.name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": reset_password_url,
            }

            # Send email asynchronously
            await send_email(
                subject="Reset Password | RentHome",
                recipient_email=user_detail.email,
                context=context,
            )

            return redirect("reset-password")

    return render(request, "core/forgot_password.html", {"msg": msg})


# Reset password view
async def user_reset_password(request):
    msg = ""
    if request.method == "POST":
        # Fetch data from form
        verify_code = request.POST.get("verifycode")
        new_password = request.POST.get("password")

        # verify user entered code
        user_id = ""
        try:
            check_entered_code = await asyncio.to_thread(
                ResetPassword.objects.get(code_hash=verify_code)
            )
            user_id = check_entered_code.user_id
        except:
            pass

        if not user_id:
            msg = "Incorrect Verification code"
        else:
            # Delete the code from the database asynchronously
            await asyncio.to_thread(check_entered_code.delete)

            # reset password
            reset_password = await asyncio.to_thread(CustomUser.objects.get(id=user_id))
            reset_password.set_password(new_password)

            # Save the record asynchronously
            await asyncio.to_thread(reset_password.save())

            # get user details
            user_detail = await asyncio.to_thread(CustomUser.objects.get(id=user_id))

            # send confirmation mail
            email_msg = "Password Reset Successful!"
            email_msg1 = f"Your password has been reset successfully. Timestamp: {dateandtime}. Use below button to login."
            email_msg2 = "Thank you for being a part of our RentHome!"
            login_url = "http://127.0.0.1:8000/auth/login/"
            context = {
                "name": user_detail.name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": login_url,
            }
            # Send confirmation email asynchronously
            await send_email(
                subject="Reset password successfully | RentHome",
                recipient_email=user_detail.email,
                context=context,
            )

            # redirect to login page with success message
            url = reverse("login") + f"?resetpassword=success"
            return redirect(url)
    return render(request, "core/reset_user_password.html", {"msg": msg})


# choose usertype page view
def user_type(request):
    return render(request, "core/choose_usertype.html")


# register page view
async def user_register(request):
    type = request.GET.get("type")  # get user type

    # fetch data from form
    name = request.POST.get("name")
    email = request.POST.get("email")
    password = request.POST.get("password")

    # fetch data from User model to check if user already exist or not
    check_email = asyncio.to_thread(CustomUser.objects.filter(email=email))

    msg = ""
    if not type:
        # redirect to choose user type page
        return redirect("user-type")
    elif check_email.exists():
        msg = "Email already exist, try different email id"
    else:
        if request.method == "POST":
            user = asyncio.to_thread(
                CustomUser.objects.create(name=name, email=email, role=type)
            )
            user.set_password(password)  # convert in hash password
            asyncio.to_thread(user.save())

            # sending mail
            email_msg = "Congratulations!"
            email_msg1 = f" You have successfully created your account on Rent Home on {dateandtime}. We’re excited to have you on board! Explore our platform to find your perfect home."
            email_msg2 = "Happy renting!"
            login_url = "http://127.0.0.1:8000/auth/login/"
            context = {
                "name": name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": login_url,
            }
            await send_email(
                subject="Account created successfully | Rent Home",
                recipient_email=email,
                context=context,
            )

            # redirect to sign in page and add message
            url = reverse("login") + f"?register=success"
            return redirect(url)

    return render(request, "core/register.html", {"type": type, "msg": msg})


# user logout
async def user_logout(request):
    # get user details
    user_details = request.user
    # sending mail
    email_msg = f"You have successfully logged out on {dateandtime}."
    email_msg1 = "See you soon!"
    context = {
        "name": user_details.name,
        "message": email_msg,
        "message1": email_msg1,
    }
    await send_email(
        subject="Logout successfully | RentHome",
        recipient_email=user_details.email,
        context=context,
    )

    logout(request)
    return redirect("welcome")
