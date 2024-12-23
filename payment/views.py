from decimal import Decimal
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from payment.utils.payment_calculator import PaymentCalculator
from payment.models import Payment
from payment.permissions import IsStudentOrManagement
from payment.serializers import PaymentSerializer
from django.urls import reverse
from payment.utils.paypal_operations import PayPalOperationsManager
from user.models import User
from utils.helpers import get_semester


class PaymentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows payments to be viewed.
    Student can view only his payments and staff can view all payments.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsStudentOrManagement]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and isinstance(user, User):
            if user.role == 4:
                return Payment.objects.filter(
                    user__faculty__department=user.department
                )
            elif user.role == 3:
                return Payment.objects.all()
        return Payment.objects.filter(user=user)

    @action(detail=False, methods=["get"])
    def current_fee(self, request):
        """
        API endpoint that allows to calculate the current semester fee.
        """
        user = request.user

        if user.is_staff:
            return Response(
                {"error": "Staff members can't pay the semester fee"},
                status=400
            )

        queryset = self.get_queryset()
        try:
            payment_dict = PaymentCalculator(user).student_payment(queryset)
            if payment_dict is None:
                return Response(
                    {"error": "You have already paid the semester fee"},
                    status=400
                )
            return Response(payment_dict)
        except Exception as e:
            return Response(
                {"error": "No courses found for this semester"}, status=400
            )


class PayPalCreateOrderView(APIView):
    """
    API endpoint that allows to create a new PayPal order.
    """
    permission_classes = [IsStudentOrManagement]

    def post(self, request):
        user = request.user
        queryset = Payment.objects.filter(user=user)
        try:
            amount = PaymentCalculator(
                user
            ).student_payment(
                queryset
            )["semester_fee"]
        except Exception as e:
            return Response(
                {"error": "No courses found for this semester"},
                status=400
            )

        return_url = request.build_absolute_uri(
            reverse("payment:payment_success")
        )
        cancel_url = request.build_absolute_uri(
            reverse("payment:payment_failed")
        )

        try:
            order = PayPalOperationsManager().create_paypal_order(
                amount,
                return_url=return_url,
                cancel_url=cancel_url
            )
            return Response(order)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class PayPalCaptureOrderView(APIView):
    """
    API endpoint that allows to capture a PayPal order.
    """
    permission_classes = [IsStudentOrManagement]

    def post(self, request):
        order_id = request.data.get("order_id")
        try:
            capture = PayPalOperationsManager().capture_paypal_order(order_id)
            payments = capture["purchase_units"][0]["payments"]
            amount = (
                payments["captures"][0]["amount"]["value"]
            )
            amount = float(amount)
            if capture.get("status") == "COMPLETED":
                semester = get_semester()
                payment = Payment.objects.create(
                    order_id=order_id,
                    amount=amount,
                    user=request.user,
                    semester=semester,
                )
                payment.save()
                request.user.loan -= Decimal(amount)
                request.user.save()
            return Response(capture)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class payment_success(APIView):
    """
    API endpoint that allows to show a success message.
    """
    def get(self, request):
        return Response(
            {
                "success": True,
                "msg": "payment has been successfully completed"
            },
            status=200
        )


class payment_failed(APIView):
    """
    API endpoint that allows to show a failed message.
    """
    def get(self, request):
        return Response(
            {"success": False, "msg": "payment has been failed"}, status=400
        )
