from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if hasattr(request.user, 'profile'):
                return request.user.profile.is_manager
        return False
