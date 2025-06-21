# Fliply Backend API - Bruno Collection

Complete Bruno API testing collection for the Fliply TCG marketplace backend.

## 📋 Overview

This collection provides comprehensive API testing coverage for all Fliply backend endpoints, organized into logical categories for easy navigation and testing workflows.

## 🗂️ Collection Structure

### 1. Authentication
- **Login** - User authentication with email/password
- **Register** - New user registration
- **Refresh Token** - JWT token refresh
- **Verify Email** - Email verification with OTP
- **Request Password Reset** - Password reset request
- **Reset Password** - Complete password reset

### 2. User Management
- **Get Current User** - Retrieve authenticated user profile
- **Update Profile** - Update user information
- **Become Seller** - Enable seller capabilities
- **List Addresses** - Get user addresses
- **Create Address** - Add new shipping/billing address

### 3. Product Catalog
- **List Categories** - Browse product categories
- **List Products** - Product catalog with filtering
- **Get Product** - Individual product details

### 4. Search & Discovery
- **Search Products** - Advanced marketplace search
- **Search Suggestions** - Auto-complete suggestions

### 5. Marketplace
- **List Listings** - Browse marketplace listings
- **Create Listing** - Add new product listing
- **Get Listing** - Individual listing details
- **Update Listing** - Modify existing listing
- **Delete Listing** - Remove listing

### 6. Orders & Payments
- **Create Order** - Place new order
- **List Orders** - View user orders
- **Get Order** - Order details
- **Confirm Payment** - Complete payment process

### 7. Seller Management
- **Update Order Status** - Seller order management
- **Seller Dashboard** - Performance metrics

### 8. Disputes & Support
- **Create Dispute** - File order dispute
- **List Disputes** - View user disputes
- **Get Dispute** - Dispute details

### 9. Admin Management
- **List Users** - Admin user management
- **Get User Details** - Detailed user information
- **Admin Analytics** - Platform metrics

## 🚀 Quick Start

### Prerequisites
- [Bruno](https://usebruno.com/) installed
- Access to Fliply backend API (development, staging, or production)

### Setup Instructions

1. **Import Collection**
   ```bash
   # Clone or download the bruno-collection folder
   # Open Bruno and import the collection
   ```

2. **Configure Environment**
   - Choose your target environment (Development, Staging, or Production)
   - Update environment variables if needed:
     - `baseUrl`: API base URL
     - `apiPath`: API path prefix (usually `/api`)

3. **Authentication Flow**
   ```
   1. Run "Register" or "Login" to get access token
   2. Token is automatically stored in {{accessToken}} variable
   3. All protected endpoints use this token automatically
   ```

## 🔧 Environment Configuration

### Development Environment
```
baseUrl: http://localhost:8000
apiPath: /api
```

### Staging Environment
```
baseUrl: https://staging-api.fliply.com
apiPath: /api
```

### Production Environment
```
baseUrl: https://api.fliply.com
apiPath: /api
```

## 🔐 Authentication

The collection uses JWT Bearer token authentication:

1. **Get Token**: Use Login or Register endpoints
2. **Automatic Storage**: Access token stored in `{{accessToken}}` variable
3. **Auto-Include**: Protected endpoints automatically include the token
4. **Refresh**: Use Refresh Token endpoint when token expires

## 📝 Testing Features

### Built-in Tests
Each request includes comprehensive tests:
- ✅ HTTP status code validation
- ✅ Response structure verification
- ✅ Data type validation
- ✅ Required field presence checks

### Example Test Output
```javascript
✓ should return 200
✓ should return user profile
✓ should include required fields
```

## 🎯 Common Testing Workflows

### 1. User Registration & Setup
```
1. Register → New user account
2. Verify Email → Activate account
3. Create Address → Add shipping address
4. Become Seller → Enable selling (optional)
```

### 2. Marketplace Operations
```
1. Login → Get authentication
2. List Products → Browse catalog
3. Create Listing → Add product for sale
4. Search Products → Find specific items
```

### 3. Order Processing
```
1. Create Order → Place order
2. Confirm Payment → Complete payment
3. Update Order Status → Seller ships item
4. Get Order → Track progress
```

### 4. Admin Operations
```
1. Login (admin) → Admin authentication
2. List Users → User management
3. Admin Analytics → Platform metrics
4. Get User Details → User investigation
```

## 🛠️ Customization

### Adding New Endpoints
1. Create new `.bru` file in appropriate folder
2. Use existing files as templates
3. Include comprehensive tests and documentation
4. Update README if new category added

### Modifying Requests
- Update request parameters in `params:query` section
- Modify request body in `body:json` section
- Adjust authentication in `auth:bearer` section
- Enhance tests in `tests` section

### Environment Variables
Available variables:
- `{{baseUrl}}` - API base URL
- `{{apiPath}}` - API path prefix
- `{{accessToken}}` - JWT access token
- `{{refreshToken}}` - JWT refresh token

## 📊 Response Examples

### Successful Response
```json
{
  "id": 1,
  "name": "Charizard",
  "series": "Base Set",
  "price": "299.99",
  "condition": "Near Mint"
}
```

### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": ["This field is required"]
    }
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check if access token is valid
   - Run Login endpoint to refresh token
   - Verify user has required permissions

2. **404 Not Found**
   - Verify endpoint URL is correct
   - Check if resource ID exists
   - Confirm API path configuration

3. **422 Validation Error**
   - Review request body format
   - Check required fields are included
   - Validate data types and constraints

### Debug Tips
- Use Bruno's network inspector
- Check environment variable values
- Review server logs for detailed errors
- Verify request headers and authentication

## 📞 Support

For issues with the API collection:
1. Check this README for common solutions
2. Review endpoint documentation in each `.bru` file
3. Contact the development team
4. Submit issues to the project repository

## 🔄 Updates

This collection is automatically updated with:
- New API endpoints
- Schema changes
- Authentication updates
- Environment configurations

Keep your collection updated by pulling the latest version from the repository.

---

**Happy Testing! 🎮**