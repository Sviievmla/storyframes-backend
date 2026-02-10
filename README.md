# Storyframes Backend

Backend API for Storyframes application with PayPal integration, order management, and email notifications.

## Features

- ✅ PayPal payment integration (Sandbox & Live mode)
- ✅ Order management with PostgreSQL database
- ✅ Email notifications for customers and admins
- ✅ CORS configuration for production
- ✅ Health check endpoint for Render
- ✅ Complete REST API for order tracking

## Environment Configuration

### Required Environment Variables

The following environment variables must be set:

#### PayPal Configuration
- `PAYPAL_CLIENT_ID`: Your PayPal application client ID
- `PAYPAL_CLIENT_SECRET`: Your PayPal application client secret
- `PAYPAL_MODE`: Set to `sandbox` for testing or `live` for production (default: sandbox)

#### Database Configuration
- `DATABASE_URL`: PostgreSQL database URL (automatically provided by Render)
  - Format: `postgresql://user:password@host:port/database`
  - Note: Render provides this as `postgres://` which is automatically converted to `postgresql://`

#### Email Configuration (Optional but recommended)
- `SMTP_HOST`: SMTP server hostname (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP username (usually your email)
- `SMTP_PASSWORD`: SMTP password (use app-specific password for Gmail)
- `FROM_EMAIL`: Email address to send from (defaults to SMTP_USERNAME)
- `ADMIN_EMAIL`: Email address to receive order notifications (defaults to SMTP_USERNAME)

### Setting Environment Variables

#### Local Development

Create a `.env` file in the project root (not committed to repository):

```env
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_MODE=sandbox

# Optional: If DATABASE_URL is not set, SQLite will be used
DATABASE_URL=postgresql://user:password@localhost:5432/storyframes

# Email configuration (optional for development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@mystoryframes.shop
ADMIN_EMAIL=admin@mystoryframes.shop
```

#### Production (Render)

Set environment variables in Render Dashboard:
1. Go to your web service
2. Navigate to Environment tab
3. Add the following variables:

```
PAYPAL_CLIENT_ID=your_live_client_id
PAYPAL_CLIENT_SECRET=your_live_client_secret
PAYPAL_MODE=live
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@mystoryframes.shop
ADMIN_EMAIL=admin@mystoryframes.shop
```

Note: `DATABASE_URL` is automatically provided by Render when you add a PostgreSQL database.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

### Local Development

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Production (Render)

Render automatically runs the application using the command specified in `render.yaml` or the dashboard.

## API Endpoints

### Health Check

#### Health Check
- **Endpoint**: `GET /` or `GET /health`
- **Description**: Health check endpoint for monitoring
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "storyframes-backend"
  }
  ```

### Products

#### Get Products
- **Endpoint**: `GET /products`
- **Description**: Returns list of available products
- **Response**: Array of product objects

### PayPal Integration

#### Create Order from Checkout
- **Endpoint**: `POST /api/paypal/create-order`
- **Description**: Creates a PayPal order from checkout cart
- **Request Body**:
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
- **Response**:
  ```json
  {
    "id": "paypal_order_id",
    "status": "CREATED"
  }
  ```

#### Capture Order
- **Endpoint**: `POST /api/paypal/capture-order`
- **Description**: Captures a PayPal order after user approval
- **Request Body**:
  ```json
  {
    "orderID": "paypal_order_id"
  }
  ```
- **Response**:
  ```json
  {
    "status": "COMPLETED",
    "orderID": "paypal_order_id"
  }
  ```

#### Legacy Product Payment
- **Endpoint**: `POST /pay/paypal`
- **Description**: Creates a PayPal order for a specific product (legacy)
- **Query Parameter**: `product_id` (integer)
- **Response**:
  ```json
  {
    "orderID": "paypal_order_id"
  }
  ```

### Order Management

#### Get Order Details
- **Endpoint**: `GET /api/orders/{order_id}`
- **Description**: Get detailed information about a specific order
- **Response**:
  ```json
  {
    "id": 1,
    "paypal_order_id": "paypal_order_id",
    "status": "COMPLETED",
    "total": 29.99,
    "currency": "EUR",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1234567890",
    "customer_address": "123 Main St",
    "created_at": "2026-02-10T12:00:00",
    "updated_at": "2026-02-10T12:05:00",
    "completed_at": "2026-02-10T12:05:00",
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

#### List All Orders (Admin)
- **Endpoint**: `GET /api/orders`
- **Description**: List all orders with pagination
- **Query Parameters**:
  - `skip`: Number of orders to skip (default: 0)
  - `limit`: Maximum orders to return (default: 100, max: 1000)
  - `status`: Filter by status (CREATED, APPROVED, COMPLETED, FAILED, REFUNDED)
- **Response**:
  ```json
  {
    "orders": [
      {
        "id": 1,
        "paypal_order_id": "paypal_order_id",
        "status": "COMPLETED",
        "total": 29.99,
        "currency": "EUR",
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "created_at": "2026-02-10T12:00:00",
        "completed_at": "2026-02-10T12:05:00",
        "item_count": 1
      }
    ],
    "count": 1,
    "skip": 0,
    "limit": 100
  }
  ```

## Order Status Flow

1. **CREATED**: Order created in PayPal but not yet approved by customer
2. **APPROVED**: Customer approved payment (not captured yet)
3. **COMPLETED**: Payment captured successfully
4. **FAILED**: Payment capture failed
5. **REFUNDED**: Order was refunded (future feature)

## Email Notifications

When an order is successfully captured:
- Customer receives order confirmation email with order details
- Admin receives notification email with customer and order information

Email notifications are optional. If SMTP credentials are not configured, the application will log a warning but continue to function.

## Currency Configuration

- The `/api/paypal/create-order` endpoint defaults to **EUR** currency
- The legacy `/pay/paypal` endpoint uses **USD** currency
- Currency can be customized per request in the create-order endpoint

## Database

The application uses PostgreSQL in production (provided by Render) and falls back to SQLite for local development if `DATABASE_URL` is not set.

Database tables are automatically created on application startup.

## Error Handling

All endpoints return errors in JSON format:

```json
{
  "error": "error message"
}
```

Errors are returned with appropriate HTTP status codes:
- `400`: Bad request (validation errors, PayPal errors)
- `404`: Resource not found
- `500`: Internal server error

## Deployment Guide for Render

### Prerequisites

1. Create a Render account at https://render.com
2. Set up your PayPal application credentials:
   - Sandbox: https://developer.paypal.com/developer/applications
   - Live: https://www.paypal.com/businessmanage/account/products

### Step 1: Create PostgreSQL Database

1. In Render Dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - Name: `storyframes-db`
   - Region: Choose closest to your users
   - Plan: Free or paid based on needs
4. Click "Create Database"
5. Note the Internal Database URL (automatically used by web service)

### Step 2: Deploy Web Service

1. In Render Dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository: `Sviievmla/storyframes-backend`
4. Configure:
   - Name: `storyframes-backend`
   - Region: Same as database
   - Branch: `main` (or your deployment branch)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables (see above)
6. Connect the PostgreSQL database created in Step 1
7. Click "Create Web Service"

### Step 3: Configure Custom Domain (Optional)

1. In your web service settings, go to "Custom Domain"
2. Add your domain (e.g., `api.mystoryframes.shop`)
3. Update DNS records as instructed by Render
4. Add the domain to CORS allowed origins in `main.py`

### Step 4: Verify Deployment

1. Check the logs for any errors
2. Test the health endpoint: `https://your-app.onrender.com/health`
3. Test creating a test order with Sandbox credentials first
4. Once verified, switch to Live mode and update PayPal credentials

## PayPal Live Setup Instructions

### Step 1: Create Live PayPal App

1. Go to https://developer.paypal.com/developer/applications
2. Switch to "Live" mode (toggle in top right)
3. Click "Create App"
4. Configure:
   - App Name: "Storyframes Live"
   - App Type: Merchant
5. Copy the Live Client ID and Secret

### Step 2: Configure App Settings

1. In your app settings, enable:
   - Orders
   - Payments
   - Checkout
2. Add your return URL: `https://mystoryframes.shop`
3. Save changes

### Step 3: Update Backend Environment Variables

Update your Render environment variables:
```
PAYPAL_CLIENT_ID=live_client_id
PAYPAL_CLIENT_SECRET=live_secret
PAYPAL_MODE=live
```

### Step 4: Test with Real Payment

1. Use a small test amount first
2. Complete the payment flow
3. Verify order is captured
4. Check email notifications
5. Verify in PayPal dashboard

### Important Notes for Live Mode

- ⚠️ Test thoroughly in Sandbox before going live
- ⚠️ Never commit Live credentials to repository
- ⚠️ Use environment variables for all sensitive data
- ⚠️ Monitor PayPal dashboard for disputes/issues
- ⚠️ Keep backup of all transaction records
- ⚠️ Ensure HTTPS is enabled (Render provides this automatically)

## CORS Configuration

The application is configured to accept requests from:
- https://mystoryframes.shop
- https://www.mystoryframes.shop
- http://localhost:3000 (development)
- http://localhost:8000 (development)
- http://127.0.0.1:8000 (development)
- http://127.0.0.1:5500 (Live Server)

To add more domains, update the `allow_origins` list in `main.py`.

## Logging

The application logs important events:
- Order creation
- Order capture
- Email notifications
- Errors and exceptions

In production, logs are available in the Render dashboard.

## Security Best Practices

1. ✅ Never commit `.env` file or credentials
2. ✅ Use environment variables for all sensitive data
3. ✅ Enable HTTPS in production (Render provides this)
4. ✅ Validate all input data with Pydantic models
5. ✅ Use prepared statements (SQLAlchemy ORM)
6. ✅ Log security-relevant events
7. ✅ Keep dependencies updated

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Verify `DATABASE_URL` is set correctly
2. Ensure PostgreSQL database is running (Render status)
3. Check database credentials and permissions

### PayPal API Errors

If PayPal operations fail:
1. Verify `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` are set
2. Check `PAYPAL_MODE` is set correctly (sandbox/live)
3. Verify credentials are valid in PayPal dashboard
4. Check PayPal API status: https://www.paypal-status.com/

### Email Not Sending

If emails are not being sent:
1. Verify SMTP credentials are correct
2. For Gmail, use an App Password, not your regular password
3. Check SMTP host and port settings
4. Review application logs for email errors

### CORS Errors

If frontend can't connect:
1. Verify your domain is in the `allow_origins` list
2. Ensure the domain includes the correct protocol (https://)
3. Check browser console for specific CORS errors

## API Documentation

Once running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For issues or questions:
1. Check the logs first
2. Review this README
3. Check PayPal developer documentation
4. Review FastAPI documentation
