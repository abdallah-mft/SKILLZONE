from rest_framework.permissions import BasePermission

class IsEmailVerified(BasePermission):
    """
    Permission check for email verification.
    """
    message = 'Email verification required.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.email_verified