from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, ResetPassword
from apps.send_email.views import send_email
import random
from datetime import datetime
from django.utils import timezone
from asgiref.sync import sync_to_async

# Get current date and time
dateandtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def home_page(request):
    return render(request, "core/home_page.html")


async def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


async def terms(request):
    return render(request, "core/terms.html")


async def user_login(request):
    msg = ""
    success = ""
    check_registered = request.GET.get("register", "")
    check_reset_password = request.GET.get("resetpassword", "")

    if check_registered:
        success = "Congratulations, your account has been created successfully. Now you can log in."
    elif check_reset_password:
        success = "Your password has been reset successfully. Now you can log in."

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user
        user_auth = await sync_to_async(authenticate, thread_sensitive=True)(
            request, email=email, password=password
        )
        if user_auth is None:
            msg = "Enter correct email or password"
        else:
            # Log in user
            await sync_to_async(login, thread_sensitive=True)(request, user_auth)

            # Send login notification email asynchronously
            email_msg = "Welcome Back to RentHome!"
            email_msg1 = f"You have successfully logged in on {dateandtime}. If this wasn't you, please click the button below to reset your password."
            email_msg2 = "Thank you for being with us!"
            forgot_password_url = "http://127.0.0.1:8000/auth/forgot-password/"
            context = {
                "name": user_auth.name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": forgot_password_url,
            }
            await sync_to_async(send_email)(
                subject="Login Successful | RentHome",
                recipient_email=user_auth.email,
                context=context,
            )

            # Redirect based on user role
            if hasattr(user_auth, "role"):
                if user_auth.role == "Renter":
                    return redirect("user-home")
                else:
                    return redirect("owner-home")
            else:
                return redirect("login")
    return render(request, "core/login.html", {"success": success, "msg": msg})


# Forgot password view
async def user_forgot_password(request):
    msg = ""
    if request.method == "POST":
        email = request.POST.get("email")

        # Check if user exists
        try:
            user_detail = await sync_to_async(CustomUser.objects.get)(email=email)
        except CustomUser.DoesNotExist:
            user_detail = None

        if not user_detail:
            msg = "User does not exist, enter correct Email ID"
        else:
            # Delete previous generated code
            await sync_to_async(
                ResetPassword.objects.filter(user_id=user_detail.id).delete
            )()

            # Generate verification code
            verification_code = random.randint(100000, 999999)

            # Save verification code in database with the correct datetime format
            await ResetPassword.objects.acreate(
                user_id=user_detail.id,
                code_hash=verification_code,
                created_at=timezone.now(),  # Use timezone.now() for current datetime
            )

            # Send reset password email asynchronously
            email_msg = f"Your Reset code is {verification_code}. Timestamp: {timezone.now().strftime('%I:%M %p, %d-%m-%Y')}. Use the button below to reset your password."
            email_msg1 = "Do not share this code with anyone."
            email_msg2 = "Thank you for being a part of our Rent Home!"
            reset_password_url = "http://127.0.0.1:8000/auth/reset-password/"
            context = {
                "name": user_detail.name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": reset_password_url,
            }
            await sync_to_async(send_email)(
                subject="Reset Password | Rent Home",
                recipient_email=user_detail.email,
                context=context,
            )

            return redirect("reset-password")
    return render(request, "core/forgot_password.html", {"msg": msg})


async def user_reset_password(request):
    msg = ""
    if request.method == "POST":
        # Fetch data from form
        verify_code = request.POST.get("verifycode")
        new_password = request.POST.get("password")

        # Verify user-entered code
        check_entered_code = await ResetPassword.objects.aget(code_hash=verify_code)

        if not check_entered_code:
            msg = "Incorrect Verification code"
        else:

            # Delete code from database
            await check_entered_code.adelete()

            # Reset password
            user_id = check_entered_code.user_id

            reset_password = await CustomUser.objects.aget(id=user_id)
            reset_password.set_password(new_password)
            await reset_password.asave()

            # Send confirmation mail
            email_msg = "Password Reset Successful!"
            email_msg1 = f"Your password has been reset successfully. Timestamp: {dateandtime}. Use the button below to login."
            email_msg2 = "Thank you for being a part of our RentHome!"
            login_url = "http://127.0.0.1:8000/auth/login/"
            context = {
                "name": reset_password.name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": login_url,
            }
            await sync_to_async(send_email)(
                subject="Reset password successfully | RentHome",
                recipient_email=reset_password.email,
                context=context,
            )

            # Redirect to login page with success message
            url = reverse("login") + "?resetpassword=success"
            return redirect(url)

    return render(request, "core/reset_user_password.html", {"msg": msg})


# choose usertype page view
async def choose_user_type(request):
    return render(request, "core/choose_usertype.html")


# register page view
async def user_register(request):
    user_type = request.GET.get("type")  # get user type

    # Fetch data from form
    name = request.POST.get("name")
    email = request.POST.get("email")
    password = request.POST.get("password")

    # Check if user already exists
    user_exists = await sync_to_async(CustomUser.objects.filter(email=email).exists)()

    msg = ""
    if not user_type:
        # Redirect to choose user type page
        return redirect("user-type")
    elif user_exists:
        msg = "Email already exists, try a different email ID"
    else:
        if request.method == "POST":
            # Create new user
            user = CustomUser(name=name, email=email, role=user_type)
            user.set_password(password)  # Convert to hashed password
            await sync_to_async(user.save)()

            # Sending welcome email asynchronously
            email_msg = "Congratulations!"
            email_msg1 = f"You have successfully created your account on Rent Home on {dateandtime}. We’re excited to have you on board! Explore our platform to find your perfect home."
            email_msg2 = "Happy renting!"
            login_url = "http://127.0.0.1:8000/auth/login/"
            context = {
                "name": name,
                "message": email_msg,
                "message1": email_msg1,
                "message2": email_msg2,
                "url": login_url,
            }
            await sync_to_async(send_email)(
                subject="Account created successfully | Rent Home",
                recipient_email=email,
                context=context,
            )

            # Redirect to sign-in page with success message
            url = reverse("login") + "?register=success"
            return redirect(url)

    return render(request, "core/register.html", {"type": user_type, "msg": msg})


async def user_logout(request):
    # Get user details
    user_details = await sync_to_async(lambda: request.user)()

    # Ensure `user_details.name` is accessed correctly
    user_name = await sync_to_async(lambda: user_details.name)()
    user_email = await sync_to_async(lambda: user_details.email)()

    # Sending logout notification email asynchronously
    email_msg = f"You have successfully logged out on {dateandtime}."
    email_msg1 = "See you soon!"
    context = {
        "name": user_name,
        "message": email_msg,
        "message1": email_msg1,
    }

    await sync_to_async(send_email)(
        subject="Logout successful | Rent Home",
        recipient_email=user_email,
        context=context,
    )

    # Log out user properly
    await sync_to_async(logout, thread_sensitive=True)(request)

    return redirect("home")
