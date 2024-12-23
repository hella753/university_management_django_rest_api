from modeltranslation.translator import register, TranslationOptions
from .models import Course, Department, Faculty, Lecture, Assignment, Resource


@register(Course)
class CourseTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Faculty)
class FacultyTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Lecture)
class LectureTranslationOptions(TranslationOptions):
    fields = ("name", "day")


@register(Assignment)
class AssignmentTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Resource)
class ResourcesTranslationOptions(TranslationOptions):
    fields = ("name",)