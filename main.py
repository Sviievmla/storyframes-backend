from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import logging

from paypal_pay import create_paypal_order, create_paypal_order_from_amount, capture_paypal_order

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Request models
class CreateOrderRequest(BaseModel):
    total: float
    currency: Optional[str] = "EUR"
    cart: Optional[list] = None

class CaptureOrderRequest(BaseModel):
    orderID: str

@app.get("/products")
def get_products():
    with open("products.json") as f:
        return json.load(f)

@app.post("/pay/paypal")
def paypal_pay(product_id: int):
    """Legacy endpoint for product-based PayPal orders."""
    try:
        return create_paypal_order(product_id)
    except StopIteration:
        raise HTTPException(status_code=404, detail={"error": "Product not found"})
    except Exception as e:
        logger.error(f"Error creating PayPal order for product {product_id}: {str(e)}")
        raise HTTPException(status_code=400, detail={"error": "Failed to create PayPal order"})

@app.post("/api/paypal/create-order")
def create_order(request: CreateOrderRequest):
    """
    Create a PayPal order from checkout cart/total.
    
    Accepts JSON body with:
    - total (required): The total amount for the order
    - currency (optional): Currency code (default: EUR)
    - cart (optional): Cart items for reference
    
    Returns: {"orderID": "..."}
    """
    try:
        result = create_paypal_order_from_amount(request.total, request.currency)
        return result
    except Exception as e:
        logger.error(f"Error creating PayPal order: {str(e)}")
        raise HTTPException(status_code=400, detail={"error": "Failed to create PayPal order"})

@app.post("/api/paypal/capture-order")
def capture_order(request: CaptureOrderRequest):
    """
    Capture a PayPal order by order ID.
    
    Accepts JSON body with:
    - orderID (required): The PayPal order ID to capture
    
    Returns: PayPal capture response
    """
    try:
        result = capture_paypal_order(request.orderID)
        return result
    except Exception as e:
        logger.error(f"Error capturing PayPal order {request.orderID}: {str(e)}")
        raise HTTPException(status_code=400, detail={"error": "Failed to capture PayPal order"})

