from django.db import models
from django.utils.translation import gettext_lazy as _

class Payment(models.Model):
    """
    Payment model to store payment details
    """
    order_id = models.CharField(max_length=255, verbose_name=_("გადახდის კოდი"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("თანხა"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("შექმნილია"))
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="payments", verbose_name=_("მომხმარებელი"))
    semester = models.ForeignKey("course.Semester", on_delete=models.CASCADE, related_name="payments", verbose_name=_("სემესტრი"))