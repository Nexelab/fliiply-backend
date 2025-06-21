# Nuxt 3 API Reference - Fliiply Backend

## API Client Usage Examples

### Authentication Examples

```typescript
// Login Example
const { login } = useAuth()

try {
  await login('username', 'password')
  // User is now authenticated, redirect to dashboard
  await navigateTo('/dashboard')
} catch (error) {
  // Handle login error
  console.error('Login failed:', error.message)
}

// Registration Example
const { register } = useAuth()

try {
  await register({
    username: 'newuser',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    password: 'securepassword',
    confirm_password: 'securepassword',
    accept_terms: true,
    role: 'particulier'
  })
} catch (error) {
  console.error('Registration failed:', error)
}

// Email Verification
const { verifyEmail } = useAuth()

try {
  await verifyEmail('john@example.com', '123456')
  // Email verified successfully
} catch (error) {
  console.error('Verification failed:', error)
}
```

### Product Management Examples

```typescript
// Fetch Products with Filters
const productsStore = useProductsStore()

// Get all products
await productsStore.fetchProducts()

// Get products with filters
await productsStore.fetchProducts({
  tcg_type: 'pokemon',
  page: 1,
  page_size: 20
})

// Search Products
await productsStore.searchProducts({
  q: 'charizard',
  tcg_type: 'pokemon',
  min_price: 50,
  max_price: 200,
  condition: 'near_mint'
})

// Get Product by ID
const product = await productsStore.fetchProduct(123)

// Get Search Suggestions
const suggestions = await productsStore.getSearchSuggestions('char')
```

### Cart Management Examples

```typescript
const cartStore = useCartStore()

// Add item to cart
try {
  await cartStore.addToCart(listingId, quantity)
  // Show success message
} catch (error) {
  // Handle error (out of stock, etc.)
}

// Update cart item quantity
await cartStore.updateCartItem(cartItemId, newQuantity)

// Remove item from cart
await cartStore.removeFromCart(cartItemId)

// Get cart items
await cartStore.fetchCartItems()

// Access cart data
const itemCount = cartStore.itemCount
const subtotal = cartStore.subtotal
const isEmpty = !cartStore.isNotEmpty
```

### Order Management Examples

```typescript
const ordersStore = useOrdersStore()

// Create order from cart
try {
  const order = await ordersStore.createOrder(
    [cartItemId1, cartItemId2], // Cart item IDs
    addressId // Shipping address ID
  )
  
  // Redirect to payment
  await navigateTo(`/orders/${order.id}/payment`)
} catch (error) {
  console.error('Order creation failed:', error)
}

// Pay for order (Stripe integration)
await ordersStore.payForOrder(orderId, paymentMethodId)

// Fetch user orders
await ordersStore.fetchOrders()

// Get specific order
const order = await ordersStore.fetchOrder(orderId)
```

## Composables Reference

### useAuth()

```typescript
const {
  // State
  isAuthenticated, // Ref<boolean>
  user, // Ref<User | null>
  isLoading, // Ref<boolean>
  
  // Actions
  login, // (username: string, password: string) => Promise<void>
  register, // (userData: RegisterData) => Promise<void>
  logout, // () => Promise<void>
  becomeSeller, // () => Promise<any>
  verifyEmail, // (email: string, otp: string) => Promise<boolean>
  
  // Token management
  getToken, // () => Promise<string | null>
  refreshToken, // () => Promise<boolean>
} = useAuth()
```

### useApi()

```typescript
const {
  get, // <T>(endpoint: string, options?: RequestOptions) => Promise<ApiResponse<T>>
  post, // <T>(endpoint: string, body?: any, options?: RequestOptions) => Promise<ApiResponse<T>>
  put, // <T>(endpoint: string, body?: any, options?: RequestOptions) => Promise<ApiResponse<T>>
  patch, // <T>(endpoint: string, body?: any, options?: RequestOptions) => Promise<ApiResponse<T>>
  delete, // <T>(endpoint: string, options?: RequestOptions) => Promise<ApiResponse<T>>
} = useApi()

// Usage examples
const response = await api.get<Product[]>('/products/')
const newProduct = await api.post<Product>('/products/', productData)
const updatedProduct = await api.put<Product>(`/products/${id}/`, updateData)
await api.delete(`/products/${id}/`)
```

## Store Actions Reference

### Products Store Actions

