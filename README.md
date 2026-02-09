# Storyframes Backend

Backend API for Storyframes application with PayPal integration.

## Environment Configuration

### Required Environment Variables

The following environment variables must be set for the PayPal integration to work:

- `PAYPAL_CLIENT_ID`: Your PayPal application client ID
- `PAYPAL_CLIENT_SECRET`: Your PayPal application client secret

### Setting Environment Variables

```bash
export PAYPAL_CLIENT_ID="your_client_id_here"
export PAYPAL_CLIENT_SECRET="your_client_secret_here"
```

Or create a `.env` file (not committed to repository):

```
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
```

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### PayPal Integration

#### Create Order from Checkout (New)
- **Endpoint**: `POST /api/paypal/create-order`
- **Description**: Creates a PayPal order from checkout cart total
- **Request Body**:
  ```json
  {
    "total": 29.99,
    "currency": "EUR",  // optional, defaults to EUR
    "cart": []          // optional, for reference
  }
  ```
- **Response**:
  ```json
  {
    "orderID": "paypal_order_id"
  }
  ```

#### Capture Order (New)
- **Endpoint**: `POST /api/paypal/capture-order`
- **Description**: Captures a PayPal order after user approval
- **Request Body**:
  ```json
  {
    "orderID": "paypal_order_id"
  }
  ```
- **Response**: PayPal capture response with order details

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

### Products

#### Get Products
- **Endpoint**: `GET /products`
- **Description**: Returns list of available products
- **Response**: Array of product objects

## Currency Configuration

- The new `/api/paypal/create-order` endpoint defaults to **EUR** currency (matching checkout.html)
- The legacy `/pay/paypal` endpoint uses **USD** currency
- Currency can be customized per request in the create-order endpoint

## Error Handling

All endpoints return errors in JSON format:

```json
{
  "error": "error message"
}
```

Errors are returned with appropriate HTTP status codes (typically 400 for bad requests).

## PayPal Sandbox

The application is configured to use PayPal Sandbox environment for testing. Update `paypal_client.py` to use `LiveEnvironment` for production.
