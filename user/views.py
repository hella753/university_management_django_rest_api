import os
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from course.permissions import IsManagement, IsProfessorOrManagement
from course.utils.grade_calculator import GradeCalculator
from payment.permissions import IsStudentOrManagement
from utils.helpers import get_semester
from .permissions import IsOwnProfessor, IsOwnStudentOrProfessor
from .serializers import *
from .permissions import IsOwnerOrManagement
from course.models import Lecture
from .utils.google_calendar import GoogleCalendar
from dotenv import load_dotenv

load_dotenv()


class UserViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing user instances.

    If the user is a professor, return the students of the professor.

    If the user is a student, return the student in detail.

    If the user is a manager, return all users in their department.

    If the user is admin, return all users.
    """
    lookup_field = "username"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["role", "lectures", "courses"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UserModificationSerializer
        return UserDisplaySerializer

    def get_queryset(self):
        """
        """
        user = self.request.user
        queryset = User.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role == 2:
                queryset = User.objects.filter(
                    lectures__professor=user, role=1
                )
            elif user.role == 4:
                queryset = User.objects.filter(
                    faculty__department=user.department
                )
        return queryset.select_related(
            "faculty",
            "department"
        ).prefetch_related(
            "lectures",
            "lectures__resources",
            "lectures__course",
            "lectures__professor",
            "courses",
            "faculty__department"
        )

    def get_permissions(self):
        """
        If the action is not "retrieve", only managers can access the view.
        If the action is "retrieve", only the owner or admin
        can access the view.
        """
        if self.action == "list":
            return [IsProfessorOrManagement()]
        elif self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsManagement()]
        else:
            return [IsOwnerOrManagement()]

    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = serializer.data
        # If the user is a student, calculate the GPA.
        if instance.role in [1, 5]:
            gpa_cache_key = f"gpa_{instance.username}"
            gpa = cache.get(gpa_cache_key)
            if gpa is None:
                gpa = round(GradeCalculator(instance).calculate_gpa(), 2)
                cache.set(gpa_cache_key, gpa, timeout=60 * 60)
            response["gpa"] = gpa
        return Response(response)

    @action(methods=["post"],
            detail=False,
            serializer_class=ResetPasswordSerializer,
            permission_classes=[],
            url_path="forget-password")
    def forget_password(self, request):
        """
        Email the user with a link to reset the password.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            return Response(
                {"message": "Forget password email sent."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"],
            detail=False,
            serializer_class=ConfirmResetSerializer,
            permission_classes=[],
            url_path="reset-password")
    def reset_password(self, request):
        """
        Reset the password.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistTokenView(CreateAPIView):
    """
    A View for blacklisting tokens.
    """
    serializer_class = BlacklistTokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for marking attendance.
    """
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lecture__users', 'date', 'lecture']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        If the action is 'create', 'update', 'partial_update', or 'destroy',
        only the professor can access the view.
        :return:
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOwnProfessor()]
        if self.action in ['retrieve']:
            return [IsOwnStudentOrProfessor()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role == 2:
                queryset = queryset.filter(lecture__professor=user)
            if user.role in [1, 5]:
                queryset = queryset.filter(user=user)
            if user.role == 4:
                queryset = queryset.filter(
                    user__faculty__department=user.department
                )
            return queryset.select_related(
                "user",
                "lecture"
            )
        return queryset.none()


class CreateEventView(APIView):
    """
    A View for creating timetable in Google calendar.
    """
    permission_classes = [IsStudentOrManagement]

    def get_queryset(self):
        semester = get_semester()
        return Lecture.objects.filter(
            users=self.request.user,
            semester=semester,
        )

    def post(self, request):
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")

        try:
            google_calendar = GoogleCalendar(
                request.user,
                credentials_path
            )
            lectures = self.get_queryset()
            created_events = google_calendar.create_events(lectures)
            return Response(
                {
                    "message": "Events created successfully",
                    "events": created_events
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": f"Error creating events: {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )
