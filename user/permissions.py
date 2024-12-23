from rest_framework.permissions import BasePermission


class IsOwnProfessor(BasePermission):
    """
    Custom permission to only allow the professor of a lecture to edit it.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role not in [2, 3, 4]:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role in [3, 4]:
            return True
        return obj.lecture.professor == request.user


class IsOwnStudentOrProfessor(BasePermission):
    """
    Custom permission to only allow the student
    or professor of a lecture to view it.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role in [3, 4]:
            return True
        if obj.user == request.user:
            return True
        if obj.lecture.professor == request.user:
            return True
        return False


class IsOwnerOrManagement(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated:
            if (
                    request.user.role == 4 and
                    obj.faculty and
                    obj.faculty.department == request.user.department
            ):
                return True
        return obj == request.user
