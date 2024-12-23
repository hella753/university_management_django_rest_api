from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from payment.permissions import IsStudentOrManagement
from .permissions import *
from .serilalizers import *
from .models import *
from .utils.grade_calculator import GradeCalculator
from .utils.syllabus_generator import SyllabusGenerator


class LectureViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the lecture operations.

    If the user is professor, they can see the lectures that they are teaching.
    They are allowed to update their lectures syllabus and resources.

    If the user is manager, they can see the lectures that are in
    their department.
    They are allowed to create, update, partial_update and destroy
    the lecture.

    If the user is admin, they can see everything.

    If the user is a student, they can see the lectures that are
    in their department.
    They are allowed to see the list of lecture and register/unregister
    the lecture.
    """
    serializer_class = LectureDisplaySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course",
                        "professor__username",
                        "users__username",
                        "semester"]
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        If the user is a professor, he is able to edit
        the lecture syllabus and resources.
        """
        user = self.request.user
        if user.is_authenticated and isinstance(user, User):
            if self.action in ["update", "partial_update"]:
                if user.role == 2:
                    return LectureProfessorSerializer
            if self.action in ["create", "update", "partial_update"]:
                return LectureModificationSerializer
        return super().get_serializer_class()

    @action(detail=True,
            methods=["post"],
            serializer_class=RegisterLectureSerializer,
            permission_classes=[RestrictAfterTwoWeeks])
    def register_lecture(self, request, pk=None):
        """
        This action registers the lecture for the user.
        """
        lecture_id = pk
        serializer = RegisterLectureSerializer(
            data={"lecture_id": lecture_id},
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                "You registered/unregistered the subject successfully",
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_queryset(self):
        user = self.request.user
        queryset = Lecture.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role in [1, 5]:
                queryset = Lecture.objects.filter(
                    course__department__in=[
                        user.faculty.department,
                    ]
                )
            elif user.role == 4:
                queryset = Lecture.objects.filter(
                    course__department__in=[
                        user.department
                    ]
                )
            elif user.role == 2:
                queryset = Lecture.objects.filter(professor=self.request.user)
        return queryset.prefetch_related(
            "resources",
            "professor",
            "professor__department",
            "course",
            "course__department",
            "course__prerequisites",
            "course__prerequisites__prerequisites",
        ).all()

    @action(detail=True, methods=["get"])
    def final_grade(self, request, pk=None):
        """
        This action calculates the final grade for the subject
        and current student.
        """
        lecture = self.get_object()
        if lecture not in request.user.lectures.all():
            return Response(
                "You are not registered to this lecture",
                status=status.HTTP_400_BAD_REQUEST
            )
        grade_calculator = GradeCalculator(request.user)
        final_cache_key = f"final_grade_{request.user.id}_{lecture.id}"
        final_grade = cache.get(final_cache_key)
        if not final_grade:
            final_grade = grade_calculator.calculate_grade(lecture)
            cache.set(final_cache_key, final_grade, 60 * 10)
        grade_points_cache_key = f"grade_point_{final_grade["final_grade"]}"
        grade_points = cache.get(grade_points_cache_key)
        if not grade_points:
            grade_points = grade_calculator.calculate_subject_grade_point(
                final_grade["final_grade"]
            )
            cache.set(grade_points_cache_key, grade_points, 60 * 10)

        response = {**final_grade, **grade_points}
        return Response(
            response,
            status=status.HTTP_200_OK
        )

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and isinstance(user, User):
            if self.action in ["update", "partial_update"] and user.role == 2:
                return [IsThisLecturesProfessor()]
            if self.action in [
                "create",
                "update",
                "partial_update",
                "destroy"
            ]:
                return [IsManagement()]
        return super().get_permissions()


class CourseViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the course operations.

    If the user is professor, they can see the courses that they are teaching.

    If the user is manager, they can see the courses that are in
    their department.
    They are allowed to create, update, partial_update and destroy
    the course.

    If the user is admin, they can see all the courses.
    They are allowed to create, update, partial_update and destroy the course.

    If the user is a student, they can see the courses that are in
    their department.
    """
    serializer_class = CourseDisplaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department", "users__username", "lecture__semester"]

    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CourseModificationSerializer
        return CourseDisplaySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsManagement()]
        return super().get_permissions()

    @action(detail=True,
            methods=["post"],
            serializer_class=RegisterCourseSerializer,
            permission_classes=[RestrictAfterTwoWeeks])
    def register_course(self, request, pk=None):
        """
        This action registers the course for the student.
        """
        course_id = pk
        serializer = RegisterCourseSerializer(
            data={"course_id": course_id},
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                "You registered/unregistered the course successfully",
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_200_OK
        )

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role in [1, 5]:
                queryset = Course.objects.filter(
                    department__in=[
                        user.faculty.department,
                    ]
                )
            if user.role == 4:
                queryset = Course.objects.filter(
                    department=user.department
                )
            if user.role == 2:
                queryset = Course.objects.filter(
                    lecture__in=user.lectures
                )
        return queryset.select_related(
            "department"
        ).prefetch_related(
            "prerequisites",
            "prerequisites__prerequisites"
        )


class FacultyViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the faculty operations.

    Only Admin can see, create, update, partial_update and destroy the faculty.
    """
    queryset = Faculty.objects.select_related("department").all()
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FacultyModificationSerializer
        return FacultyDisplaySerializer


class DepartmentViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the department operations.

    Only Admin can see, create, update, partial_update and destroy
    the department.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUser]


class GradeViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the grade operations.

    If the user is professor, they can see the grades that they gave.
    They are allowed to create, update, partial_update and destroy
    their created grade.

    If the user is in manager, they can see the grades that are in
    their department.
    They are allowed to create, update, partial_update and destroy
    the grade.

    It the user is admin, they can see and modify all grades.

    If the user is a student, they can see their grades.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "student__username",
        "assignment__lecture",
        "assignment__lecture__professor__username"
    ]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return GradeModificationSerializer
        return GradeDisplaySerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and isinstance(user, User):
            if self.action == "create":
                return [IsProfessorOrManagement()]
            if self.action in ["update", "partial_update", "destroy"]:
                return [IsCreatorOfGradeOrManagement()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = Grade.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role == 2:
                queryset = Grade.objects.filter(
                    assignment__lecture__professor=self.request.user
                )
            elif user.role == 4:
                queryset = Grade.objects.filter(
                    assignment__lecture__course__department__in=[
                        user.department,
                    ]
                )
            elif user.role in [1, 5]:
                queryset = Grade.objects.filter(student=user)
        return queryset.select_related(
            "student",
            "assignment"
        ).prefetch_related(
            "assignment__lecture",
            "assignment__lecture__professor",
            "assignment__lecture__resources",
            "assignment__lecture__course",
            "assignment__lecture__course__department",
            "assignment__lecture__course__prerequisites",
            "assignment__lecture__course__prerequisites__prerequisites"
        )


class AssignmentViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the assignment operations.

    If the user is professor, they can see the assignments that they created.
    They are allowed to create, update, partial_update and destroy
    their created assignment.

    If the user is manager, they can see the assignments that are
    in their department.
    They are allowed to create, update, partial_update and destroy
    the grade.

    If the user is admin, they can see and modify all assignments.

    If the user is a student, they can see the assignments that are in
    their department.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["lecture"]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return AssignmentModificationSerializer
        return AssignmentDisplaySerializer

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated:
            if self.action == 'create':
                return [IsProfessorOrManagement()]
            if self.action in ['update', 'partial_update', 'destroy']:
                return [IsCreatorOfAssignmentOrManagement()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        queryset = Assignment.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role == 2:
                queryset = Assignment.objects.filter(lecture__professor=user)
            if user.role == 4:
                queryset = Assignment.objects.filter(
                    lecture__course__department__in=[
                        user.department
                    ]
                )
            if user.role in [1, 5]:
                queryset = Assignment.objects.filter(
                    lecture__users=self.request.user
                )
        return queryset.prefetch_related(
            "lecture",
            "lecture__professor",
            "lecture__resources",
            "lecture__course",
            "lecture__course__department",
            "lecture__course__prerequisites",
            "lecture__course__prerequisites__prerequisites"
        )


class AuditoriumViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the auditorium operations.

    Only Admin and Manager can see, create, update, partial_update
    and destroy the auditorium.
    """
    queryset = Auditorium.objects.all()
    serializer_class = AuditoriumSerializer
    permission_classes = [IsManagement]


class CreateSyllabusView(APIView):
    """
    This APIView class is responsible for creating the syllabus for the course.
    If the user is professor/manager/admin, he is allowed to
    create the syllabus.

    Use test_syllabus.json file for testing this APIView.
    """
    serializer_class = SyllabusSerializer
    permission_classes = [IsProfessorOrManagement]

    def post(self, request):
        """
        This method creates the syllabus for the course.
        """
        serializer = SyllabusSerializer(data=request.data)
        if serializer.is_valid():
            try:
                syllabus_generator = (
                    SyllabusGenerator(serializer.validated_data)
                )
                output_path = syllabus_generator.generate_syllabus()
                download_url = (f"{request.scheme}://"
                                f"{request.get_host()}/"
                                f"{output_path}")
                return Response(
                    {"download_url": download_url},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SemesterViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the semester operations.

    Only Admin can see, create, update, partial_update and
    destroy the semester.
    """
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAdminUser]


class ResourceViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the resource operations.

    If the user is professor, they can see the resources that they created.
    And they are allowed to create, update, partial_update and
    destroy their created resource.

    If the user is manager, they can see and modify the resources
    that are in their department.

    If the user is admin, they can see and modify all resources.
    """
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lecture', 'lecture__professor__username']

    def get_queryset(self):
        user = self.request.user
        queryset = Resource.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role == 2:
                queryset = Resource.objects.filter(lecture__professor=user)
            if user.role == 4:
                queryset = Resource.objects.filter(
                    lecture__course__department__in=[
                       user.department
                    ]
                )
            if user.role in [1, 5]:
                queryset = Resource.objects.filter(lecture__users=user)
        return queryset

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated:
            if self.action == 'create':
                return [IsProfessorOrManagement()]
            if self.action in ['update', 'partial_update', 'destroy']:
                return [IsThisLecturesProfessor()]
        return super().get_permissions()


class GradeRecordViewSet(ListModelMixin, GenericViewSet):
    """
    This ViewSet class is responsible for handling the grade record operations.

    If the user is a student, they can see their grade records.

    If the user is manager, they can see the grade records that
    are in their department.

    If the user is admin, they can see all grade records.
    """
    serializer_class = GradeRecordSerializer
    permission_classes = [IsStudentOrManagement]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student__username"]

    def get_queryset(self):
        user = self.request.user
        queryset = GradeRecord.objects.all()
        if user.is_authenticated and isinstance(user, User):
            if user.role in [1, 5]:
                queryset = GradeRecord.objects.filter(student=user)
            if user.role == 4:
                queryset = GradeRecord.objects.filter(
                    student__faculty__department=user.department
                )
            if user.role == 2:
                queryset = queryset.none()
        return queryset.select_related(
            "student",
            "lecture"
        )


class AssignmentSubmissionViewSet(ModelViewSet):
    """
    This ViewSet class is responsible for handling the assignment
    submission operations.

    If the user is a student, they can create and see their assignment
    submissions.

    If the user is a professor, they can see the assignment submissions
    that are submitted to them.
    They are allowed to create, update, partial_update and destroy their
    created assignment submission.

    If the user is a manager, they can see the assignment submissions
    that are in their department.
    They are allowed to create, update, partial_update and destroy
    the assignment submission.

    If the user is admin, they can see and modify all assignment submissions.
    """
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["assignment",
                        "assignment__lecture__professor__username"]

    def get_queryset(self):
        user = self.request.user
        queryset = AssignmentSubmission.objects.all()

        if user.is_authenticated and isinstance(user, User):
            if user.role == 2:
                queryset = AssignmentSubmission.objects.filter(
                    assignment__lecture__professor=user
                )
            if user.role == 4:
                queryset = AssignmentSubmission.objects.filter(
                    assignment__lecture__course__department=user.department
                )
            if user.role in [1, 5]:
                queryset = AssignmentSubmission.objects.filter(student=user)

        return queryset.prefetch_related(
            "assignment",
            "assignment__lecture",
            "assignment__lecture__professor",
            "assignment__lecture__resources",
            "assignment__lecture__course",
            "assignment__lecture__course__department",
            "assignment__lecture__course__prerequisites",
            "assignment__lecture__course__prerequisites__prerequisites"
        )

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and isinstance(user, User):
            if self.action == 'create':
                return [IsStudentOrManagement()]
            if self.action in ['update', 'partial_update', 'destroy']:
                return [IsCreatorOfAssignmentSubmissionOrManagement()]
        return super().get_permissions()
