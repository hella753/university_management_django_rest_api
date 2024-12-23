from django.db.models.aggregates import Sum
from course.models import Grade


class GradeCalculator:
    """
    This class is responsible for calculating the final grade
    and GPA for the given user.
    """
    def __init__(self, user):
        """
        This function initializes the GradeCalculator class.
        :param user: User object
        """
        self.user = user

    def calculate_grade(self, lecture):
        """
        This function calculates the final grade for the given lecture.
        :param lecture: Lecture object
        :return: Dictionary with subject, final grade and final exam grade
        """
        grade = Grade.objects.filter(
            student=self.user,
            assignment__lecture=lecture
        ).values(
            "assignment__lecture"
        ).annotate(total_grade=Sum(
            "grade")
        )
        final_exam = Grade.objects.filter(
            assignment__name__in=["დასკვნითი გამოცდა", "Final Exam"],
            student=self.user,
            assignment__lecture=lecture
        ).first()
        if not grade:
            return {
                "subject": lecture.name,
                "final_grade": 0,
                "final_exam": 0
            }
        return {
            "subject": lecture.name,
            "final_grade": grade[0]["total_grade"],
            "final_exam": final_exam.grade
        }

    @staticmethod
    def calculate_subject_grade_point(grade):
        """
        This function calculates the grade point for the given grade.
        :param grade: Grade value
        :return: Dictionary with grade and letter
        """
        match grade:
            case g if 90 <= g <= 100:
                return {
                    "grade_point": 4.0,
                    "letter": "A"
                }
            case g if 80 <= g < 90:
                return {
                    "grade_point": 3.0,
                    "letter": "B"
                }
            case g if 70 <= g < 80:
                return {
                    "grade_point": 2.0,
                    "letter": "C"
                }
            case g if 60 <= g < 70:
                return {
                    "grade_point": 1.0,
                    "letter": "D"
                }
            case _:
                return {
                    "grade_point": 0.0,
                    "letter": "F"
                }

    def calculate_gpa(self):
        """
        This function calculates the GPA for the given user.
        :return: Decimal GPA value
        """
        # Get all grades and credits for the given user
        grades_and_credits = Grade.objects.filter(
            student=self.user,
            assignment__lecture__course__in=self.user.courses.all()
        ).values(
            "assignment__lecture__course",
            "assignment__lecture__course__credits"
        ).annotate(
            total_grade=Sum('grade'),
        )

        # Calculate total grade points and total credits
        total_grade_points = sum(
            [self.calculate_subject_grade_point(
                item["total_grade"]
            )["grade_point"]
             * item[
                 "assignment__lecture__course__credits"
             ] for item in grades_and_credits]
        )
        total_credits = sum(
            [item[
                 "assignment__lecture__course__credits"
             ] for item in grades_and_credits]
        )
        if total_credits == 0:
            return 0
        gpa = total_grade_points / total_credits
        return gpa
