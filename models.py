from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from database import Base

class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    paypal_order_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.CREATED, nullable=False)
    total = Column(Float, nullable=False)
    currency = Column(String, default="EUR", nullable=False)
    
    # Customer information
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_address = Column(Text, nullable=True)
    
    # PayPal response data
    paypal_payer_id = Column(String, nullable=True)
    paypal_payer_email = Column(String, nullable=True)
    paypal_capture_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Product information
    product_name = Column(String, nullable=False)
    product_sku = Column(String, nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationship
    order = relationship("Order", back_populates="items")