```typescript
const productsStore = useProductsStore()

// Fetch products with optional filters
await productsStore.fetchProducts({
  tcg_type?: 'pokemon' | 'yugioh' | 'magic' | 'other'
  category?: number
  page?: number
  page_size?: number
})

// Fetch single product
const product = await productsStore.fetchProduct(productId: number)

// Search products
const results = await productsStore.searchProducts({
  q?: string // Search query
  tcg_type?: string
  block?: string
  series?: string
  language?: string
  version?: string
  condition?: string
  grade?: string
  min_price?: number
  max_price?: number
  availability?: 'in_stock' | 'out_of_stock'
  page?: number
  page_size?: number
})

// Get search suggestions
const suggestions = await productsStore.getSearchSuggestions(query: string)

// Fetch categories
await productsStore.fetchCategories()

// Clear search results
productsStore.clearSearch()
```

### Cart Store Actions

```typescript
const cartStore = useCartStore()

// Fetch cart items
await cartStore.fetchCartItems()

// Add item to cart
const cartItem = await cartStore.addToCart(
  listingId: number,
  quantity: number = 1
)

// Update cart item
const updatedItem = await cartStore.updateCartItem(
  cartItemId: number,
  quantity: number
)

// Remove from cart
await cartStore.removeFromCart(cartItemId: number)

// Clear entire cart
await cartStore.clearCart()

// Getters (computed)
const itemCount = cartStore.itemCount // number
const subtotal = cartStore.subtotal // number
const isNotEmpty = cartStore.isNotEmpty // boolean
```

### Orders Store Actions

```typescript
const ordersStore = useOrdersStore()

// Fetch user orders
await ordersStore.fetchOrders()

// Fetch specific order
const order = await ordersStore.fetchOrder(orderId: number)

// Create order
const newOrder = await ordersStore.createOrder(
  cartItemIds: number[],
  buyerAddressId: number
)

// Pay for order
const paymentResult = await ordersStore.payForOrder(
  orderId: number,
  paymentMethodId: string
)
```

### Auth Store Actions

```typescript
const authStore = useAuthStore()

// Login
await authStore.login(username: string, password: string)

// Register
await authStore.register({
  username: string
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
  accept_terms: boolean
  role?: 'particulier' | 'professionnel'
  subscribed_to_newsletter?: boolean
})

// Fetch current user
await authStore.fetchUser()

// Refresh tokens
const success = await authStore.refreshTokens()

// Logout
await authStore.logout()

// Initialize auth (call on app start)
await authStore.initializeAuth()

// Become seller
const result = await authStore.becomeSeller()

// Verify email
const verified = await authStore.verifyEmail(email: string, otp: string)
```

## Component Examples

### Search Component with Filters

```vue
<template>
  <div>
    <!-- Search Input -->
    <ProductsSearchBar
      v-model="searchQuery"
      @search="handleSearch"
    />
    
    <!-- Filters -->
    <div class="grid grid-cols-4 gap-4 mt-4">
      <select v-model="filters.tcg_type" @change="applyFilters">
        <option value="">All TCG Types</option>
        <option value="pokemon">Pokemon</option>
        <option value="yugioh">Yu-Gi-Oh</option>
        <option value="magic">Magic</option>
      </select>
      
      <input
        v-model.number="filters.min_price"
        type="number"
        placeholder="Min Price"
        @input="applyFilters"
      />
      
      <input
        v-model.number="filters.max_price"
        type="number"
        placeholder="Max Price"
        @input="applyFilters"
      />
      
      <select v-model="filters.availability" @change="applyFilters">
        <option value="">All</option>
        <option value="in_stock">In Stock</option>
        <option value="out_of_stock">Out of Stock</option>
      </select>
    </div>
    
    <!-- Results -->
    <div class="grid grid-cols-4 gap-4 mt-6">
      <ProductsProductCard
        v-for="product in searchResults"
        :key="product.id"
        :product="product"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const productsStore = useProductsStore()

const searchQuery = ref('')
const filters = reactive({
  tcg_type: '',
  min_price: undefined as number | undefined,
  max_price: undefined as number | undefined,
  availability: '',
})

const searchResults = computed(() => productsStore.searchResults)

const handleSearch = async () => {
  await productsStore.searchProducts({
    q: searchQuery.value,
    ...filters,
  })
}

const applyFilters = useDebounceFn(() => {
  if (searchQuery.value) {
    handleSearch()
  }
}, 500)
</script>
```

### Cart Management Component

