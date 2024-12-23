from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from course.models import *


@admin.register(Faculty)
class FacultyAdmin(TabbedTranslationAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_filter = ("name", "code")


@admin.register(Department)
class DepartmentAdmin(TabbedTranslationAdmin):
    list_display = ("name", "code")
    list_filter = ("name", "code")


@admin.register(Course)
class CourseAdmin(TabbedTranslationAdmin):
    list_display = ("name", "code", "department")
    search_fields = ("name", "code")
    list_filter = ("department",)
    list_select_related = ("department",)


@admin.register(Lecture)
class LectureAdmin(TabbedTranslationAdmin):
    list_display = ("course__code",
                    "name",
                    "day",
                    "start_time",
                    "end_time",
                    "location",
                    "professor",
                    "uni_year",
                    "semester")
    list_filter = ("name", "course")
    list_select_related = ("course", "professor", "location", "semester")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student",
                    "grade",
                    "assignment",
                    "assignment__lecture__name",
                    "assignment__due_date")
    list_select_related = ("student", "assignment", "assignment__lecture")


@admin.register(Assignment)
class AssignmentAdmin(TabbedTranslationAdmin):
    list_display = ("name", "lecture", "due_date")
    list_select_related = ("lecture",)


@admin.register(AssignmentSubmission)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("student", "assignment__lecture")
    list_select_related = ("student", "assignment", "assignment__lecture")


@admin.register(Resource)
class ResourceAdmin(TabbedTranslationAdmin):
    list_display = ("name",)


@admin.register(Auditorium)
class AuditoriumAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "has_computers")
    list_filter = ("name", "capacity", 'has_computers')


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    list_display = ('grade', 'student', 'lecture', 'failed', 'is_active')


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester', 'start_date', 'end_date')
    list_filter = ('semester', 'start_date', 'end_date')