# Django Backend Overview - Fliiply

## Architecture Overview

Fliiply is a **Trading Card Game (TCG) marketplace** built with Django REST Framework, designed to facilitate buying, selling, and collecting trading cards with robust payment processing and dispute resolution.

### Core Technology Stack

- **Framework**: Django 4.2.23 + Django REST Framework
- **Database**: PostgreSQL with comprehensive indexing
- **Authentication**: JWT with SimpleJWT
- **Payment Processing**: Stripe Connect + PaymentIntents
- **File Storage**: AWS S3 / MinIO
- **API Documentation**: Swagger/OpenAPI
- **Containerization**: Docker + Docker Compose

## Environment Configuration

### Base URLs by Environment

| Environment | API Base URL | Admin Panel | Documentation |
|-------------|--------------|-------------|---------------|
| **Development** | `http://localhost:8000` | `/admin/` | `/swagger/` |
| **Staging** | `https://staging-api.fliiply.com` | `/admin/` | `/swagger/` |
| **Production** | `https://api.fliiply.com` | `/admin/` | `/swagger/` |

### Environment Variables Required

```bash
# Django Core
DJANGO_ENVIRONMENT=development|staging|production
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True|False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DATABASE_NAME=fliiply_database
DATABASE_USER=fliiply_user
DATABASE_PASSWORD=secure_password
DATABASE_HOST=db
DATABASE_PORT=5432

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1  # days

# Stripe Payments
STRIPE_SECRET_KEY=sk_test_or_live_key
STRIPE_PUBLIC_KEY=pk_test_or_live_key
STRIPE_WEBHOOK_SECRET=whsec_webhook_secret

# Email Configuration
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True

# File Storage (AWS S3/MinIO)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=fliiply-media
AWS_S3_REGION_NAME=us-east-1

# Business Configuration
PLATFORM_COMMISSION_PERCENT=0.05  # 5% platform fee
CART_RESERVATION_MINUTES=30       # Cart item reservation time
```

## Authentication Method

### JWT (JSON Web Token) Authentication

The backend uses **stateless JWT authentication** with access and refresh tokens:

#### Token Lifecycle
- **Access Token**: 60 minutes (for API requests)
- **Refresh Token**: 1 day (for token renewal)
- **Storage**: Client-side (secure storage recommended)

#### Authentication Flow
```mermaid
sequenceDiagram
    participant Client
    participant Backend
    participant Database
    
    Client->>Backend: POST /api/v1/auth/login/ {username, password}
    Backend->>Database: Validate credentials
    Database-->>Backend: User data
    Backend-->>Client: {access_token, refresh_token}
    
    Note over Client: Store tokens securely
    
    Client->>Backend: API Request with Authorization: Bearer <access_token>
    Backend-->>Client: Protected resource data
    
    Note over Client: When access token expires
    
    Client->>Backend: POST /api/v1/auth/token/refresh/ {refresh}
    Backend-->>Client: New access_token
```

#### Authorization Header Format
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### User Roles & Permissions

The system implements **role-based access control** with the following roles:

| Role | Capabilities | Verification Required |
|------|-------------|----------------------|
| **Buyer** | Purchase items, manage cart, create orders | Email verification |
| **Seller** | List items, manage inventory, receive payments | Email + KYC + Stripe onboarding |
| **Verifier** | Verify product authenticity and condition | Admin assignment |
| **Admin** | Full system access, user management | Staff status |

#### Professional vs Individual Accounts
- **Individual (`particulier`)**: Personal collecting and trading
- **Professional (`professionnel`)**: Business accounts with tax information

## Database Models Structure

### Core Entity Relationships

```mermaid
erDiagram
    User ||--o{ Address : has
    User ||--o| ProfessionalInfo : has
    User ||--o{ Order : places
    User ||--o{ CartItem : owns
    User ||--o{ Collection : creates
    User ||--o{ Dispute : initiates
    
    Product ||--o{ ProductImage : has
    Product }o--o{ Category : belongs_to
    Product ||--o{ Variant : has
    
    Variant ||--o{ Listing : offered_as
    Variant }o--o{ Collection : included_in
    
    Listing ||--o{ CartItem : added_to
    Listing ||--o{ OrderItem : purchased_as
    
    Order ||--o{ OrderItem : contains
    Order ||--o{ Dispute : may_have
    
    Language ||--o{ Variant : defines
    Version ||--o{ Variant : defines
    Condition ||--o{ Variant : defines
    Grade ||--o{ Variant : defines
```

### Key Model Groups

#### **1. Identity & Access Management**
- `User` (extended AbstractUser with roles)
- `Address` (shipping/billing addresses)
- `ProfessionalInfo` (business account details)

#### **2. Product Catalog**
- `Product` (base TCG items)
- `Category` (hierarchical product categorization)
- `ProductImage` (multiple images per product)
- `Variant` (specific product versions)

#### **3. Product Attributes**
- `Language` (English, Japanese, French, etc.)
- `Version` (First Edition, Unlimited, etc.)
- `Condition` (Near Mint, Played, etc.)
- `Grade` (PSA 10, BGS 9.5, etc.)

#### **4. Marketplace**
- `Listing` (seller offerings)
- `CartItem` (shopping cart items)
- `Order` (purchase orders)
- `OrderItem` (individual order items)

#### **5. Collections & Social**
- `Collection` (user card collections)
- `CollectionItem` (items in collections)

#### **6. Dispute Resolution**
- `Dispute` (order dispute cases)
- `DisputeMessage` (dispute conversation)

#### **7. Search & Analytics**
- `SearchHistory` (user search tracking)

