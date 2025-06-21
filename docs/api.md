# API Documentation - Fliiply Backend

## Base Information

### Base URLs
- **Development**: `http://localhost:8000`
- **Staging**: `https://staging-api.fliiply.com`
- **Production**: `https://api.fliiply.com`

### API Versioning
All API endpoints are prefixed with `/api/v1/`

### Response Format
All API responses follow a consistent format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  },
  "meta": {
    "pagination": {
      "count": 100,
      "next": "http://api.example.com/api/v1/endpoint/?page=2",
      "previous": null,
      "page_size": 20
    }
  },
  "timestamp": "2025-06-19T12:00:00Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "message": "Validation failed",
  "error_code": "validation_error",
  "details": {
    "field_name": ["This field is required."]
  },
  "timestamp": "2025-06-19T12:00:00Z"
}
```

## Authentication

### JWT Authentication
The API uses JWT (JSON Web Token) authentication with access and refresh tokens.

#### Token Configuration
- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 1 day
- **Header Format**: `Authorization: Bearer <access_token>`

#### Authentication Flow
1. Login with credentials to get tokens
2. Use access token for API requests
3. Refresh access token when expired using refresh token

## API Endpoints

### 🔒 Authentication

#### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_expires_in": 86400,
  "access_expires_in": 3600
}
```

#### Register
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string",
  "confirm_password": "string",
  "accept_terms": true,
  "subscribed_to_newsletter": false,
  "role": "particulier" // or "professionnel"
}
```

#### Refresh Token
```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "refresh_token_here"
}
```

#### Email Verification
```http
POST /api/v1/auth/verify-email/
Content-Type: application/json

{
  "email": "string",
  "otp": "123456"
}
```

#### Password Reset Request
```http
POST /api/v1/auth/password-reset/
Content-Type: application/json

{
  "email": "string"
}
```

#### Password Reset Confirm
```http
POST /api/v1/auth/password-reset/confirm/
Content-Type: application/json

