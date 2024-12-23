import datetime
from rest_framework.permissions import BasePermission
from utils.helpers import get_semester


class IsCreatorOfAssignmentOrManagement(BasePermission):
    """
    This permission class checks if the user is the
    creator of the assignment, or if the user is a manager/admin.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role in [3, 4]:
            return True
        return obj.lecture.professor == request.user


class IsCreatorOfAssignmentSubmissionOrManagement(BasePermission):
    """
    This permission class checks if the user is the creator
    of the assignment submission, or if the user is a manager/admin.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role in [3, 4]:
            return True
        return obj.student == request.user


class IsCreatorOfGradeOrManagement(BasePermission):
    """
    This permission class checks if the user is the creator of the grade,
    or if the user is manager/admin.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role in [3, 4]:
            return True
        return obj.assignment.lecture.professor == request.user


class IsProfessorOrManagement(BasePermission):
    """
    This permission class checks if the user is a professor,
    or if the user is a manager/admin.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [2, 3, 4]


class IsManagement(BasePermission):
    """
    This permission class checks if the user is a manager.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 4 or request.user.role == 3


class IsThisLecturesProfessor(BasePermission):
    """
    This permission class checks if the user is the professor of
    the specific lecture.
    """
    def has_object_permission(self, request, view, obj):
        return obj.professor == request.user


class RestrictAfterTwoWeeks(BasePermission):
    """
    This permission class checks if the student is allowed to
    register the lecture. Student is allowed to register if the
    registration is open, which is two weeks after the semester start date.
    """
    def has_permission(self, request, view):
        current_semester = get_semester()
        if not request.user.is_authenticated:
            return False
        if request.user.role in [2, 5]:
            return False
        start_date = current_semester.start_date
        now = datetime.datetime.now().date()
        if start_date + datetime.timedelta(weeks=2) < now:
            return False
        return True
