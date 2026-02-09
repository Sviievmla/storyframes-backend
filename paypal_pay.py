import json
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from paypal_client import PayPalClient

def create_paypal_order_from_amount(total: float, currency: str = "EUR"):
    """
    Create a PayPal order from a total amount and currency.
    
    Args:
        total: The total amount for the order
        currency: Currency code (default: EUR)
    
    Returns:
        dict: Contains orderID
    """
    request = OrdersCreateRequest()
    request.prefer("return=representation")
    request.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": str(total)
            }
        }]
    })

    client = PayPalClient().get_client()
    response = client.execute(request)

    return {"orderID": response.result.id}

def capture_paypal_order(order_id: str):
    """
    Capture a PayPal order by order ID.
    
    Args:
        order_id: The PayPal order ID to capture
    
    Returns:
        dict: The PayPal capture response
    """
    request = OrdersCaptureRequest(order_id)
    
    client = PayPalClient().get_client()
    response = client.execute(request)
    
    # Return the full capture result
    return {
        "id": response.result.id,
        "status": response.result.status,
        "payer": response.result.payer if hasattr(response.result, 'payer') else None,
        "purchase_units": response.result.purchase_units if hasattr(response.result, 'purchase_units') else None
    }

def create_paypal_order(product_id: int):
    """
    Create a PayPal order from a product ID (legacy endpoint).
    
    Args:
        product_id: The product ID from products.json
    
    Returns:
        dict: Contains orderID
    """
    products = json.load(open("products.json"))
    product = next(p for p in products if p["id"] == product_id)

    # Use the refactored helper function
    return create_paypal_order_from_amount(product["price"], "USD")

