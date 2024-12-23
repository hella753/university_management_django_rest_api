from django.urls import path
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, AttendanceViewSet, CreateEventView

app_name = "user"

router = DefaultRouter()
router.register(r"user", UserViewSet, basename="user")
router.register(r"attendance", AttendanceViewSet, basename="attendance")

urlpatterns = router.urls

urlpatterns += [
    path("create-event/", CreateEventView.as_view(), name="create_event"),
]