# Fliiply Backend - Flutter Integration Guide

## Overview

This is a comprehensive integration guide for connecting a Flutter application to the Fliiply Trading Card Game (TCG) marketplace backend. The backend is built with Django REST Framework and provides APIs for user management, product catalog, marketplace operations, payment processing, and dispute resolution.

## Table of Contents

1. [Authentication & JWT Configuration](#authentication--jwt-configuration)
2. [Base URLs & Environment Setup](#base-urls--environment-setup)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Model Structures](#model-structures)
6. [Error Handling](#error-handling)
7. [Business Logic Overview](#business-logic-overview)
8. [Code Examples](#code-examples)

## Authentication & JWT Configuration

### JWT Token Management

The API uses JSON Web Tokens (JWT) for authentication with the following configuration:

- **Access Token Lifetime**: 60 minutes (configurable via environment)
- **Refresh Token Lifetime**: 1 day (configurable via environment)
- **Auth Header Type**: `Bearer`

### Authentication Headers

All authenticated requests must include:

```
Authorization: Bearer <your_jwt_token>
```

### Authentication Endpoints

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Token Refresh
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

#### Registration
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "new_user",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "secure_password",
  "confirm_password": "secure_password",
  "accept_terms": true,
  "subscribed_to_newsletter": false,
  "role": "particulier"  // or "professionnel"
}
```

## Base URLs & Environment Setup

### Development Environment
- **Base URL**: `http://localhost:8000`
- **API Base**: `http://localhost:8000/api/`
- **Documentation**: `http://localhost:8000/swagger/`

### Production Environment
- **Base URL**: Configure according to your deployment
- **CORS**: Ensure Flutter app domain is in `CORS_ALLOWED_ORIGINS`

### Required Headers

```dart
Map<String, String> headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer $accessToken',  // For authenticated requests
  'Accept': 'application/json',
};
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login/` | User login | No |
| POST | `/api/auth/refresh/` | Refresh JWT token | No |
| POST | `/api/auth/register/` | User registration | No |
| POST | `/api/auth/password_reset/` | Request password reset | No |
| POST | `/api/auth/password_reset_confirm/` | Confirm password reset | No |
| POST | `/api/auth/verify_email/` | Verify email with OTP | No |
| POST | `/api/auth/resend_verification_email/` | Resend verification email | Yes |

### User Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/me/` | Get current user profile | Yes |
| PATCH | `/api/users/{id}/` | Update user profile | Yes (Owner) |
| POST | `/api/users/become_seller/` | Enable seller capabilities | Yes |
| GET | `/api/users/addresses/` | List user addresses | Yes |
| POST | `/api/users/addresses/` | Create new address | Yes |
| PATCH | `/api/users/addresses/{id}/` | Update address | Yes (Owner) |
| DELETE | `/api/users/addresses/{id}/` | Delete address | Yes (Owner) |
| GET | `/api/users/professional-info/` | Get professional info | Yes |
| POST | `/api/users/professional-info/` | Create professional info | Yes |

### Product Catalog Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/categories/` | List product categories | No |
| GET | `/api/products/` | List products | No |
| GET | `/api/products/{id}/` | Get product details | No |
| GET | `/api/languages/` | List available languages | No |
| GET | `/api/versions/` | List product versions | No |
| GET | `/api/conditions/` | List product conditions | No |
| GET | `/api/grades/` | List available grades | No |
| GET | `/api/variants/` | List product variants | No |
| GET | `/api/listings/` | List marketplace listings | No |

### Marketplace & Orders

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/cart/` | Get cart items | Yes |
| POST | `/api/cart/` | Add to cart | Yes |
| PATCH | `/api/cart/{id}/` | Update cart item | Yes |
| DELETE | `/api/cart/{id}/` | Remove from cart | Yes |
| GET | `/api/orders/` | List orders | Yes |
| POST | `/api/orders/` | Create order from cart | Yes |
| GET | `/api/orders/{id}/` | Get order details | Yes |
| POST | `/api/orders/{id}/pay/` | Pay for order | Yes |

### Collections

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/collections/` | List user collections | Yes |
| POST | `/api/collections/` | Create collection | Yes |
| GET | `/api/collections/{id}/` | Get collection details | Yes |
| PATCH | `/api/collections/{id}/` | Update collection | Yes |
| DELETE | `/api/collections/{id}/` | Delete collection | Yes |

### Search & Discovery

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/search/` | Search listings with filters | No |
| GET | `/api/search/suggestions/` | Get search suggestions | No |

### Disputes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/disputes/` | List user disputes | Yes |
| POST | `/api/disputes/` | Create dispute | Yes |
| GET | `/api/disputes/{id}/` | Get dispute details | Yes |
| POST | `/api/disputes/{id}/add_message/` | Add message to dispute | Yes |
| POST | `/api/disputes/{id}/resolve/` | Resolve dispute | Yes |

### Stripe Payment Integration

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/stripe/setup-intent/` | Create payment setup intent | Yes |
| POST | `/api/stripe/subscription/` | Create subscription | Yes |
| POST | `/api/stripe/onboarding/start/` | Start seller onboarding | Yes |

## Request/Response Formats

### Standard Response Format

All API responses follow a consistent structure:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": { /* response data */ },
  "meta": { /* optional metadata */ }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "error_code",
  "message": "Human readable error message",
  "timestamp": "2024-01-01T12:00:00Z",
  "status_code": 400,
  "details": { /* error details */ }
}
```

### Pagination

List endpoints support pagination:

**Request Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Paginated Response:**
```json
{
  "success": true,
  "data": [ /* items */ ],
  "meta": {
    "pagination": {
      "count": 100,
      "next": "http://api.example.com/api/products/?page=3",
      "previous": "http://api.example.com/api/products/?page=1"
    }
  }
}
```

## Model Structures

### User Model

```json
{
  "id": 1,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "is_buyer": true,
  "is_seller": false,
  "is_verifier": false,
  "is_email_verified": true,
  "role": "particulier",  // "particulier" or "professionnel"
  "rating": 4.5,
  "stripe_account_id": "acct_xxx",
  "is_kyc_verified": false,
  "billing_address": { /* Address object */ },
  "addresses": [ /* Array of Address objects */ ]
}
```

### Address Model

```json
{
  "id": 1,
  "name": "Home",
  "street_number": "123",
  "street": "Main Street",
  "city": "Paris",
  "state": "Île-de-France",
  "postal_code": "75001",
  "country": "France",
  "phone_number": "+33123456789",
  "address_type": "delivery",  // "billing", "delivery", "both", "company"
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Product Model

```json
{
  "id": 1,
  "name": "Charizard",
  "block": "Base Set",
  "series": "Pokémon TCG",
  "description": "Powerful Fire-type Pokémon card",
  "tcg_type": "pokemon",  // "pokemon", "yugioh", "magic", "other"
  "slug": "charizard-base-set",
  "categories": [ /* Array of Category objects */ ],
  "allowed_languages": [ /* Array of Language objects */ ],
  "allowed_versions": [ /* Array of Version objects */ ],
  "images": [ /* Array of ProductImage objects */ ],
  "average_price": "150.00",
  "total_stock": 5,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Variant Model

```json
{
  "id": 1,
  "product": 1,
  "language": {
    "id": 1,
    "code": "en",
    "name": "English"
  },
  "version": {
    "id": 1,
    "code": "1st",
    "name": "First Edition",
    "tcg_types": ["pokemon"],
    "description": "First edition print",
    "displayable": true
  },
  "condition": {
    "id": 1,
    "code": "nm",
    "label": "Near Mint",
    "is_graded": false
  },
  "grade": {
    "id": 1,
    "value": "10.0",
    "grader": "PSA"
  }
}
```

### Listing Model

```json
{
  "id": 1,
  "product": 1,
  "variant": { /* Variant object */ },
  "seller": 1,
  "price": "150.00",
  "stock": 3,
  "status": "active",  // "active", "sold", "inactive"
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Order Model

```json
{
  "id": 1,
  "buyer": { /* User object */ },
  "items": [ /* Array of OrderItem objects */ ],
  "base_price": "180.00",
  "buyer_address": { /* Address object */ },
  "buyer_processing_fee": "10.80",
  "buyer_shipping_fee": "10.00",
  "buyer_total_price": "200.80",
  "platform_commission": "9.00",
  "stripe_payment_intent_id": "pi_xxx",
  "status": "pending",  // "pending", "shipped", "delivered", "cancelled"
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Cart Item Model

```json
{
  "id": 1,
  "listing": { /* Listing object */ },
  "quantity": 2,
  "reserved_until": "2024-01-01T12:30:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Error Handling

### Error Types

| Error Code | HTTP Status | Description |
|------------|------------|-------------|
| `validation_error` | 400 | Request data validation failed |
| `authentication_required` | 401 | Authentication credentials required |
| `authentication_failed` | 401 | Invalid authentication credentials |
| `permission_denied` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `method_not_allowed` | 405 | HTTP method not allowed |
| `rate_limit_exceeded` | 429 | Rate limit exceeded |
| `internal_server_error` | 500 | Internal server error |

### Common Error Examples

**Validation Error:**
```json
{
  "success": false,
  "error": "validation_error",
  "message": "Validation failed",
  "timestamp": "2024-01-01T12:00:00Z",
  "status_code": 400,
  "details": {
    "email": ["This field is required."],
    "password": ["This field is required."]
  }
}
```

**Authentication Error:**
```json
{
  "success": false,
  "error": "authentication_required",
  "message": "Authentication credentials required",
  "timestamp": "2024-01-01T12:00:00Z",
  "status_code": 401
}
```

**Permission Error:**
```json
{
  "success": false,
  "error": "permission_denied",
  "message": "You do not have permission to perform this action",
  "timestamp": "2024-01-01T12:00:00Z",
  "status_code": 403
}
```

## Business Logic Overview

### User Roles & Permissions

1. **Particulier (Individual)**
   - Can buy products
   - Cannot sell initially (must upgrade to seller)
   - Can create collections

2. **Professionnel (Professional)**
   - Can buy and sell products
   - Requires company information
   - Automatic Stripe account creation

3. **Verifier**
   - Can verify other users (admin role)
   - Can moderate disputes

### Cart & Reservation System

- Cart items are automatically reserved for 30 minutes
- Stock is temporarily held during reservation
- Expired reservations are automatically cleaned up

### Order Processing

1. Create order from cart items
2. Generate Stripe PaymentIntent
3. Reduce stock from listings
4. Clear cart items
5. Payment confirmation
6. Order fulfillment

### Dispute Resolution

- Buyers can create disputes for orders
- Disputes support message threads
- File attachments supported
- Moderators can resolve disputes

### Search Features

- Full-text search across products
- Advanced filtering by multiple criteria
- Search suggestions with autocomplete
- Search history tracking for authenticated users

## Code Examples

### Flutter HTTP Client Setup

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000/api';
  
  static Map<String, String> _headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  static void setAuthToken(String token) {
    _headers['Authorization'] = 'Bearer $token';
  }
  
  static void clearAuthToken() {
    _headers.remove('Authorization');
  }
  
  static Future<Map<String, dynamic>> get(String endpoint) async {
    final response = await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: _headers,
    );
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> post(
    String endpoint, 
    Map<String, dynamic> data
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: _headers,
      body: json.encode(data),
    );
    return _handleResponse(response);
  }
  
  static Map<String, dynamic> _handleResponse(http.Response response) {
    final data = json.decode(response.body);
    
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return data;
    } else {
      throw ApiException(
        data['error'] ?? 'unknown_error',
        data['message'] ?? 'An error occurred',
        response.statusCode,
        data['details'],
      );
    }
  }
}

class ApiException implements Exception {
  final String code;
  final String message;
  final int statusCode;
  final dynamic details;
  
  ApiException(this.code, this.message, this.statusCode, this.details);
}
```

### Authentication Service

```dart
class AuthService {
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';
  
  Future<bool> login(String username, String password) async {
    try {
      final response = await ApiClient.post('/auth/login/', {
        'username': username,
        'password': password,
      });
      
      await _storeTokens(response['access'], response['refresh']);
      ApiClient.setAuthToken(response['access']);
      return true;
    } catch (e) {
      return false;
    }
  }
  
  Future<bool> refreshToken() async {
    final refreshToken = await _getRefreshToken();
    if (refreshToken == null) return false;
    
    try {
      final response = await ApiClient.post('/auth/refresh/', {
        'refresh': refreshToken,
      });
      
      await _storeTokens(response['access'], refreshToken);
      ApiClient.setAuthToken(response['access']);
      return true;
    } catch (e) {
      await logout();
      return false;
    }
  }
  
  Future<void> logout() async {
    await _clearTokens();
    ApiClient.clearAuthToken();
  }
  
  Future<void> _storeTokens(String accessToken, String refreshToken) async {
    // Store tokens securely (e.g., using flutter_secure_storage)
  }
  
  Future<String?> _getRefreshToken() async {
    // Retrieve refresh token from secure storage
    return null; // Placeholder
  }
  
  Future<void> _clearTokens() async {
    // Clear stored tokens
  }
}
```

### Product Search

```dart
class ProductService {
  Future<List<Product>> searchProducts({
    String? query,
    String? tcgType,
    String? block,
    String? series,
    double? minPrice,
    double? maxPrice,
    int page = 1,
  }) async {
    final params = <String, String>{
      'page': page.toString(),
    };
    
    if (query != null) params['q'] = query;
    if (tcgType != null) params['tcg_type'] = tcgType;
    if (block != null) params['block'] = block;
    if (series != null) params['series'] = series;
    if (minPrice != null) params['min_price'] = minPrice.toString();
    if (maxPrice != null) params['max_price'] = maxPrice.toString();
    
    final queryString = params.entries
        .map((e) => '${e.key}=${Uri.encodeComponent(e.value)}')
        .join('&');
    
    final response = await ApiClient.get('/search/?$queryString');
    
    return (response['data'] as List)
        .map((json) => Product.fromJson(json))
        .toList();
  }
  
  Future<List<String>> getSearchSuggestions(String query) async {
    final response = await ApiClient.get('/search/suggestions/?query=$query');
    return List<String>.from(response);
  }
}
```

### Cart Management

```dart
class CartService {
  Future<List<CartItem>> getCartItems() async {
    final response = await ApiClient.get('/cart/');
    return (response['data'] as List)
        .map((json) => CartItem.fromJson(json))
        .toList();
  }
  
  Future<CartItem> addToCart(int listingId, int quantity) async {
    final response = await ApiClient.post('/cart/', {
      'listing': listingId,
      'quantity': quantity,
    });
    return CartItem.fromJson(response['data']);
  }
  
  Future<void> removeFromCart(int cartItemId) async {
    await ApiClient.delete('/cart/$cartItemId/');
  }
}
```

### Order Processing

```dart
class OrderService {
  Future<Order> createOrder(List<int> cartItemIds, int addressId) async {
    final response = await ApiClient.post('/orders/', {
      'cart_items': cartItemIds,
      'buyer_address': addressId,
    });
    return Order.fromJson(response['data']);
  }
  
  Future<Map<String, dynamic>> payForOrder(int orderId, String paymentMethodId) async {
    final response = await ApiClient.post('/orders/$orderId/pay/', {
      'payment_method_id': paymentMethodId,
    });
    return response;
  }
  
  Future<List<Order>> getOrders() async {
    final response = await ApiClient.get('/orders/');
    return (response['data'] as List)
        .map((json) => Order.fromJson(json))
        .toList();
  }
}
```

This comprehensive guide provides all the necessary information for Flutter developers to integrate with the Fliiply backend API, including authentication, endpoint details, model structures, error handling, and practical code examples.