def user_context(request):
    return {
        "is_authenticated": request.user.is_authenticated,
        "user_role": (
            getattr(request.user, "role", None)
            if request.user.is_authenticated
            else None
        ),
    }
