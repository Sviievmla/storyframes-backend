# API Reference

Complete API documentation for the Storyframes Backend API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-app.onrender.com` or `https://api.mystoryframes.shop`

## Authentication

No authentication required for the current version. All endpoints are public.

> **Note**: Consider adding API key authentication for the admin endpoints (`/api/orders`) in production.

---

## Endpoints

### Health & Status

#### `GET /` or `GET /health`

Check if the API is running.

**Response**
```json
{
  "status": "healthy",
  "service": "storyframes-backend"
}
```

---

### Products

#### `GET /products`

Get list of available products.

**Response**
```json
[
  {
    "id": 1,
    "name": "Product 1",
    "price": 19.99
  },
  {
    "id": 2,
    "name": "Product 2",
    "price": 29.99
  }
]
```

---

### PayPal Payment

#### `POST /api/paypal/create-order`

Create a PayPal order with customer information and cart items.

**Request Body**
```json
{
  "total": 29.99,
  "currency": "EUR",
  "cart": [
    {
      "product_name": "Custom Frame",
      "product_sku": "FRAME-001",
      "quantity": 1,
      "unit_price": 29.99,
      "total_price": 29.99
    }
  ],
  "customerInfo": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "address": "123 Main St, City, Country"
  }
}
```

**Fields**
- `total` (required, number): Total amount for the order
- `currency` (optional, string): Currency code (default: "EUR")
- `cart` (optional, array): Array of cart items
  - `product_name` (required, string): Name of the product
  - `product_sku` (optional, string): Product SKU
  - `quantity` (required, integer): Quantity
  - `unit_price` (required, number): Unit price
  - `total_price` (required, number): Total price for this item
- `customerInfo` (optional, object): Customer information
  - `name` (optional, string): Customer name
  - `email` (optional, string): Customer email
  - `phone` (optional, string): Customer phone
  - `address` (optional, string): Customer address

**Response**
```json
{
  "id": "8RH75926UV123456D",
  "status": "CREATED"
}
```

**Fields**
- `id` (string): PayPal order ID to use for approval and capture
- `status` (string): Order status ("CREATED")

**Frontend Integration**
```javascript
fetch('/api/paypal/create-order', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    total: 29.99,
    currency: 'EUR',
    cart: [/* cart items */],
    customerInfo: {
      name: 'John Doe',
      email: 'john@example.com'
    }
  })
})
.then(response => response.json())
.then(data => {
  console.log('PayPal Order ID:', data.id);
  // Use data.id to initialize PayPal button
});
```

---

#### `POST /api/paypal/capture-order`

Capture a PayPal order after customer approval.

**Request Body**
```json
{
  "orderID": "8RH75926UV123456D"
}
```

**Fields**
- `orderID` (required, string): PayPal order ID from create-order response

**Response**
```json
{
  "status": "COMPLETED",
  "orderID": "8RH75926UV123456D"
}
```

**Fields**
- `status` (string): Order status after capture ("COMPLETED" on success)
- `orderID` (string): PayPal order ID

**Frontend Integration**
```javascript
fetch('/api/paypal/capture-order', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    orderID: '8RH75926UV123456D'
  })
})
.then(response => response.json())
.then(data => {
  if (data.status === 'COMPLETED') {
    // Show success message
    console.log('Payment successful!');
  }
});
```

---

### Legacy Payment Endpoint

#### `POST /pay/paypal?product_id={id}`

Create a PayPal order for a specific product (legacy endpoint).

**Query Parameters**
- `product_id` (required, integer): Product ID from the products list

**Response**
```json
{
  "orderID": "8RH75926UV123456D"
}
```

---

### Order Management

#### `GET /api/orders/{order_id}`

Get detailed information about a specific order.

**Path Parameters**
- `order_id` (required, integer): Database order ID (not PayPal order ID)

