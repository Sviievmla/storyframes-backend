import os
from paypal_checkout_serversdk.core import PayPalHttpClient, SandboxEnvironment

class PayPalClient:
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

        self.environment = SandboxEnvironment(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        self.client = PayPalHttpClient(self.environment)

    def get_client(self):
        return self.client

