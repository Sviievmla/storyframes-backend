from fastapi import FastAPI
import json
from paypal_pay import create_paypal_order

app = FastAPI()

@app.get("/products")
def get_products():
    return json.load(open("products.json"))

@app.post("/pay/paypal")
def paypal_pay(product_id: int):
    return create_paypal_order(product_id)

