def navdata(request):
    """Get authentication status & user role asynchronously"""
    is_authenticated = request.user.is_authenticated
    user_role = getattr(request.user, "role", None)
    return {"is_authenticated": is_authenticated, "user_role": user_role}
