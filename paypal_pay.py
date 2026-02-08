import json
from paypal_checkout_serversdk.orders import OrdersCreateRequest
from paypal_client import PayPalClient

def create_paypal_order(product_id: int):
    products = json.load(open("products.json"))
    product = next(p for p in products if p["id"] == product_id)

    request = OrdersCreateRequest()
    request.prefer("return=representation")
    request.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": str(product["price"])
            }
        }]
    })

    client = PayPalClient().get_client()
    response = client.execute(request)

    return {"orderID": response.result.id}

