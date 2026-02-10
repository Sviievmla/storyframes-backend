import os
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PayPalClient:
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.mode = os.getenv("PAYPAL_MODE", "sandbox").lower()

        # Choose environment based on mode
        if self.mode == "live":
            self.environment = LiveEnvironment(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        else:
            self.environment = SandboxEnvironment(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        
        self.client = PayPalHttpClient(self.environment)

    def get_client(self):
        return self.client

