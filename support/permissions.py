from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)
    

class IsStaff(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_staff)
    

