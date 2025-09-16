from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        return bool(
            request.method in SAFE_METHODS
            and request.user
            and request.user.is_authenticated
        )
