import uuid
import requests
from django.conf import settings


class PayPalOperationsManager:
    def __init__(self):
        self.BASE_URL = settings.PAYPAL_API_BASE_URL
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET

    def _get_paypal_access_token(self):
        """
        Get access token for PayPal API
        :return: access token
        """
        url = f"{self.BASE_URL}/v1/oauth2/token"
        data = {"grant_type": "client_credentials"}
        auth = (self.client_id, self.client_secret)
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=auth
            )
            response = response.json().get("access_token")
        except requests.exceptions.ConnectionError as e:
            response = str(e)
        return response

    def create_paypal_order(self,
                            amount,
                            currency="USD",
                            return_url=None,
                            cancel_url=None):
        """
        Create PayPal order
        :param amount: amount to pay
        :param currency: currency
        :param return_url: return url
        :param cancel_url: cancel url
        :return: response from PayPal API
        """
        token = self._get_paypal_access_token()
        url = f"{self.BASE_URL}/v2/checkout/orders"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        reference_id = str(uuid.uuid4())

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount),
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "EXAMPLE INC",
                        "locale": "en-US",
                        "landing_page": "LOGIN",
                        "shipping_preference": "NO_SHIPPING",
                        "user_action": "PAY_NOW",
                        "return_url": return_url,
                        "cancel_url": cancel_url,
                    }
                }
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response = response.json()
        except requests.exceptions.ConnectionError as e:
            response = str(e)
        return response

    def capture_paypal_order(self, order_id):
        """
        Capture PayPal order.
        :param order_id: Order id.
        :return: Response from PayPal API.
        """
        token = self._get_paypal_access_token()
        url = (f"{self.BASE_URL}/"
               f"v2/checkout/orders/{order_id}/capture")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        try:
            response = requests.post(url, headers=headers)
            print(response)
            response = response.json()
        except requests.exceptions.ConnectionError as e:
            response = str(e)
        return response