```vue
<template>
  <div>
    <!-- Cart Items -->
    <div v-if="cartItems.length === 0" class="text-center py-8">
      <p class="text-gray-500">Your cart is empty</p>
      <NuxtLink to="/products" class="text-blue-600 hover:text-blue-500">
        Continue Shopping
      </NuxtLink>
    </div>
    
    <div v-else>
      <div class="space-y-4">
        <CartCartItem
          v-for="item in cartItems"
          :key="item.id"
          :item="item"
          @quantity-updated="handleQuantityUpdate"
          @removed="handleItemRemoval"
        />
      </div>
      
      <!-- Cart Summary -->
      <div class="bg-gray-50 p-4 rounded-lg mt-6">
        <div class="flex justify-between items-center mb-4">
          <span class="text-lg font-semibold">Total Items:</span>
          <span>{{ itemCount }}</span>
        </div>
        
        <div class="flex justify-between items-center mb-4">
          <span class="text-lg font-semibold">Subtotal:</span>
          <span class="text-xl font-bold">€{{ subtotal.toFixed(2) }}</span>
        </div>
        
        <button
          @click="proceedToCheckout"
          :disabled="!canCheckout"
          class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const cartStore = useCartStore()
const { isAuthenticated } = useAuth()

const cartItems = computed(() => cartStore.items)
const itemCount = computed(() => cartStore.itemCount)
const subtotal = computed(() => cartStore.subtotal)
const canCheckout = computed(() => isAuthenticated.value && cartItems.value.length > 0)

onMounted(async () => {
  if (isAuthenticated.value) {
    await cartStore.fetchCartItems()
  }
})

const handleQuantityUpdate = async (cartItemId: number, newQuantity: number) => {
  try {
    await cartStore.updateCartItem(cartItemId, newQuantity)
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message)
  }
}

const handleItemRemoval = async (cartItemId: number) => {
  try {
    await cartStore.removeFromCart(cartItemId)
    const { $toast } = useNuxtApp()
    $toast.success('Item removed from cart')
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message)
  }
}

const proceedToCheckout = async () => {
  if (!isAuthenticated.value) {
    await navigateTo('/auth/login?redirect=/checkout')
    return
  }
  
  await navigateTo('/checkout')
}
</script>
```

### Product Details with Add to Cart

```vue
<template>
  <div v-if="product" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
    <!-- Product Images -->
    <div>
      <img
        :src="currentImage?.image || '/placeholder.jpg'"
        :alt="product.name"
        class="w-full h-96 object-cover rounded-lg"
      />
      
      <div v-if="product.images.length > 1" class="grid grid-cols-4 gap-2 mt-4">
        <button
          v-for="image in product.images"
          :key="image.id"
          @click="currentImage = image"
          class="border-2 rounded"
          :class="currentImage?.id === image.id ? 'border-blue-500' : 'border-gray-200'"
        >
          <img
            :src="image.image"
            :alt="image.alt_text"
            class="w-full h-20 object-cover rounded"
          />
        </button>
      </div>
    </div>
    
    <!-- Product Info -->
    <div>
      <h1 class="text-3xl font-bold mb-4">{{ product.name }}</h1>
      
      <div class="flex items-center space-x-4 mb-4">
        <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
          {{ product.tcg_type.toUpperCase() }}
        </span>
        <span v-if="product.series" class="text-gray-600">
          {{ product.series }}
        </span>
      </div>
      
      <p v-if="product.description" class="text-gray-700 mb-6">
        {{ product.description }}
      </p>
      
      <!-- Available Listings -->
      <div class="space-y-4">
        <h3 class="text-lg font-semibold">Available Listings</h3>
        
        <div
          v-for="listing in availableListings"
          :key="listing.id"
          class="border rounded-lg p-4 flex justify-between items-center"
        >
          <div>
            <p class="font-semibold text-lg">€{{ listing.price }}</p>
            <p class="text-sm text-gray-600">
              {{ listing.variant.condition.label }} - {{ listing.variant.language.name }}
            </p>
            <p class="text-xs text-gray-500">
              Sold by {{ listing.seller.username }} • Stock: {{ listing.stock }}
            </p>
          </div>
          
          <div class="flex items-center space-x-2">
            <select v-model="quantities[listing.id]" class="border rounded px-2 py-1">
              <option v-for="n in Math.min(listing.stock, 10)" :key="n" :value="n">
                {{ n }}
              </option>
            </select>
            
            <button
              @click="addToCart(listing.id, quantities[listing.id] || 1)"
              :disabled="listing.stock === 0 || isAddingToCart"
              class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  product: Product
  listings: Listing[]
}

const props = defineProps<Props>()

const cartStore = useCartStore()

const currentImage = ref<ProductImage>()
const quantities = reactive<Record<number, number>>({})
const isAddingToCart = ref(false)

const availableListings = computed(() =>
  props.listings.filter(listing => listing.status === 'active')
)

onMounted(() => {
  // Set primary image
  currentImage.value = props.product.images.find(img => img.is_primary) || props.product.images[0]
  
  // Initialize quantities
  availableListings.value.forEach(listing => {
    quantities[listing.id] = 1
  })
})

const addToCart = async (listingId: number, quantity: number) => {
  isAddingToCart.value = true
  
  try {
    await cartStore.addToCart(listingId, quantity)
    const { $toast } = useNuxtApp()
    $toast.success('Added to cart!')
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message || 'Failed to add to cart')
  } finally {
    isAddingToCart.value = false
  }
}
</script>
```