## Business Logic Overview

### **1. User Onboarding Flow**

```mermaid
flowchart TD
    A[User Registration] --> B[Email Verification]
    B --> C{Account Type?}
    C -->|Individual| D[Basic Account Active]
    C -->|Professional| E[Business Info Required]
    E --> F[KYC Verification]
    F --> G{Wants to Sell?}
    G -->|Yes| H[Stripe Account Creation]
    G -->|No| D
    H --> I[Stripe Onboarding]
    I --> J[Seller Account Active]
    D --> K[Can Buy Only]
    J --> L[Can Buy & Sell]
```

### **2. Order Processing Workflow**

```mermaid
flowchart TD
    A[Add Items to Cart] --> B[Cart Reservation 30min]
    B --> C[Create Order]
    C --> D[Calculate Fees]
    D --> E[Create Payment Intent]
    E --> F[Payment Processing]
    F --> G{Payment Success?}
    G -->|Yes| H[Order Confirmed]
    G -->|No| I[Order Failed]
    H --> J[Update Inventory]
    J --> K[Notify Seller]
    K --> L[Shipping Process]
    L --> M{Issue?}
    M -->|Yes| N[Dispute Process]
    M -->|No| O[Order Complete]
```

### **3. Fee Calculation System**

```python
# Order Fee Structure
base_price = sum(item.price * item.quantity for item in order_items)
platform_commission = base_price * PLATFORM_COMMISSION_PERCENT  # 5%
buyer_processing_fee = max(base_price * 0.06, 5.00)  # 6% min €5
buyer_shipping_fee = 10.00  # Fixed shipping
buyer_total = base_price + platform_commission + buyer_processing_fee + buyer_shipping_fee

# Seller receives
seller_net = base_price - platform_commission - seller_fees
```

### **4. Search & Discovery**

- **Basic Text Search**: Product names, series, blocks
- **Advanced Filtering**: TCG type, price range, condition, language
- **Search History**: Automatic tracking for authenticated users
- **Suggestions**: Auto-complete functionality
- **Performance**: Database indexes on searchable fields

### **5. Inventory Management**

- **Stock Tracking**: Real-time inventory updates
- **Reservation System**: 30-minute cart reservation
- **Automatic Deactivation**: Out-of-stock listings
- **Conflict Resolution**: Oversold item handling

### **6. Payment Processing (Stripe Integration)**

#### Stripe Account Types
- **Sellers**: Express Connect accounts for payouts
- **Buyers**: Customer accounts for payment methods
- **Platform**: Standard account for commission collection

#### Payment Flow
1. **Setup**: Buyer saves payment methods via SetupIntent
2. **Purchase**: PaymentIntent created for order total
3. **Processing**: Payment confirmed with saved method
4. **Payout**: Automatic transfer to seller account
5. **Fees**: Platform commission automatically deducted

### **7. Dispute Resolution**

- **Initiation**: Buyers can create disputes for orders
- **Communication**: Message system between parties
- **Moderation**: Admin/verifier intervention
- **Resolution**: Refund, replacement, or dismissal
- **Integration**: Payment holds during disputes

## Security Features

### **Authentication Security**
- Password hashing with Django's PBKDF2
- JWT token expiration and rotation
- Email verification with OTP (6-digit, 10-minute expiry)
- Rate limiting on authentication endpoints

### **API Security**
- CORS configuration for allowed origins
- Request throttling (100/hour anonymous, 1000/hour authenticated)
- Input validation and sanitization
- SQL injection prevention (Django ORM)

### **Business Security**
- User ownership validation on resources
- Role-based permission checks
- Payment security via Stripe PCI compliance
- KYC verification for sellers

### **Data Protection**
- Environment-based configuration
- Secret key rotation capability
- Secure file upload handling
- Database encryption at rest (PostgreSQL)

## Performance Optimizations

### **Database Optimizations**
- **30+ Strategic Indexes**: On frequently queried fields
- **Query Optimization**: select_related() and prefetch_related()
- **Connection Pooling**: Configured for production
- **Composite Indexes**: Multi-field query optimization

### **Caching Strategy**
- **Redis Integration**: Ready for cache implementation
- **Query Caching**: Frequently accessed data
- **Session Caching**: User session management

### **API Performance**
- **Pagination**: Configurable page sizes (default 20, max 100)
- **Field Selection**: Minimize data transfer
- **Response Compression**: Gzip enabled in production

## Monitoring & Logging

### **Health Checks**
- `/health/` - Basic application health
- `/health/detailed/` - Comprehensive system status
- `/health/ready/` - Kubernetes readiness probe
- `/health/live/` - Kubernetes liveness probe

### **Logging Configuration**
- **Structured Logging**: JSON format for production
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Size and time-based rotation
- **Error Tracking**: Integration-ready for Sentry

### **Metrics & Analytics**
- **Business Metrics**: Order volume, revenue, user activity
- **Performance Metrics**: Response times, error rates
- **System Metrics**: Database performance, resource usage

## Deployment Architecture

### **Container Setup**
```yaml
# docker-compose.yml structure
services:
  web:      # Django application
  db:       # PostgreSQL database
  redis:    # Caching and sessions
  nginx:    # Reverse proxy (production)
  minio:    # Object storage (development)
```

### **Environment Separation**
- **Development**: Local Docker, debug enabled, test payments
- **Staging**: Production-like, test data, staging Stripe
- **Production**: Optimized settings, live payments, monitoring

This backend provides a robust foundation for a Flutter mobile application with comprehensive user management, secure payment processing, and scalable marketplace functionality.