from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from paypal_pay import create_paypal_order, create_paypal_order_from_amount, capture_paypal_order
from database import engine, get_db, Base
from models import Order, OrderItem, OrderStatus
from email_service import email_service

# Create database tables
Base.metadata.create_all(bind=engine)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Storyframes Backend API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mystoryframes.shop",
        "https://www.mystoryframes.shop",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class CustomerInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CartItem(BaseModel):
    product_name: str
    product_sku: Optional[str] = None
    quantity: int = 1
    unit_price: float
    total_price: float

class CreateOrderRequest(BaseModel):
    total: float
    currency: Optional[str] = "EUR"
    cart: Optional[List[CartItem]] = None
    customerInfo: Optional[CustomerInfo] = None

class CaptureOrderRequest(BaseModel):
    orderID: str

# Health check endpoint
@app.get("/")
@app.get("/health")
def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy", "service": "storyframes-backend"}

@app.get("/products")
def get_products():
    """Get all available products."""
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
def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    Create a PayPal order from checkout cart/total.
    
    Accepts JSON body with:
    - total (required): The total amount for the order
    - currency (optional): Currency code (default: EUR)
    - cart (optional): Cart items for reference
    - customerInfo (optional): Customer details
    
    Returns: {"id": "paypal_order_id", "status": "CREATED"}
    """
    try:
        # Create PayPal order
        result = create_paypal_order_from_amount(request.total, request.currency)
        paypal_order_id = result["orderID"]
        
        # Store order in database
        db_order = Order(
            paypal_order_id=paypal_order_id,
            status=OrderStatus.CREATED,
            total=request.total,
            currency=request.currency,
            customer_name=request.customerInfo.name if request.customerInfo else None,
            customer_email=request.customerInfo.email if request.customerInfo else None,
            customer_phone=request.customerInfo.phone if request.customerInfo else None,
            customer_address=request.customerInfo.address if request.customerInfo else None,
        )
        db.add(db_order)
        db.flush()  # Get the order ID
        
        # Store cart items if provided
        if request.cart:
            for item in request.cart:
                db_item = OrderItem(
                    order_id=db_order.id,
                    product_name=item.product_name,
                    product_sku=item.product_sku,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                )
                db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        
        logger.info(f"Created order #{db_order.id} with PayPal order ID: {paypal_order_id}")
        
        return {
            "id": paypal_order_id,
            "status": "CREATED"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating PayPal order: {str(e)}")
        raise HTTPException(status_code=400, detail={"error": "Failed to create PayPal order"})

@app.post("/api/paypal/capture-order")
def capture_order(request: CaptureOrderRequest, db: Session = Depends(get_db)):
    """
    Capture a PayPal order by order ID.
    
    Accepts JSON body with:
    - orderID (required): The PayPal order ID to capture
    
    Returns: {"status": "COMPLETED", "orderID": string}
    """
    db_order = None
    try:
        # Capture PayPal payment
        result = capture_paypal_order(request.orderID)
        
        # Find order in database
        db_order = db.query(Order).filter(Order.paypal_order_id == request.orderID).first()
        
        if not db_order:
            logger.warning(f"Order not found in database for PayPal order ID: {request.orderID}")
            # Still return success if PayPal capture succeeded
            return {
                "status": result.get("status", "COMPLETED"),
                "orderID": request.orderID
            }
        
        # Update order status
        db_order.status = OrderStatus.COMPLETED
        db_order.completed_at = datetime.now(timezone.utc)
        
        # Store PayPal payer information if available
        if result.get("payer"):
            payer = result["payer"]
            if "payer_id" in payer:
                db_order.paypal_payer_id = payer["payer_id"]
            if "email_address" in payer:
                db_order.paypal_payer_email = payer["email_address"]
        
        # Store capture ID
        if result.get("purchase_units") and len(result["purchase_units"]) > 0:
            captures = result["purchase_units"][0].get("payments", {}).get("captures", [])
            if captures and len(captures) > 0:
                db_order.paypal_capture_id = captures[0].get("id")
        
        db.commit()
        db.refresh(db_order)
        
        logger.info(f"Order #{db_order.id} captured successfully")
        
        # Send confirmation emails
        try:
            order_data = {
                "id": db_order.id,
                "paypal_order_id": db_order.paypal_order_id,
                "status": db_order.status.value,
                "total": db_order.total,
                "currency": db_order.currency,
                "customer_name": db_order.customer_name,
                "customer_email": db_order.customer_email,
                "customer_phone": db_order.customer_phone,
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "total_price": item.total_price,
                        "currency": db_order.currency
                    }
                    for item in db_order.items
                ]
            }
            
            # Send customer confirmation
            if db_order.customer_email:
                email_service.send_order_confirmation(order_data, db_order.customer_email)
            
            # Send admin notification
            email_service.send_admin_notification(order_data)
        except Exception as e:
            logger.error(f"Error sending confirmation emails: {str(e)}")
            # Don't fail the capture if email fails
        
        return {
            "status": result.get("status", "COMPLETED"),
            "orderID": request.orderID
        }
    except Exception as e:
        if db_order:
            db_order.status = OrderStatus.FAILED
            db.commit()
        logger.error(f"Error capturing PayPal order {request.orderID}: {str(e)}")
        raise HTTPException(status_code=400, detail={"error": "Failed to capture PayPal order"})

@app.get("/api/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order details by order ID."""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail={"error": "Order not found"})
    
    return {
        "id": db_order.id,
        "paypal_order_id": db_order.paypal_order_id,
        "status": db_order.status.value,
        "total": db_order.total,
        "currency": db_order.currency,
        "customer_name": db_order.customer_name,
        "customer_email": db_order.customer_email,
        "customer_phone": db_order.customer_phone,
        "customer_address": db_order.customer_address,
        "created_at": db_order.created_at.isoformat() if db_order.created_at else None,
        "updated_at": db_order.updated_at.isoformat() if db_order.updated_at else None,
        "completed_at": db_order.completed_at.isoformat() if db_order.completed_at else None,
        "items": [
            {
                "id": item.id,
                "product_name": item.product_name,
                "product_sku": item.product_sku,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
            }
            for item in db_order.items
        ]
    }

@app.get("/api/orders")
def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all orders (admin endpoint).
    
    Query parameters:
    - skip: Number of orders to skip (default: 0)
    - limit: Maximum number of orders to return (default: 100, max: 1000)
    - status: Filter by order status (optional)
    """
    # Limit the maximum number of results
    limit = min(limit, 1000)
    
    query = db.query(Order)
    
    # Filter by status if provided
    if status:
        try:
            status_enum = OrderStatus(status.upper())
            query = query.filter(Order.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail={"error": f"Invalid status: {status}"})
    
    # Order by most recent first
    query = query.order_by(Order.created_at.desc())
    
    # Apply pagination
    orders = query.offset(skip).limit(limit).all()
    
    return {
        "orders": [
            {
                "id": order.id,
                "paypal_order_id": order.paypal_order_id,
                "status": order.status.value,
                "total": order.total,
                "currency": order.currency,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "completed_at": order.completed_at.isoformat() if order.completed_at else None,
                "item_count": len(order.items)
            }
            for order in orders
        ],
        "count": len(orders),
        "skip": skip,
        "limit": limit
    }

