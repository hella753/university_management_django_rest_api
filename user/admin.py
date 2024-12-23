from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User, Attendance


@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            "fields": ("username",
                       "email",
                       "first_name",
                       "last_name",
                       "password1",
                       "password2"),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ("Profile Info", {"fields": (
            "image",
            "identity_number",
            "enrollment_year",
            "faculty",
            "phone",
            "lectures",
            "date_of_birth",
            "government_scholarship",
            "courses",
            "loan",
            "role",
            "department",
        )
        }),
    )

    list_display = (
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "faculty",
        "role",
        "department",
    )
    list_select_related = ("faculty", "department")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "first_hour", "second_hour", "third_hour")
    list_filter = ("date",)
    search_fields = ("user__username", "user__first_name", "user__last_name")
    date_hierarchy = "date"
    ordering = ("date",)
