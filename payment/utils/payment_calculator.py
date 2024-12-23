from decimal import Decimal
from django.db.models.aggregates import Sum
from utils.helpers import get_semester


class PaymentCalculator:
    def __init__(self, student):
        self.student = student

    def calculate_fee(self):
        """
        Calculate semester fee
        :return: dictionary with fee, government scholarship and courses
        """
        government_scholarship = self.student.government_scholarship
        semester = get_semester()

        courses = self.student.courses.filter(
            lecture__semester=semester
        ).distinct()
        credit = courses.aggregate(credits_sum=Sum("credits"))["credits_sum"]
        fee = 0
        if credit:
            fee = float(credit * 37.5)
            if government_scholarship:
                government_part = float(2250 * government_scholarship / 100)
                fee -= float(government_part / 2)

        payment_dict = {
            "semester_fee": fee,
            "government_scholarship": government_scholarship,
            "courses": courses.values("name", "credits")
        }
        return payment_dict

    def student_payment(self, queryset):
        """
        This function is used to calculate the student payment.
        :param queryset: Payment model queryset
        :return: dictionary with semester fee, government
        scholarship and courses
        """
        semester = get_semester()
        payment_dict = self.calculate_fee()
        semester_fee = float(payment_dict["semester_fee"])
        if queryset.exists():
            has_paid_queryset = queryset.filter(
                amount=semester_fee,
                semester=semester
            )
            if has_paid_queryset.exists():
                return None

            partly_paid_queryset = queryset.filter(
                amount__lt=semester_fee,
                semester=semester
            )
            if partly_paid_queryset.exists():
                total_paid = partly_paid_queryset.aggregate(
                    total_paid=Sum("amount")
                )["total_paid"]
                new_fee = semester_fee - total_paid
                payment_dict.update({"semester_fee": new_fee})
        self.student.loan = payment_dict.get("semester_fee")
        self.student.save()
        return payment_dict
