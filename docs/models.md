# Data Models Documentation - Fliiply Backend

## Overview

This document details all Django models and their corresponding JSON representations for Flutter integration. Each model includes field types, relationships, and example JSON responses.

## User Management Models

### User Model (Extended AbstractUser)

**Django Model Fields:**
```python
class User(AbstractUser):
    # Role and permissions
    is_buyer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    is_verifier = models.BooleanField(default=False)
    
    # Account type
    role = models.CharField(max_length=20, choices=[
        ('particulier', 'Individual'),
        ('professionnel', 'Professional')
    ])
    
    # Verification status
    is_email_verified = models.BooleanField(default=False)
    is_kyc_verified = models.BooleanField(default=False)
    
    # Email verification
    email_otp = models.CharField(max_length=6, blank=True, null=True)
    email_otp_expiry = models.DateTimeField(blank=True, null=True)
    
    # Password reset
    password_reset_otp = models.CharField(max_length=6, blank=True, null=True)
    password_reset_otp_expiry = models.DateTimeField(blank=True, null=True)
    
    # Stripe integration
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional info
    subscribed_to_newsletter = models.BooleanField(default=False)
    accept_terms = models.BooleanField(default=False)
```

**JSON Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_buyer": true,
  "is_seller": false,
  "is_verifier": false,
  "role": "particulier",
  "is_email_verified": true,
  "is_kyc_verified": false,
  "subscribed_to_newsletter": true,
  "accept_terms": true,
  "date_joined": "2025-06-19T10:00:00Z",
  "last_login": "2025-06-19T12:00:00Z"
}
```

### Address Model

**Django Model Fields:**
```python
class Address(models.Model):
    ADDRESS_TYPES = [
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
```

**JSON Response:**
```json
{
  "id": 1,
  "address_type": "shipping",
  "street": "123 Main Street",
  "city": "Paris",
  "state": "Île-de-France",
  "postal_code": "75001",
  "country": "France",
  "is_default": true,
  "created_at": "2025-06-19T10:00:00Z",
  "updated_at": "2025-06-19T10:00:00Z"
}
```

### ProfessionalInfo Model

**Django Model Fields:**
```python
class ProfessionalInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional_info')
    company_name = models.CharField(max_length=255)
    siret = models.CharField(max_length=14, unique=True)
    vat_number = models.CharField(max_length=20, blank=True, null=True)
    business_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "company_name": "TCG Shop Paris",
  "siret": "12345678901234",
  "vat_number": "FR12345678901",
  "business_address": "456 Business Ave, 75002 Paris, France",
  "phone_number": "+33123456789",
  "website": "https://tcgshopparis.com",
  "description": "Specialized in Pokemon and Yu-Gi-Oh cards",
  "created_at": "2025-06-19T10:00:00Z",
  "updated_at": "2025-06-19T10:00:00Z"
}
```

## Product Catalog Models

### Category Model

**Django Model Fields:**
```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "name": "Pokemon",
  "slug": "pokemon",
  "description": "Pokemon Trading Card Game",
  "parent": null,
  "image": "https://media.fliiply.com/categories/pokemon.jpg",
  "is_active": true,
  "children": [
    {
      "id": 2,
      "name": "Base Set",
      "slug": "pokemon-base-set",
      "parent": 1
    }
  ]
}
```

### Product Model

**Django Model Fields:**
```python
class Product(models.Model):
    TCG_TYPES = [
        ('pokemon', 'Pokemon'),
        ('yugioh', 'Yu-Gi-Oh'),
        ('magic', 'Magic: The Gathering'),
        ('other', 'Other'),
    ]
    
    tcg_type = models.CharField(max_length=20, choices=TCG_TYPES)
    name = models.CharField(max_length=255)
    series = models.CharField(max_length=255, blank=True, null=True)
    block = models.CharField(max_length=255, blank=True, null=True)
    set_number = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name='products')
    is_active = models.BooleanField(default=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "tcg_type": "pokemon",
  "name": "Charizard",
  "series": "Base Set",
  "block": "Wizard of the Coast",
  "set_number": "4/102",
  "description": "A powerful Fire-type Pokemon card",
  "categories": [
    {
      "id": 1,
      "name": "Pokemon",
      "slug": "pokemon"
    }
  ],
  "images": [
    {
      "id": 1,
      "image": "https://media.fliiply.com/products/charizard-1.jpg",
      "alt_text": "Charizard Base Set",
      "is_primary": true
    }
  ],
  "average_price": "150.00",
  "total_stock": 5,
  "is_active": true,
  "created_at": "2025-06-19T10:00:00Z",
  "updated_at": "2025-06-19T10:00:00Z"
}
```

### ProductImage Model

**Django Model Fields:**
```python
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
```

**JSON Response:**
```json
{
  "id": 1,
  "image": "https://media.fliiply.com/products/charizard-1.jpg",
  "alt_text": "Charizard Base Set Front",
  "is_primary": true,
  "created_at": "2025-06-19T10:00:00Z"
}
```

## Product Attribute Models

### Language Model

**Django Model Fields:**
```python
class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "name": "English",
  "code": "en",
  "is_active": true
}
```

### Version Model

**Django Model Fields:**
```python
class Version(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "name": "First Edition",
  "code": "1st",
  "description": "First print run of the set",
  "is_active": true
}
```

### Condition Model

**Django Model Fields:**
```python
class Condition(models.Model):
    label = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    quality_score = models.IntegerField()  # 1-10 scale
    is_active = models.BooleanField(default=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "label": "Near Mint",
  "code": "NM",
  "description": "Card shows minimal wear from play or handling",
  "quality_score": 9,
  "is_active": true
}
```

### Grade Model

**Django Model Fields:**
```python
class Grade(models.Model):
    grader = models.CharField(max_length=50)  # PSA, BGS, CGC, etc.
    value = models.CharField(max_length=10)   # 10, 9.5, etc.
    description = models.TextField(blank=True)
    numeric_value = models.DecimalField(max_digits=3, decimal_places=1)
    is_active = models.BooleanField(default=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "grader": "PSA",
  "value": "10",
  "description": "Perfect condition, no flaws",
  "numeric_value": "10.0",
  "is_active": true
}
```

### Variant Model

**Django Model Fields:**
```python
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    version = models.ForeignKey(Version, on_delete=models.PROTECT)
    condition = models.ForeignKey(Condition, on_delete=models.PROTECT)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "product": {
    "id": 1,
    "name": "Charizard",
    "tcg_type": "pokemon"
  },
  "language": {
    "id": 1,
    "name": "English",
    "code": "en"
  },
  "version": {
    "id": 1,
    "name": "First Edition",
    "code": "1st"
  },
  "condition": {
    "id": 1,
    "label": "Near Mint",
    "code": "NM"
  },
  "grade": {
    "id": 1,
    "grader": "PSA",
    "value": "10"
  },
  "is_active": true,
  "created_at": "2025-06-19T10:00:00Z"
}
```

## Marketplace Models

### Listing Model

**Django Model Fields:**
```python
class Listing(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('inactive', 'Inactive'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    is_negotiable = models.BooleanField(default=False)
```

**JSON Response:**
```json
{
  "id": 1,
  "seller": {
    "id": 2,
    "username": "card_seller",
    "is_seller": true
  },
  "product": {
    "id": 1,
    "name": "Charizard",
    "tcg_type": "pokemon"
  },
  "variant": {
    "id": 1,
    "language": {"name": "English"},
    "condition": {"label": "Near Mint"},
    "grade": {"grader": "PSA", "value": "10"}
  },
  "status": "active",
  "price": "299.99",
  "stock": 1,
  "description": "Perfect PSA 10 Charizard from Base Set",
  "is_negotiable": false,
  "created_at": "2025-06-19T10:00:00Z",
  "updated_at": "2025-06-19T10:00:00Z"
}
```

## Shopping & Orders Models

### CartItem Model

**Django Model Fields:**
```python
class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    reserved_until = models.DateTimeField()
```

**JSON Response:**
```json
{
  "id": 1,
  "listing": {
    "id": 1,
    "product": {"name": "Charizard"},
    "price": "299.99",
    "stock": 1,
    "seller": {"username": "card_seller"}
  },
  "quantity": 1,
  "reserved_until": "2025-06-19T12:30:00Z",
  "subtotal": "299.99",
  "created_at": "2025-06-19T12:00:00Z"
}
```

### Order Model

**Django Model Fields:**
```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Addresses
    buyer_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='buyer_orders')
    
    # Payment
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "buyer": {
    "id": 1,
    "username": "buyer_user",
    "email": "buyer@example.com"
  },
  "status": "pending",
  "base_price": "299.99",
  "platform_commission": "15.00",
  "buyer_processing_fee": "18.00",
  "buyer_shipping_fee": "10.00",
  "buyer_total_price": "342.99",
  "buyer_address": {
    "street": "123 Main St",
    "city": "Paris",
    "country": "France"
  },
  "items": [
    {
      "id": 1,
      "listing": {
        "product": {"name": "Charizard"},
        "price": "299.99"
      },
      "quantity": 1,
      "unit_price": "299.99",
      "total_price": "299.99"
    }
  ],
  "shipped_at": null,
  "delivered_at": null,
  "created_at": "2025-06-19T12:00:00Z",
  "updated_at": "2025-06-19T12:00:00Z"
}
```

### OrderItem Model

**Django Model Fields:**
```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
```

**JSON Response:**
```json
{
  "id": 1,
  "listing": {
    "id": 1,
    "product": {"name": "Charizard"},
    "seller": {"username": "card_seller"}
  },
  "quantity": 1,
  "unit_price": "299.99",
  "total_price": "299.99"
}
```

## Collections Models

### Collection Model

**Django Model Fields:**
```python
class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    variants = models.ManyToManyField(Variant, through='CollectionItem', related_name='collections')
```

**JSON Response:**
```json
{
  "id": 1,
  "name": "My Pokemon Collection",
  "description": "Rare Pokemon cards from Base Set",
  "is_public": true,
  "item_count": 25,
  "total_value": "2500.00",
  "items": [
    {
      "id": 1,
      "variant": {
        "product": {"name": "Charizard"},
        "condition": {"label": "Near Mint"}
      },
      "quantity": 1,
      "acquired_date": "2025-06-19T10:00:00Z",
      "notes": "First edition, perfect condition"
    }
  ],
  "created_at": "2025-06-19T10:00:00Z",
  "updated_at": "2025-06-19T10:00:00Z"
}
```

### CollectionItem Model

**Django Model Fields:**
```python
class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    acquired_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
```

## Dispute Models

### Dispute Model

**Django Model Fields:**
```python
class Dispute(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes')
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_disputes')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_disputes')
    
    reason = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "order": {
    "id": 1,
    "buyer": {"username": "buyer_user"},
    "total_price": "342.99"
  },
  "initiator": {
    "id": 1,
    "username": "buyer_user"
  },
  "moderator": null,
  "reason": "Item not as described",
  "description": "The card condition was not as advertised",
  "status": "open",
  "resolution": "",
  "messages": [
    {
      "id": 1,
      "sender": {"username": "buyer_user"},
      "message": "The card has visible damage not mentioned",
      "created_at": "2025-06-19T12:00:00Z"
    }
  ],
  "resolved_at": null,
  "created_at": "2025-06-19T12:00:00Z",
  "updated_at": "2025-06-19T12:00:00Z"
}
```

### DisputeMessage Model

**Django Model Fields:**
```python
class DisputeMessage(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='dispute_attachments/', blank=True, null=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "sender": {
    "id": 1,
    "username": "buyer_user"
  },
  "message": "Here are photos showing the damage",
  "attachment": "https://media.fliiply.com/dispute_attachments/evidence.jpg",
  "created_at": "2025-06-19T12:30:00Z"
}
```

## Search Models

### SearchHistory Model

**Django Model Fields:**
```python
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    results_count = models.IntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)
```

**JSON Response:**
```json
{
  "id": 1,
  "query": "charizard base set",
  "results_count": 15,
  "searched_at": "2025-06-19T12:00:00Z"
}
```

## Serializer Field Types Reference

### Common Field Types Used

| Django Field | JSON Type | Example Value | Description |
|-------------|-----------|---------------|-------------|
| `CharField` | `string` | `"Charizard"` | Text field |
| `TextField` | `string` | `"Long description..."` | Large text |
| `EmailField` | `string` | `"user@example.com"` | Email format |
| `IntegerField` | `number` | `42` | Integer number |
| `DecimalField` | `string` | `"299.99"` | Decimal as string |
| `BooleanField` | `boolean` | `true` | True/false value |
| `DateTimeField` | `string` | `"2025-06-19T12:00:00Z"` | ISO 8601 format |
| `DateField` | `string` | `"2025-06-19"` | Date only |
| `URLField` | `string` | `"https://example.com"` | URL format |
| `ImageField` | `string` | `"https://media.../image.jpg"` | Image URL |
| `FileField` | `string` | `"https://media.../file.pdf"` | File URL |
| `ForeignKey` | `object` | `{"id": 1, "name": "..."}` | Related object |
| `ManyToManyField` | `array` | `[{"id": 1}, {"id": 2}]` | Array of objects |

### Validation Rules

#### User Model Validation
- `username`: Required, unique, 3-150 characters
- `email`: Required, unique, valid email format
- `password`: Minimum 8 characters, not too common

#### Product Model Validation
- `name`: Required, max 255 characters
- `price`: Positive decimal, max 10 digits with 2 decimal places
- `stock`: Non-negative integer

#### Order Model Validation
- `quantity`: Positive integer
- `price`: Positive decimal
- Business rule: Cannot order more than available stock

This documentation provides the complete data model structure for Flutter integration with proper JSON examples and validation rules.