## Error Handling Patterns

### API Error Handling

```typescript
// Global error handler
const handleApiError = (error: any) => {
  const { $toast } = useNuxtApp()
  
  if (error.error_code) {
    switch (error.error_code) {
      case 'validation_error':
        // Handle validation errors
        if (error.details) {
          Object.values(error.details).flat().forEach((message: any) => {
            $toast.error(message)
          })
        } else {
          $toast.error(error.message)
        }
        break
        
      case 'authentication_failed':
        $toast.error('Please log in to continue')
        navigateTo('/auth/login')
        break
        
      case 'permission_denied':
        $toast.error('You do not have permission to perform this action')
        break
        
      case 'not_found':
        $toast.error('The requested resource was not found')
        break
        
      case 'throttled':
        $toast.error('Too many requests. Please try again later.')
        break
        
      default:
        $toast.error(error.message || 'An error occurred')
    }
  } else {
    $toast.error(error.message || 'An unexpected error occurred')
  }
}

// Usage in components
try {
  await someApiCall()
} catch (error) {
  handleApiError(error)
}
```

### Form Validation

```typescript
// Form validation composable
export const useFormValidation = () => {
  const errors = ref<Record<string, string[]>>({})
  
  const validateField = (field: string, value: any, rules: ValidationRule[]) => {
    const fieldErrors: string[] = []
    
    rules.forEach(rule => {
      const result = rule(value)
      if (result !== true) {
        fieldErrors.push(result)
      }
    })
    
    errors.value[field] = fieldErrors
    return fieldErrors.length === 0
  }
  
  const clearErrors = (field?: string) => {
    if (field) {
      delete errors.value[field]
    } else {
      errors.value = {}
    }
  }
  
  const hasErrors = computed(() => 
    Object.values(errors.value).some(fieldErrors => fieldErrors.length > 0)
  )
  
  return {
    errors: readonly(errors),
    validateField,
    clearErrors,
    hasErrors
  }
}

// Validation rules
export const validationRules = {
  required: (value: any) => !!value || 'This field is required',
  email: (value: string) => 
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Invalid email format',
  minLength: (min: number) => (value: string) =>
    value.length >= min || `Minimum ${min} characters required`,
  maxLength: (max: number) => (value: string) =>
    value.length <= max || `Maximum ${max} characters allowed`,
  numeric: (value: any) => 
    !isNaN(Number(value)) || 'Must be a number',
  positive: (value: number) => 
    value > 0 || 'Must be a positive number',
}
```

## Performance Optimization Tips

### Lazy Loading and Code Splitting

```vue
<!-- Lazy load components -->
<template>
  <div>
    <LazyProductsProductCard
      v-for="product in products"
      :key="product.id"
      :product="product"
    />
  </div>
</template>

<!-- Async component loading -->
<script setup lang="ts">
const AsyncProductDetails = defineAsyncComponent(() => 
  import('~/components/products/ProductDetails.vue')
)
</script>
```

### Image Optimization

```vue
<template>
  <NuxtImg
    :src="product.image"
    :alt="product.name"
    width="300"
    height="300"
    format="webp"
    quality="80"
    loading="lazy"
    class="product-image"
  />
</template>
```

### Search Debouncing

```typescript
// Debounced search
const debouncedSearch = useDebounceFn(async (query: string) => {
  if (query.length >= 2) {
    await productsStore.searchProducts({ q: query })
  }
}, 300)

watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery)
})
```

This reference provides comprehensive examples and patterns for building a production-ready Nuxt 3 application that integrates seamlessly with the Django backend.