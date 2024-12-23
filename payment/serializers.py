from rest_framework import serializers
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Payment Serializer to serialize the Payment model
    """
    class Meta:
        model = Payment
        fields = "__all__"