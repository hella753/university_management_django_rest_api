from celery import shared_task
from django.db.models import Sum
from course.utils.grade_calculator import GradeCalculator
from payment.utils.payment_calculator import PaymentCalculator
from course.models import Grade, GradeRecord, Lecture
from user.models import User


@shared_task
def deactivate_student_status():
    """
    Deactivate student status for students who have not
    paid for the current year and semester.
    """
    students = User.objects.filter(is_active=True, role=1)
    for student in students:
        queryset = student.payments.all()
        if queryset.exists():
            PaymentCalculator(student).student_payment(queryset)
    students.filter(
        loan__gt=0,
    ).update(is_active=False)


@shared_task
def add_grade_record(student, lecture):
    """
    Add grade record for students
    :param: student - User object
    :param: lecture - Lecture object
    """
    student = User.objects.filter(pk=student).first()
    lecture = Lecture.objects.filter(pk=lecture).first()
    if lecture.name in ["საბაკალავრო ნაშრომი",
                        "სამაგისტრო ნაშრომი",
                        "Master Thesis",
                        "Bachelor Thesis"]:
        total_grade = Grade.objects.filter(
            assignment__lecture=lecture,
            student=student
        ).first().grade
        failed = False
        if total_grade < 51:
            failed = True
    else:
        grade_calculator = GradeCalculator(student)
        grades = grade_calculator.calculate_grade(lecture)
        final_exam_grade = grades["final_exam"]
        total_grade = grades["final_grade"]
        failed = False
        if total_grade < 51:
            failed = True
        if final_exam_grade < 18:
            failed = True
    instance, created = GradeRecord.objects.get_or_create(
        student=student,
        lecture=lecture,
        failed=failed,
        defaults={"grade": total_grade}
    )
    if not created:
        instance.grade = total_grade
        instance.save()


@shared_task
def make_graduate():
    """
    Change a Student group to a graduate group for students who have graduated
    """
    users = User.objects.filter(is_active=True)
    students = users.filter(role=1)

    for student in students:
        student_records = GradeRecord.objects.filter(
            student=student,
            is_active=True
        ).all()
        if student_records:
            masters = student_records.filter(
                lecture__name__in=["სამაგისტრო ნაშრომი", "Master Thesis"]
            )
            bachelors = student_records.filter(
                lecture__name__in=["საბაკალავრო ნაშრომი", "Bachelor Thesis"]
            )
            print(bachelors)
            if masters.exists():
                print("masters exists")
                if not masters.first().failed:
                    student_records = student_records.filter(
                        lecture__uni_year__in=[5, 6]
                    )
                    total_credits = student_records.aggregate(
                        total_credits=Sum("lecture__course__credits")
                    )
                    if total_credits["total_credits"] >= 120:
                        student.role = 5
                        student.save()
            elif bachelors.exists():
                if not bachelors.first().failed:
                    total_credits = student_records.aggregate(
                        total_credits=Sum("lecture__course__credits")
                    )
                    if total_credits["total_credits"] >= 240:
                        student.role = 5
                        student.save()
