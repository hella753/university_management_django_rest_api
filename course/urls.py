from django.urls import path
from rest_framework.routers import DefaultRouter
from course.views import LectureViewSet, CourseViewSet, FacultyViewSet, DepartmentViewSet, GradeViewSet, \
    AssignmentViewSet, AuditoriumViewSet, CreateSyllabusView, SemesterViewSet, ResourceViewSet, GradeRecordViewSet, \
    AssignmentSubmissionViewSet

app_name = "course"
router = DefaultRouter()

router.register(r"course", CourseViewSet, basename="course")
router.register(r"lecture", LectureViewSet, basename="lecture")
router.register(r"faculty", FacultyViewSet, basename="faculty")
router.register(r"department", DepartmentViewSet, basename="department")
router.register(r"grade", GradeViewSet, basename="grade")
router.register(r"assignment", AssignmentViewSet, basename="assignment")
router.register(r"auditorium", AuditoriumViewSet, basename="auditorium")
router.register(r"semester", SemesterViewSet, basename="semester")
router.register(r"resource", ResourceViewSet, basename="resource")
router.register(r"grade-record", GradeRecordViewSet, basename="grade_record")
router.register(r"assignment-submission", AssignmentSubmissionViewSet, basename="assignment_submission")

urlpatterns = router.urls
urlpatterns += [
    path("syllabus/", CreateSyllabusView.as_view(), name="syllabus"),
]
