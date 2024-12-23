from rest_framework import permissions


class IsStudentOrManagement(permissions.BasePermission):
    """
    Custom permission to only allow students to access.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.role == 3 or request.user.role == 4:
                return True
        return (
                request.user.is_authenticated and
                request.user.role == 1
        )