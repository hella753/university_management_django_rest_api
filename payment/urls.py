from django.urls import path
from rest_framework.routers import DefaultRouter
from payment import views

app_name = "payment"
router = DefaultRouter()
router.register("payment", views.PaymentViewSet, basename="payment")
urlpatterns = router.urls

urlpatterns += [
    path("payment_success/", views.payment_success.as_view(), name="payment_success"),
    path("payment_failed/", views.payment_failed.as_view(), name="payment_failed"),
    path("paypal/create-order/", views.PayPalCreateOrderView.as_view(), name="paypal-create-order"),
    path("paypal/capture-order/", views.PayPalCaptureOrderView.as_view(), name="paypal-capture-order"),
]