{
  "email": "string",
  "otp": "123456",
  "new_password": "string"
}
```

### 👤 User Management

#### Get Current User Profile
```http
GET /api/v1/users/me/
Authorization: Bearer <access_token>
```

#### Update User Profile
```http
PATCH /api/v1/users/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "string",
  "last_name": "string",
  "email": "string"
}
```

#### Become Seller
```http
POST /api/v1/users/become_seller/
Authorization: Bearer <access_token>
```

#### User Addresses
```http
GET /api/v1/addresses/
POST /api/v1/addresses/
PUT /api/v1/addresses/{id}/
DELETE /api/v1/addresses/{id}/
Authorization: Bearer <access_token>
```

**Address Object:**
```json
{
  "id": 1,
  "address_type": "shipping", // or "billing"
  "street": "123 Main St",
  "city": "Paris",
  "state": "Île-de-France",
  "postal_code": "75001",
  "country": "France",
  "is_default": true
}
```

### 🛍️ Product Catalog

#### List Categories
```http
GET /api/v1/categories/
```

#### List Products
```http
GET /api/v1/products/
GET /api/v1/products/?tcg_type=pokemon
GET /api/v1/products/?category=1
```

#### Get Product Details
```http
GET /api/v1/products/{id}/
```

#### Product Attributes
```http
GET /api/v1/languages/
GET /api/v1/versions/
GET /api/v1/conditions/
GET /api/v1/grades/
```

### 🏬 Marketplace

#### List Marketplace Listings
```http
GET /api/v1/listings/
GET /api/v1/listings/?product=1
GET /api/v1/listings/?min_price=10&max_price=100
```

#### Search Products/Listings
```http
GET /api/v1/search/?q=charizard
GET /api/v1/search/?q=pokemon&tcg_type=pokemon&min_price=50
```

**Search Parameters:**
- `q`: Search query
- `tcg_type`: pokemon, yugioh, magic
- `block`: Product block
- `series`: Product series
- `language`: Language code
- `version`: Version code
- `condition`: Condition code
- `grade`: Grade value
- `min_price` / `max_price`: Price range
- `availability`: in_stock, out_of_stock

#### Search Suggestions
```http
GET /api/v1/search/suggestions/?query=char
```

### 🛒 Shopping Cart

#### List Cart Items
```http
GET /api/v1/cart/
Authorization: Bearer <access_token>
```

#### Add to Cart
```http
POST /api/v1/cart/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "listing": 1,
  "quantity": 2
}
```

#### Update Cart Item
```http
PUT /api/v1/cart/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "quantity": 3
}
```

#### Remove from Cart
```http
DELETE /api/v1/cart/{id}/
Authorization: Bearer <access_token>
```

### 📦 Orders

#### List Orders
```http
GET /api/v1/orders/
Authorization: Bearer <access_token>
```

#### Create Order
```http
POST /api/v1/orders/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "cart_items": [1, 2, 3],
  "buyer_address": 1
}
```

#### Get Order Details
```http
GET /api/v1/orders/{id}/
Authorization: Bearer <access_token>
```

#### Pay for Order
```http
POST /api/v1/orders/{id}/pay/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "payment_method_id": "pm_1234567890"
}
```

### 📚 Collections

#### List User Collections
```http
GET /api/v1/collections/
Authorization: Bearer <access_token>
```

#### Create Collection
```http
POST /api/v1/collections/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Pokemon Collection",
  "description": "Rare Pokemon cards",
  "is_public": true
}
```

### ⚖️ Disputes

#### List Disputes
```http
GET /api/v1/disputes/
Authorization: Bearer <access_token>
```

#### Create Dispute
```http
POST /api/v1/disputes/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "order": 1,
  "reason": "Item not as described",
  "description": "The card condition was not as advertised"
}
```

#### Add Dispute Message
```http
POST /api/v1/disputes/{id}/add_message/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "Here are photos of the item received"
}
```

### 💳 Payment & Billing

#### Create Setup Intent (Save Payment Method)
```http
POST /api/v1/stripe/setup-intent/
Authorization: Bearer <access_token>
```

#### Create Subscription
```http
POST /api/v1/stripe/subscription/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "price_id": "price_1234567890"
}
```

#### Stripe Onboarding (Sellers)
```http
GET /api/v1/stripe/onboarding/
Authorization: Bearer <access_token>
```

### 🔧 System Health

#### Health Check
```http
GET /health/
```

#### Detailed Health Check
```http
GET /health/detailed/
```

## Error Codes

| Code | Description |
|------|-------------|
| `validation_error` | Request validation failed |
| `authentication_failed` | Invalid or missing authentication |
| `permission_denied` | Insufficient permissions |
| `not_found` | Resource not found |
| `method_not_allowed` | HTTP method not allowed |
| `throttled` | Rate limit exceeded |
| `server_error` | Internal server error |
| `payment_failed` | Payment processing failed |
| `insufficient_stock` | Product out of stock |
| `business_rule_violation` | Business logic constraint violated |

## HTTP Status Codes

| Status | Description |
|--------|-------------|
| `200` | OK - Request successful |
| `201` | Created - Resource created successfully |
| `204` | No Content - Request successful, no response body |
| `400` | Bad Request - Invalid request data |
| `401` | Unauthorized - Authentication required |
| `403` | Forbidden - Permission denied |
| `404` | Not Found - Resource not found |
| `405` | Method Not Allowed - HTTP method not supported |
| `429` | Too Many Requests - Rate limit exceeded |
| `500` | Internal Server Error - Server error |
| `503` | Service Unavailable - Service temporarily unavailable |

## Rate Limiting

| Endpoint Type | Rate Limit |
|---------------|------------|
| Anonymous users | 100 requests/hour |
| Authenticated users | 1000 requests/hour |
| Login attempts | 5 requests/minute |
| Payment operations | 10 requests/hour |

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Pagination Response:**
```json
{
  "count": 150,
  "next": "http://api.example.com/api/v1/endpoint/?page=3",
  "previous": "http://api.example.com/api/v1/endpoint/?page=1",
  "results": [...]
}
```

## Content Types

- **Request**: `application/json`
- **Response**: `application/json`
- **File uploads**: `multipart/form-data`

## CORS Configuration

The API supports CORS for the following origins:
- `http://localhost:3000` (development)
- `https://app.fliiply.com` (production)
- `https://staging-app.fliiply.com` (staging)

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`