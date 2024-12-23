from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum


class CourseManager(models.Manager):
    """
    This manager class is responsible for finding
    missing prerequisites and failed prerequisites.
    """
    @staticmethod
    def find_missing_prerequisites(course_instance, request):
        """
        This method finds the missing prerequisites for the user.
        :param course_instance: Course instance
        :param request: Request
        :return: QuerySet
        """
        if course_instance.prerequisites.exists():
            missing_prerequisites = (
                course_instance.prerequisites.exclude(users=request.user)
            )
            return missing_prerequisites
        else:
            return None

    @staticmethod
    def find_failed_prerequisites(course_instance, request):
        """
        This method finds the failed prerequisites for the user.
        :param course_instance: Course instance
        :param request: Request
        :return: QuerySet
        """
        from .models import Grade
        if course_instance.prerequisites.exists():
            prerequisite_grades = Grade.objects.filter(
                student=request.user,
                assignment__lecture__course__in=course_instance
                .prerequisites
                .all()
            ).values(
                "assignment__lecture__course__name"
            ).annotate(
                total_grade=Sum("grade"),
                final_exam_grade=Sum(
                    "grade",
                    filter=Q(assignment__name="დასკვნითი გამოცდა")
                )
            )
            if prerequisite_grades.exists():
                failed_prerequisites = prerequisite_grades.filter(
                    Q(
                        final_exam_grade__lt=18
                    ) | Q(
                        final_exam_grade=None
                    ) | Q(
                        total_grade__lt=41
                    )
                )
                return failed_prerequisites
            else:
                return False
        else:
            return None


class LectureManager(models.Manager):
    """
    This manager class is responsible for finding the chosen
    lectures and overlapping lectures.
    """
    def get_chosen_lectures(self, request):
        from utils.helpers import get_semester
        """
        This method finds the chosen lectures for the user.
        :param request: Request instance
        :return: QuerySet
        """
        semester = get_semester()
        chosen_lectures = self.filter(
            users=request.user,
            semester=semester
        )
        return chosen_lectures

    def get_overlapping_lectures(self, lecture_instance, request):
        """
        This method finds the overlapping lectures for the user.
        :param lecture_instance: Lecture instance
        :param request: Request
        :return: QuerySet
        """
        chosen_lectures = self.get_chosen_lectures(request)
        overlapping_lectures = chosen_lectures.filter(
            Q(
                start_time__lt=lecture_instance.end_time
            ) & Q(
                end_time__gt=lecture_instance.start_time
            ),
            day=lecture_instance.day,
            users=request.user
        ).exclude(id=lecture_instance.id)
        return overlapping_lectures
