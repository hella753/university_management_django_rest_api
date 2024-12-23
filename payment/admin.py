from django.contrib import admin
from payment.models import Payment


@admin.register(Payment)
class Payment(admin.ModelAdmin):
    list_display = ["order_id",
                    "amount",
                    "created_at",
                    "user",
                    "semester"]