**Response**
```json
{
  "id": 1,
  "paypal_order_id": "8RH75926UV123456D",
  "status": "COMPLETED",
  "total": 29.99,
  "currency": "EUR",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "customer_address": "123 Main St",
  "created_at": "2026-02-10T12:00:00+00:00",
  "updated_at": "2026-02-10T12:05:00+00:00",
  "completed_at": "2026-02-10T12:05:00+00:00",
  "items": [
    {
      "id": 1,
      "product_name": "Custom Frame",
      "product_sku": "FRAME-001",
      "quantity": 1,
      "unit_price": 29.99,
      "total_price": 29.99
    }
  ]
}
```

---

#### `GET /api/orders`

List all orders with pagination and filtering (admin endpoint).

**Query Parameters**
- `skip` (optional, integer): Number of orders to skip (default: 0)
- `limit` (optional, integer): Maximum orders to return (default: 100, max: 1000)
- `status` (optional, string): Filter by status (CREATED, APPROVED, COMPLETED, FAILED, REFUNDED)

**Example Requests**
```
GET /api/orders
GET /api/orders?skip=0&limit=50
GET /api/orders?status=COMPLETED
GET /api/orders?status=COMPLETED&skip=10&limit=20
```

**Response**
```json
{
  "orders": [
    {
      "id": 1,
      "paypal_order_id": "8RH75926UV123456D",
      "status": "COMPLETED",
      "total": 29.99,
      "currency": "EUR",
      "customer_name": "John Doe",
      "customer_email": "john@example.com",
      "created_at": "2026-02-10T12:00:00+00:00",
      "completed_at": "2026-02-10T12:05:00+00:00",
      "item_count": 1
    }
  ],
  "count": 1,
  "skip": 0,
  "limit": 100
}
```

---

## Order Status Flow

Orders progress through the following statuses:

1. **CREATED**: Order created in PayPal but not yet approved by customer
2. **APPROVED**: Customer approved payment (not captured yet) - Not currently used
3. **COMPLETED**: Payment captured successfully
4. **FAILED**: Payment capture failed
5. **REFUNDED**: Order was refunded (future feature)

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message here"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request data or PayPal error
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Errors

**Invalid PayPal credentials**
```json
{
  "error": "Failed to create PayPal order"
}
```

**Order not found**
```json
{
  "error": "Order not found"
}
```

**Invalid order status filter**
```json
{
  "error": "Invalid status: invalid_status"
}
```

---

## Email Notifications

When an order is successfully captured:

### Customer Confirmation Email
- Sent to customer email (if provided)
- Includes order details and items
- Formatted HTML email

### Admin Notification Email
- Sent to admin email (from environment variable)
- Includes customer and order information
- Formatted HTML email

> **Note**: Email notifications are optional. If SMTP is not configured, the API will log a warning but continue to function normally.

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- View all endpoints and their schemas
- Test endpoints directly from the browser
- See example requests and responses
- Download OpenAPI specification

---

## CORS Configuration

The API accepts requests from:

- `https://mystoryframes.shop`
- `https://www.mystoryframes.shop`
- `http://localhost:3000`
- `http://localhost:8000`
- `http://127.0.0.1:8000`
- `http://127.0.0.1:5500`

To add more origins, update the `allow_origins` list in `main.py`.

---

## Rate Limiting

There is currently no rate limiting implemented. Consider adding rate limiting for production:

- Use FastAPI middleware like `slowapi`
- Implement at reverse proxy level (nginx, CloudFlare)
- Use Render's built-in DDoS protection

---

## Future Enhancements

Potential additions to the API:

1. **Authentication**: Add API key authentication for admin endpoints
2. **Webhooks**: PayPal webhook integration for event notifications
3. **Refunds**: Endpoint to process refunds
4. **Order Search**: Search orders by customer email or PayPal ID
5. **Analytics**: Endpoint for sales statistics
6. **File Uploads**: Upload product images or customer files
7. **Rate Limiting**: Protect API from abuse
8. **Caching**: Cache product lists and common queries

---

## Support

For issues or questions:
- Check the [README](README.md)
- Review [DEPLOYMENT](DEPLOYMENT.md)
- Check FastAPI docs: https://fastapi.tiangolo.com
- Check PayPal docs: https://developer.paypal.com/docs
