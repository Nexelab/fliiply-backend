# Nuxt 3 Integration Guide - Fliiply Backend

## Quick Start

This guide provides everything needed to integrate your Nuxt 3 frontend with the Fliiply Django backend. The backend provides a complete TCG marketplace API with JWT authentication, payment processing, and comprehensive product management.

## Project Setup

### Dependencies

```bash
# Install required packages
npm install --save @nuxtjs/google-fonts
npm install --save @pinia/nuxt
npm install --save @vueuse/nuxt
npm install --save @nuxtjs/tailwindcss
npm install --save @stripe/stripe-js
npm install --save vue-toastification
npm install --save @headlessui/vue
npm install --save @heroicons/vue
```

### Nuxt Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  devtools: { enabled: true },
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/google-fonts',
  ],
  
  runtimeConfig: {
    // Private keys (only available on server-side)
    stripeSecretKey: process.env.STRIPE_SECRET_KEY,
    
    // Public keys (exposed to client-side)
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      apiVersion: '/api/v1',
      stripePublicKey: process.env.NUXT_PUBLIC_STRIPE_PUBLIC_KEY,
      appUrl: process.env.NUXT_PUBLIC_APP_URL || 'http://localhost:3000',
    }
  },
  
  css: ['~/assets/css/main.css'],
  
  googleFonts: {
    families: {
      Inter: [400, 500, 600, 700],
    }
  },
  
  tailwindcss: {
    cssPath: '~/assets/css/tailwind.css',
  },
  
  // Global page headers
  app: {
    head: {
      title: 'Fliiply - TCG Marketplace',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'Trading Card Game marketplace for buying, selling, and collecting rare cards' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },
  
  // Auto-import components
  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],
})
```

### Environment Variables

```bash
# .env
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
NUXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
NUXT_PUBLIC_APP_URL=http://localhost:3000
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
```

## API Configuration

### API Client Setup

```typescript
// composables/useApi.ts
interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error_code?: string
  details?: Record<string, string[]>
  meta?: {
    pagination?: {
      count: number
      next: string | null
      previous: string | null
      page_size: number
    }
  }
  timestamp: string
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: any
  query?: Record<string, any>
  headers?: Record<string, string>
  auth?: boolean
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const { getToken, refreshToken, logout } = useAuth()
  
  const baseUrl = `${config.public.apiBaseUrl}${config.public.apiVersion}`
  
  const makeRequest = async <T = any>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> => {
    const {
      method = 'GET',
      body,
      query,
      headers = {},
      auth = true
    } = options
    
    // Build URL with query parameters
    let url = `${baseUrl}${endpoint}`
    if (query) {
      const searchParams = new URLSearchParams()
      Object.entries(query).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          searchParams.append(key, String(value))
        }
      })
      if (searchParams.toString()) {
        url += `?${searchParams.toString()}`
      }
    }
    
    // Set headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers
    }
    
    // Add authentication if required
    if (auth) {
      const token = await getToken()
      if (token) {
        requestHeaders.Authorization = `Bearer ${token}`
      }
    }
    
    try {
      const response = await $fetch<ApiResponse<T>>(url, {
        method,
        headers: requestHeaders,
        body: body ? JSON.stringify(body) : undefined,
      })
      
      return response
    } catch (error: any) {
      // Handle token expiration
      if (error.status === 401 && auth) {
        const refreshed = await refreshToken()
        if (refreshed) {
          // Retry request with new token
          const newToken = await getToken()
          if (newToken) {
            requestHeaders.Authorization = `Bearer ${newToken}`
            try {
              const retryResponse = await $fetch<ApiResponse<T>>(url, {
                method,
                headers: requestHeaders,
                body: body ? JSON.stringify(body) : undefined,
              })
              return retryResponse
            } catch (retryError: any) {
              throw retryError
            }
          }
        } else {
          await logout()
          await navigateTo('/auth/login')
        }
      }
      
      // Handle other errors
      if (error.data) {
        throw error.data
      } else {
        throw {
          success: false,
          message: error.message || 'Network error occurred',
          error_code: 'network_error'
        }
      }
    }
  }
  
  return {
    get: <T = any>(endpoint: string, options: Omit<RequestOptions, 'method'> = {}) =>
      makeRequest<T>(endpoint, { ...options, method: 'GET' }),
    
    post: <T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}) =>
      makeRequest<T>(endpoint, { ...options, method: 'POST', body }),
    
    put: <T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}) =>
      makeRequest<T>(endpoint, { ...options, method: 'PUT', body }),
    
    patch: <T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}) =>
      makeRequest<T>(endpoint, { ...options, method: 'PATCH', body }),
    
    delete: <T = any>(endpoint: string, options: Omit<RequestOptions, 'method'> = {}) =>
      makeRequest<T>(endpoint, { ...options, method: 'DELETE' }),
  }
}
```

## Authentication System

### Auth Store (Pinia)

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_buyer: boolean
  is_seller: boolean
  is_verifier: boolean
  role: 'particulier' | 'professionnel'
  is_email_verified: boolean
  is_kyc_verified: boolean
  date_joined: string
  last_login?: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
  }),
  
  getters: {
    fullName: (state) => 
      state.user ? `${state.user.first_name} ${state.user.last_name}` : '',
    
    canSell: (state) => 
      state.user?.is_seller && state.user?.is_email_verified && state.user?.is_kyc_verified,
    
    isProfessional: (state) => 
      state.user?.role === 'professionnel',
  },
  
  actions: {
    async login(username: string, password: string) {
      this.isLoading = true
      const api = useApi()
      
      try {
        const response = await api.post('/auth/login/', {
          username,
          password,
        }, { auth: false })
        
        if (response.success && response.data) {
          this.accessToken = response.data.access
          this.refreshToken = response.data.refresh
          
          // Save tokens to cookies
          const accessCookie = useCookie('access_token', {
            maxAge: 60 * 60, // 1 hour
            secure: true,
            sameSite: 'strict',
          })
          const refreshCookie = useCookie('refresh_token', {
            maxAge: 24 * 60 * 60, // 1 day
            secure: true,
            sameSite: 'strict',
          })
          
          accessCookie.value = this.accessToken
          refreshCookie.value = this.refreshToken
          
          // Fetch user profile
          await this.fetchUser()
          
          return { success: true }
        } else {
          throw new Error(response.message || 'Login failed')
        }
      } catch (error: any) {
        this.logout()
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async register(userData: {
      username: string
      first_name: string
      last_name: string
      email: string
      password: string
      confirm_password: string
      accept_terms: boolean
      role?: string
      subscribed_to_newsletter?: boolean
    }) {
      this.isLoading = true
      const api = useApi()
      
      try {
        const response = await api.post('/auth/register/', userData, { auth: false })
        
        if (response.success && response.data) {
          this.accessToken = response.data.access
          this.refreshToken = response.data.refresh
          
          // Save tokens
          const accessCookie = useCookie('access_token')
          const refreshCookie = useCookie('refresh_token')
          accessCookie.value = this.accessToken
          refreshCookie.value = this.refreshToken
          
          await this.fetchUser()
          return { success: true }
        } else {
          throw new Error(response.message || 'Registration failed')
        }
      } catch (error: any) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchUser() {
      if (!this.accessToken) return
      
      const api = useApi()
      try {
        const response = await api.get('/users/me/')
        if (response.success && response.data) {
          this.user = response.data
          this.isAuthenticated = true
        }
      } catch (error) {
        this.logout()
        throw error
      }
    },
    
    async refreshTokens() {
      if (!this.refreshToken) return false
      
      const api = useApi()
      try {
        const response = await api.post('/auth/token/refresh/', {
          refresh: this.refreshToken,
        }, { auth: false })
        
        if (response.success && response.data) {
          this.accessToken = response.data.access
          
          const accessCookie = useCookie('access_token')
          accessCookie.value = this.accessToken
          
          return true
        }
      } catch (error) {
        this.logout()
      }
      
      return false
    },
    
    async logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      this.isAuthenticated = false
      
      // Clear cookies
      const accessCookie = useCookie('access_token')
      const refreshCookie = useCookie('refresh_token')
      accessCookie.value = null
      refreshCookie.value = null
      
      // Redirect to login
      await navigateTo('/auth/login')
    },
    
    async initializeAuth() {
      const accessCookie = useCookie('access_token')
      const refreshCookie = useCookie('refresh_token')
      
      this.accessToken = accessCookie.value
      this.refreshToken = refreshCookie.value
      
      if (this.accessToken) {
        try {
          await this.fetchUser()
        } catch (error) {
          // Try to refresh token
          if (this.refreshToken) {
            const refreshed = await this.refreshTokens()
            if (refreshed) {
              await this.fetchUser()
            }
          }
        }
      }
    },
    
    async becomeSeller() {
      const api = useApi()
      try {
        const response = await api.post('/users/become_seller/')
        if (response.success) {
          await this.fetchUser() // Refresh user data
          return response.data
        }
        throw new Error(response.message || 'Failed to become seller')
      } catch (error) {
        throw error
      }
    },
    
    async verifyEmail(email: string, otp: string) {
      const api = useApi()
      try {
        const response = await api.post('/auth/verify-email/', {
          email,
          otp,
        }, { auth: false })
        
        if (response.success) {
          await this.fetchUser() // Refresh user data
          return true
        }
        throw new Error(response.message || 'Email verification failed')
      } catch (error) {
        throw error
      }
    },
  },
})
```

### Auth Composable

```typescript
// composables/useAuth.ts
export const useAuth = () => {
  const authStore = useAuthStore()
  
  const getToken = async (): Promise<string | null> => {
    return authStore.accessToken
  }
  
  const refreshToken = async (): Promise<boolean> => {
    return await authStore.refreshTokens()
  }
  
  const logout = async (): Promise<void> => {
    await authStore.logout()
  }
  
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)
  const isLoading = computed(() => authStore.isLoading)
  
  return {
    getToken,
    refreshToken,
    logout,
    isAuthenticated,
    user,
    isLoading,
    login: authStore.login,
    register: authStore.register,
    becomeSeller: authStore.becomeSeller,
    verifyEmail: authStore.verifyEmail,
  }
}
```

## TypeScript Interfaces

### Core Data Types

```typescript
// types/index.ts
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_buyer: boolean
  is_seller: boolean
  is_verifier: boolean
  role: 'particulier' | 'professionnel'
  is_email_verified: boolean
  is_kyc_verified: boolean
  date_joined: string
  last_login?: string
}

export interface Address {
  id: number
  address_type: 'shipping' | 'billing'
  street: string
  city: string
  state: string
  postal_code: string
  country: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  parent?: number
  image?: string
  is_active: boolean
  children?: Category[]
}

export interface ProductImage {
  id: number
  image: string
  alt_text?: string
  is_primary: boolean
  created_at: string
}

export interface Product {
  id: number
  tcg_type: 'pokemon' | 'yugioh' | 'magic' | 'other'
  name: string
  series?: string
  block?: string
  set_number?: string
  description?: string
  categories: Category[]
  images: ProductImage[]
  average_price?: string
  total_stock: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Language {
  id: number
  name: string
  code: string
  is_active: boolean
}

export interface Version {
  id: number
  name: string
  code: string
  description?: string
  is_active: boolean
}

export interface Condition {
  id: number
  label: string
  code: string
  description?: string
  quality_score: number
  is_active: boolean
}

export interface Grade {
  id: number
  grader: string
  value: string
  description?: string
  numeric_value: string
  is_active: boolean
}

export interface Variant {
  id: number
  product: Partial<Product>
  language: Language
  version: Version
  condition: Condition
  grade?: Grade
  is_active: boolean
  created_at: string
}

export interface Listing {
  id: number
  seller: Partial<User>
  product: Partial<Product>
  variant: Variant
  status: 'draft' | 'active' | 'sold' | 'inactive'
  price: string
  stock: number
  description?: string
  is_negotiable: boolean
  created_at: string
  updated_at: string
}

export interface CartItem {
  id: number
  listing: Listing
  quantity: number
  reserved_until: string
  subtotal: string
  created_at: string
}

export interface OrderItem {
  id: number
  listing: Listing
  quantity: number
  unit_price: string
  total_price: string
}

export interface Order {
  id: number
  buyer: User
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled' | 'disputed'
  base_price: string
  platform_commission: string
  buyer_processing_fee: string
  buyer_shipping_fee: string
  buyer_total_price: string
  buyer_address: Address
  items: OrderItem[]
  shipped_at?: string
  delivered_at?: string
  created_at: string
  updated_at: string
}

export interface Collection {
  id: number
  name: string
  description?: string
  is_public: boolean
  item_count: number
  total_value?: string
  created_at: string
  updated_at: string
}

export interface CollectionItem {
  id: number
  variant: Variant
  quantity: number
  acquired_date?: string
  notes?: string
}

export interface Dispute {
  id: number
  order: Partial<Order>
  initiator: User
  moderator?: User
  reason: string
  description: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  resolution?: string
  resolved_at?: string
  created_at: string
  updated_at: string
}

export interface SearchFilters {
  q?: string
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
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
```

## Stores (Pinia)

### Products Store

```typescript
// stores/products.ts
import { defineStore } from 'pinia'

interface ProductsState {
  products: Product[]
  categories: Category[]
  currentProduct: Product | null
  searchResults: Product[]
  searchFilters: SearchFilters
  isLoading: boolean
  pagination: {
    count: number
    next: string | null
    previous: string | null
    currentPage: number
    totalPages: number
  }
}

export const useProductsStore = defineStore('products', {
  state: (): ProductsState => ({
    products: [],
    categories: [],
    currentProduct: null,
    searchResults: [],
    searchFilters: {},
    isLoading: false,
    pagination: {
      count: 0,
      next: null,
      previous: null,
      currentPage: 1,
      totalPages: 0,
    },
  }),
  
  getters: {
    featuredProducts: (state) => state.products.slice(0, 8),
    
    productsByCategory: (state) => (categoryId: number) =>
      state.products.filter(product => 
        product.categories.some(cat => cat.id === categoryId)
      ),
    
    mainCategories: (state) => 
      state.categories.filter(cat => !cat.parent),
  },
  
  actions: {
    async fetchProducts(filters: SearchFilters = {}) {
      this.isLoading = true
      const api = useApi()
      
      try {
        const response = await api.get<PaginatedResponse<Product>>('/products/', {
          query: filters,
          auth: false,
        })
        
        if (response.success && response.data) {
          this.products = response.data.results
          this.updatePagination(response.data, filters.page || 1)
        }
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchProduct(id: number) {
      this.isLoading = true
      const api = useApi()
      
      try {
        const response = await api.get<Product>(`/products/${id}/`, { auth: false })
        
        if (response.success && response.data) {
          this.currentProduct = response.data
          return response.data
        }
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async searchProducts(filters: SearchFilters) {
      this.isLoading = true
      this.searchFilters = { ...filters }
      const api = useApi()
      
      try {
        const response = await api.get<PaginatedResponse<Product>>('/search/', {
          query: filters,
          auth: false,
        })
        
        if (response.success && response.data) {
          this.searchResults = response.data.results
          this.updatePagination(response.data, filters.page || 1)
          return response.data.results
        }
        return []
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async getSearchSuggestions(query: string): Promise<string[]> {
      if (query.length < 2) return []
      
      const api = useApi()
      try {
        const response = await api.get<string[]>('/search/suggestions/', {
          query: { query },
          auth: false,
        })
        
        return response.success && response.data ? response.data : []
      } catch (error) {
        return []
      }
    },
    
    async fetchCategories() {
      const api = useApi()
      
      try {
        const response = await api.get<PaginatedResponse<Category>>('/categories/', { auth: false })
        
        if (response.success && response.data) {
          this.categories = response.data.results
        }
      } catch (error) {
        throw error
      }
    },
    
    updatePagination(data: PaginatedResponse<any>, currentPage: number) {
      this.pagination = {
        count: data.count,
        next: data.next,
        previous: data.previous,
        currentPage,
        totalPages: Math.ceil(data.count / 20), // Assuming 20 items per page
      }
    },
    
    clearSearch() {
      this.searchResults = []
      this.searchFilters = {}
    },
  },
})
```

### Cart Store

```typescript
// stores/cart.ts
import { defineStore } from 'pinia'

interface CartState {
  items: CartItem[]
  isLoading: boolean
  total: {
    itemCount: number
    subtotal: number
  }
}

export const useCartStore = defineStore('cart', {
  state: (): CartState => ({
    items: [],
    isLoading: false,
    total: {
      itemCount: 0,
      subtotal: 0,
    },
  }),
  
  getters: {
    itemCount: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    
    subtotal: (state) => state.items.reduce(
      (sum, item) => sum + parseFloat(item.subtotal), 0
    ),
    
    isNotEmpty: (state) => state.items.length > 0,
  },
  
  actions: {
    async fetchCartItems() {
      this.isLoading = true
      const api = useApi()
      
      try {
        const response = await api.get<PaginatedResponse<CartItem>>('/cart/')
        
        if (response.success && response.data) {
          this.items = response.data.results
          this.calculateTotal()
        }
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async addToCart(listingId: number, quantity: number = 1) {
      const api = useApi()
      
      try {
        const response = await api.post<CartItem>('/cart/', {
          listing: listingId,
          quantity,
        })
        
        if (response.success && response.data) {
          await this.fetchCartItems() // Refresh cart
          return response.data
        }
      } catch (error) {
        throw error
      }
    },
    
    async updateCartItem(cartItemId: number, quantity: number) {
      const api = useApi()
      
      try {
        const response = await api.put<CartItem>(`/cart/${cartItemId}/`, {
          quantity,
        })
        
        if (response.success && response.data) {
          const index = this.items.findIndex(item => item.id === cartItemId)
          if (index !== -1) {
            this.items[index] = response.data
            this.calculateTotal()
          }
          return response.data
        }
      } catch (error) {
        throw error
      }
    },
    
    async removeFromCart(cartItemId: number) {
      const api = useApi()
      
      try {
        const response = await api.delete(`/cart/${cartItemId}/`)
        
        if (response.success) {
          this.items = this.items.filter(item => item.id !== cartItemId)
          this.calculateTotal()
        }
      } catch (error) {
        throw error
      }
    },
    
    async clearCart() {
      const promises = this.items.map(item => this.removeFromCart(item.id))
      await Promise.all(promises)
    },
    
    calculateTotal() {
      this.total = {
        itemCount: this.itemCount,
        subtotal: this.subtotal,
      }
    },
  },
})
```

### Orders Store

```typescript
// stores/orders.ts
import { defineStore } from 'pinia'

interface OrdersState {
  orders: Order[]
  currentOrder: Order | null
  isLoading: boolean
}

export const useOrdersStore = defineStore('orders', {
  state: (): OrdersState => ({
    orders: [],
    currentOrder: null,
    isLoading: false,
  }),
  
  actions: {
    async fetchOrders() {
      this.isLoading = true
      const api = useApi()
      
      try {
        const response = await api.get<PaginatedResponse<Order>>('/orders/')
        
        if (response.success && response.data) {
          this.orders = response.data.results
        }
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchOrder(id: number) {
      this.isLoading = true
      const api = useApi()
      
      try {
        const response = await api.get<Order>(`/orders/${id}/`)
        
        if (response.success && response.data) {
          this.currentOrder = response.data
          return response.data
        }
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async createOrder(cartItemIds: number[], buyerAddressId: number) {
      const api = useApi()
      
      try {
        const response = await api.post<Order>('/orders/', {
          cart_items: cartItemIds,
          buyer_address: buyerAddressId,
        })
        
        if (response.success && response.data) {
          this.orders.unshift(response.data)
          return response.data
        }
      } catch (error) {
        throw error
      }
    },
    
    async payForOrder(orderId: number, paymentMethodId: string) {
      const api = useApi()
      
      try {
        const response = await api.post(`/orders/${orderId}/pay/`, {
          payment_method_id: paymentMethodId,
        })
        
        if (response.success) {
          // Refresh order data
          await this.fetchOrder(orderId)
          return response.data
        }
      } catch (error) {
        throw error
      }
    },
  },
})
```

## Components

### Authentication Components

```vue
<!-- components/auth/LoginForm.vue -->
<template>
  <form @submit.prevent="handleLogin" class="space-y-6">
    <div>
      <label for="username" class="block text-sm font-medium text-gray-700">
        Username
      </label>
      <input
        id="username"
        v-model="form.username"
        type="text"
        required
        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        :disabled="isLoading"
      />
    </div>
    
    <div>
      <label for="password" class="block text-sm font-medium text-gray-700">
        Password
      </label>
      <input
        id="password"
        v-model="form.password"
        type="password"
        required
        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        :disabled="isLoading"
      />
    </div>
    
    <div>
      <button
        type="submit"
        :disabled="isLoading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        <span v-if="!isLoading">Sign In</span>
        <div v-else class="flex items-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Signing in...
        </div>
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
const { login } = useAuth()
const router = useRouter()

const form = reactive({
  username: '',
  password: '',
})

const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  
  try {
    await login(form.username, form.password)
    await router.push('/')
    
    const { $toast } = useNuxtApp()
    $toast.success('Welcome back!')
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message || 'Login failed')
  } finally {
    isLoading.value = false
  }
}
</script>
```

### Product Components

```vue
<!-- components/products/ProductCard.vue -->
<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
    <div class="aspect-w-1 aspect-h-1">
      <img
        :src="product.images?.[0]?.image || '/placeholder-card.jpg'"
        :alt="product.name"
        class="w-full h-48 object-cover"
      />
    </div>
    
    <div class="p-4">
      <div class="flex justify-between items-start mb-2">
        <h3 class="text-lg font-semibold text-gray-900 line-clamp-2">
          {{ product.name }}
        </h3>
        <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
          {{ product.tcg_type.toUpperCase() }}
        </span>
      </div>
      
      <p v-if="product.series" class="text-sm text-gray-600 mb-2">
        {{ product.series }}
      </p>
      
      <div class="flex justify-between items-center">
        <div>
          <span v-if="product.average_price" class="text-lg font-bold text-green-600">
            €{{ product.average_price }}
          </span>
          <span v-if="product.total_stock > 0" class="text-xs text-gray-500 ml-2">
            {{ product.total_stock }} available
          </span>
          <span v-else class="text-xs text-red-500 ml-2">
            Out of stock
          </span>
        </div>
        
        <NuxtLink
          :to="`/products/${product.id}`"
          class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
        >
          View Details
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  product: Product
}

defineProps<Props>()
</script>
```

```vue
<!-- components/products/SearchBar.vue -->
<template>
  <div class="relative">
    <div class="relative">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search for cards..."
        class="w-full px-4 py-3 pl-10 pr-4 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        @input="onSearchInput"
        @keydown.enter="performSearch"
      />
      
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
      </div>
      
      <button
        v-if="searchQuery"
        @click="clearSearch"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
      >
        <XMarkIcon class="h-5 w-5 text-gray-400 hover:text-gray-600" />
      </button>
    </div>
    
    <!-- Search Suggestions -->
    <div
      v-if="suggestions.length > 0 && showSuggestions"
      class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
    >
      <button
        v-for="suggestion in suggestions"
        :key="suggestion"
        @click="selectSuggestion(suggestion)"
        class="w-full px-4 py-2 text-left hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
      >
        {{ suggestion }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  modelValue?: string
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'search', query: string): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Search for cards...'
})

const emit = defineEmits<Emits>()

const productsStore = useProductsStore()

const searchQuery = ref(props.modelValue || '')
const suggestions = ref<string[]>([])
const showSuggestions = ref(false)
const searchTimeout = ref<NodeJS.Timeout>()

watch(searchQuery, (newValue) => {
  emit('update:modelValue', newValue)
})

const onSearchInput = () => {
  clearTimeout(searchTimeout.value)
  
  if (searchQuery.value.length >= 2) {
    searchTimeout.value = setTimeout(async () => {
      try {
        suggestions.value = await productsStore.getSearchSuggestions(searchQuery.value)
        showSuggestions.value = true
      } catch (error) {
        suggestions.value = []
      }
    }, 300)
  } else {
    suggestions.value = []
    showSuggestions.value = false
  }
}

const selectSuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  showSuggestions.value = false
  performSearch()
}

const performSearch = () => {
  showSuggestions.value = false
  emit('search', searchQuery.value)
}

const clearSearch = () => {
  searchQuery.value = ''
  suggestions.value = []
  showSuggestions.value = false
}

// Hide suggestions when clicking outside
onClickOutside(ref(null), () => {
  showSuggestions.value = false
})
</script>
```

### Cart Components

```vue
<!-- components/cart/CartItem.vue -->
<template>
  <div class="flex items-center space-x-4 py-4 border-b border-gray-200">
    <div class="flex-shrink-0">
      <img
        :src="item.listing.product.images?.[0]?.image || '/placeholder-card.jpg'"
        :alt="item.listing.product.name"
        class="h-16 w-16 object-cover rounded"
      />
    </div>
    
    <div class="flex-1 min-w-0">
      <h4 class="text-sm font-medium text-gray-900">
        {{ item.listing.product.name }}
      </h4>
      <p class="text-sm text-gray-500">
        {{ item.listing.variant.condition.label }} - {{ item.listing.variant.language.name }}
      </p>
      <p class="text-sm font-medium text-green-600">
        €{{ item.listing.price }}
      </p>
    </div>
    
    <div class="flex items-center space-x-2">
      <button
        @click="decreaseQuantity"
        :disabled="item.quantity <= 1 || isUpdating"
        class="p-1 rounded-full hover:bg-gray-100 disabled:opacity-50"
      >
        <MinusIcon class="h-4 w-4" />
      </button>
      
      <span class="w-8 text-center">{{ item.quantity }}</span>
      
      <button
        @click="increaseQuantity"
        :disabled="isUpdating"
        class="p-1 rounded-full hover:bg-gray-100 disabled:opacity-50"
      >
        <PlusIcon class="h-4 w-4" />
      </button>
    </div>
    
    <div class="text-right">
      <p class="text-sm font-medium text-gray-900">
        €{{ item.subtotal }}
      </p>
      <button
        @click="removeItem"
        :disabled="isUpdating"
        class="text-sm text-red-600 hover:text-red-500"
      >
        Remove
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MinusIcon, PlusIcon } from '@heroicons/vue/24/outline'

interface Props {
  item: CartItem
}

const props = defineProps<Props>()

const cartStore = useCartStore()
const isUpdating = ref(false)

const increaseQuantity = async () => {
  isUpdating.value = true
  try {
    await cartStore.updateCartItem(props.item.id, props.item.quantity + 1)
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message || 'Failed to update quantity')
  } finally {
    isUpdating.value = false
  }
}

const decreaseQuantity = async () => {
  if (props.item.quantity <= 1) return
  
  isUpdating.value = true
  try {
    await cartStore.updateCartItem(props.item.id, props.item.quantity - 1)
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message || 'Failed to update quantity')
  } finally {
    isUpdating.value = false
  }
}

const removeItem = async () => {
  isUpdating.value = true
  try {
    await cartStore.removeFromCart(props.item.id)
    const { $toast } = useNuxtApp()
    $toast.success('Item removed from cart')
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message || 'Failed to remove item')
  } finally {
    isUpdating.value = false
  }
}
</script>
```

## Pages

### Authentication Pages

```vue
<!-- pages/auth/login.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Sign in to your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Or
          <NuxtLink to="/auth/register" class="font-medium text-blue-600 hover:text-blue-500">
            create a new account
          </NuxtLink>
        </p>
      </div>
      
      <AuthLoginForm />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: 'guest'
})

useSeoMeta({
  title: 'Login - Fliiply',
  description: 'Sign in to your Fliiply account to access the TCG marketplace'
})
</script>
```

### Product Pages

```vue
<!-- pages/products/[id].vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="isLoading" class="flex justify-center items-center min-h-96">
      <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>
    
    <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Product Images -->
      <div>
        <div class="aspect-w-1 aspect-h-1 mb-4">
          <img
            :src="currentImage?.image || '/placeholder-card.jpg'"
            :alt="product.name"
            class="w-full h-96 object-cover rounded-lg"
          />
        </div>
        
        <div v-if="product.images.length > 1" class="grid grid-cols-4 gap-2">
          <button
            v-for="image in product.images"
            :key="image.id"
            @click="currentImage = image"
            class="aspect-w-1 aspect-h-1"
          >
            <img
              :src="image.image"
              :alt="image.alt_text"
              class="w-full h-20 object-cover rounded border-2"
              :class="currentImage?.id === image.id ? 'border-blue-500' : 'border-gray-200'"
            />
          </button>
        </div>
      </div>
      
      <!-- Product Details -->
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-4">
          {{ product.name }}
        </h1>
        
        <div class="flex items-center space-x-4 mb-4">
          <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
            {{ product.tcg_type.toUpperCase() }}
          </span>
          <span v-if="product.series" class="text-gray-600">
            {{ product.series }}
          </span>
        </div>
        
        <div v-if="product.description" class="prose prose-sm mb-6">
          <p>{{ product.description }}</p>
        </div>
        
        <!-- Listings -->
        <div class="border-t pt-6">
          <h3 class="text-lg font-semibold mb-4">Available Listings</h3>
          
          <div v-if="listings.length === 0" class="text-gray-500">
            No listings available for this product.
          </div>
          
          <div v-else class="space-y-3">
            <div
              v-for="listing in listings"
              :key="listing.id"
              class="border rounded-lg p-4 hover:bg-gray-50"
            >
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-medium">€{{ listing.price }}</p>
                  <p class="text-sm text-gray-600">
                    {{ listing.variant.condition.label }} - {{ listing.variant.language.name }}
                  </p>
                  <p class="text-sm text-gray-500">
                    Sold by {{ listing.seller.username }}
                  </p>
                  <p class="text-xs text-gray-400">
                    Stock: {{ listing.stock }}
                  </p>
                </div>
                
                <button
                  @click="addToCart(listing.id)"
                  :disabled="listing.stock === 0 || isAddingToCart"
                  class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span v-if="!isAddingToCart">Add to Cart</span>
                  <span v-else>Adding...</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center py-12">
      <h2 class="text-2xl font-bold text-gray-900">Product not found</h2>
      <p class="mt-2 text-gray-600">The product you're looking for doesn't exist.</p>
      <NuxtLink to="/products" class="mt-4 inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Browse Products
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const productsStore = useProductsStore()
const cartStore = useCartStore()

const productId = parseInt(route.params.id as string)

const product = ref<Product | null>(null)
const currentImage = ref<ProductImage | null>(null)
const listings = ref<Listing[]>([])
const isLoading = ref(true)
const isAddingToCart = ref(false)

// Fetch product data
onMounted(async () => {
  try {
    product.value = await productsStore.fetchProduct(productId)
    if (product.value) {
      currentImage.value = product.value.images.find(img => img.is_primary) || product.value.images[0]
      
      // Fetch listings for this product
      const api = useApi()
      const response = await api.get<PaginatedResponse<Listing>>('/listings/', {
        query: { product: productId },
        auth: false,
      })
      
      if (response.success && response.data) {
        listings.value = response.data.results.filter(listing => listing.status === 'active')
      }
    }
  } catch (error) {
    console.error('Failed to fetch product:', error)
  } finally {
    isLoading.value = false
  }
})

const addToCart = async (listingId: number) => {
  isAddingToCart.value = true
  
  try {
    await cartStore.addToCart(listingId, 1)
    const { $toast } = useNuxtApp()
    $toast.success('Added to cart!')
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message || 'Failed to add to cart')
  } finally {
    isAddingToCart.value = false
  }
}

// SEO
useSeoMeta({
  title: () => product.value ? `${product.value.name} - Fliiply` : 'Product - Fliiply',
  description: () => product.value?.description || 'View product details on Fliiply TCG marketplace'
})
</script>
```

### Search Page

```vue
<!-- pages/search.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Search Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">Search Products</h1>
      
      <ProductsSearchBar
        v-model="searchQuery"
        @search="performSearch"
        class="mb-6"
      />
      
      <!-- Search Filters -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold mb-4">Filters</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- TCG Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              TCG Type
            </label>
            <select
              v-model="filters.tcg_type"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md"
              @change="applyFilters"
            >
              <option value="">All Types</option>
              <option value="pokemon">Pokemon</option>
              <option value="yugioh">Yu-Gi-Oh</option>
              <option value="magic">Magic: The Gathering</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <!-- Price Range -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Min Price (€)
            </label>
            <input
              v-model.number="filters.min_price"
              type="number"
              min="0"
              step="0.01"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md"
              @input="applyFilters"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Max Price (€)
            </label>
            <input
              v-model.number="filters.max_price"
              type="number"
              min="0"
              step="0.01"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md"
              @input="applyFilters"
            />
          </div>
          
          <!-- Availability -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Availability
            </label>
            <select
              v-model="filters.availability"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md"
              @change="applyFilters"
            >
              <option value="">All</option>
              <option value="in_stock">In Stock</option>
              <option value="out_of_stock">Out of Stock</option>
            </select>
          </div>
        </div>
        
        <div class="mt-4 flex space-x-4">
          <button
            @click="clearFilters"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>
    
    <!-- Search Results -->
    <div v-if="isLoading" class="flex justify-center items-center min-h-96">
      <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>
    
    <div v-else-if="searchResults.length === 0 && hasSearched" class="text-center py-12">
      <h3 class="text-xl font-semibold text-gray-900">No results found</h3>
      <p class="mt-2 text-gray-600">Try adjusting your search criteria.</p>
    </div>
    
    <div v-else-if="searchResults.length > 0">
      <div class="flex justify-between items-center mb-6">
        <p class="text-gray-600">
          {{ pagination.count }} results found
        </p>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <ProductsProductCard
          v-for="product in searchResults"
          :key="product.id"
          :product="product"
        />
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.totalPages > 1" class="mt-8 flex justify-center">
        <nav class="flex space-x-2">
          <button
            v-for="page in paginationPages"
            :key="page"
            @click="goToPage(page)"
            class="px-3 py-2 text-sm rounded"
            :class="page === pagination.currentPage
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'"
          >
            {{ page }}
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()

const searchQuery = ref('')
const filters = reactive<SearchFilters>({
  tcg_type: '',
  min_price: undefined,
  max_price: undefined,
  availability: '',
})

const searchResults = computed(() => productsStore.searchResults)
const pagination = computed(() => productsStore.pagination)
const isLoading = computed(() => productsStore.isLoading)
const hasSearched = ref(false)

const searchTimeout = ref<NodeJS.Timeout>()

// Initialize from URL query parameters
onMounted(() => {
  const query = route.query
  searchQuery.value = (query.q as string) || ''
  
  if (query.tcg_type) filters.tcg_type = query.tcg_type as string
  if (query.min_price) filters.min_price = parseFloat(query.min_price as string)
  if (query.max_price) filters.max_price = parseFloat(query.max_price as string)
  if (query.availability) filters.availability = query.availability as string
  
  if (searchQuery.value) {
    performSearch()
  }
})

const performSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  hasSearched.value = true
  
  const searchFilters: SearchFilters = {
    q: searchQuery.value,
    ...filters,
    page: 1,
  }
  
  // Clean undefined values
  Object.keys(searchFilters).forEach(key => {
    if (searchFilters[key as keyof SearchFilters] === undefined || searchFilters[key as keyof SearchFilters] === '') {
      delete searchFilters[key as keyof SearchFilters]
    }
  })
  
  try {
    await productsStore.searchProducts(searchFilters)
    
    // Update URL with search parameters
    await router.push({
      path: '/search',
      query: searchFilters,
    })
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error(error.message || 'Search failed')
  }
}

const applyFilters = () => {
  clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    if (searchQuery.value) {
      performSearch()
    }
  }, 500)
}

const clearFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key as keyof typeof filters] = key.includes('price') ? undefined : ''
  })
  performSearch()
}

const goToPage = (page: number) => {
  const searchFilters: SearchFilters = {
    q: searchQuery.value,
    ...filters,
    page,
  }
  
  productsStore.searchProducts(searchFilters)
}

const paginationPages = computed(() => {
  const pages = []
  const totalPages = pagination.value.totalPages
  const currentPage = pagination.value.currentPage
  
  // Show up to 5 pages around current page
  const start = Math.max(1, currentPage - 2)
  const end = Math.min(totalPages, currentPage + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// SEO
useSeoMeta({
  title: () => searchQuery.value ? `Search: ${searchQuery.value} - Fliiply` : 'Search - Fliiply',
  description: 'Search for trading cards and TCG products on Fliiply marketplace'
})
</script>
```

## Middleware

### Authentication Middleware

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()
  
  if (!isAuthenticated.value) {
    return navigateTo('/auth/login')
  }
})
```

```typescript
// middleware/guest.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()
  
  if (isAuthenticated.value) {
    return navigateTo('/')
  }
})
```

## Plugins

### Toast Plugin

```typescript
// plugins/toast.client.ts
import Toast, { PluginOptions, POSITION } from 'vue-toastification'
import 'vue-toastification/dist/index.css'

export default defineNuxtPlugin((nuxtApp) => {
  const options: PluginOptions = {
    position: POSITION.TOP_RIGHT,
    timeout: 5000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: 'button',
    icon: true,
    rtl: false,
  }
  
  nuxtApp.vueApp.use(Toast, options)
})
```

### Auth Plugin

```typescript
// plugins/auth.client.ts
export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  
  // Initialize authentication on app start
  await authStore.initializeAuth()
})
```

## Layouts

### Default Layout

```vue
<!-- layouts/default.vue -->
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center space-x-2">
            <img src="/logo.svg" alt="Fliiply" class="h-8 w-8" />
            <span class="text-xl font-bold text-gray-900">Fliiply</span>
          </NuxtLink>
          
          <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-8">
            <NuxtLink to="/products" class="text-gray-700 hover:text-gray-900">
              Products
            </NuxtLink>
            <NuxtLink to="/search" class="text-gray-700 hover:text-gray-900">
              Search
            </NuxtLink>
            <NuxtLink to="/collections" class="text-gray-700 hover:text-gray-900">
              Collections
            </NuxtLink>
          </div>
          
          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <!-- Cart -->
            <NuxtLink to="/cart" class="relative p-2 text-gray-600 hover:text-gray-900">
              <ShoppingCartIcon class="h-6 w-6" />
              <span
                v-if="cartItemCount > 0"
                class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center"
              >
                {{ cartItemCount }}
              </span>
            </NuxtLink>
            
            <!-- User Menu -->
            <div v-if="isAuthenticated" class="relative">
              <Menu as="div" class="relative inline-block text-left">
                <MenuButton class="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
                  <UserCircleIcon class="h-8 w-8" />
                  <span>{{ user?.username }}</span>
                  <ChevronDownIcon class="h-4 w-4" />
                </MenuButton>
                
                <MenuItems class="absolute right-0 z-10 mt-2 w-56 origin-top-right bg-white border border-gray-200 rounded-md shadow-lg">
                  <div class="py-1">
                    <MenuItem v-slot="{ active }">
                      <NuxtLink
                        to="/profile"
                        :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                      >
                        Profile
                      </NuxtLink>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <NuxtLink
                        to="/orders"
                        :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                      >
                        Orders
                      </NuxtLink>
                    </MenuItem>
                    <MenuItem v-if="user?.is_seller" v-slot="{ active }">
                      <NuxtLink
                        to="/seller"
                        :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                      >
                        Seller Dashboard
                      </NuxtLink>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="handleLogout"
                        :class="[active ? 'bg-gray-100' : '', 'block w-full text-left px-4 py-2 text-sm text-gray-700']"
                      >
                        Logout
                      </button>
                    </MenuItem>
                  </div>
                </MenuItems>
              </Menu>
            </div>
            
            <div v-else class="flex items-center space-x-4">
              <NuxtLink
                to="/auth/login"
                class="text-gray-700 hover:text-gray-900"
              >
                Login
              </NuxtLink>
              <NuxtLink
                to="/auth/register"
                class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Sign Up
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main>
      <slot />
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-800 text-white mt-16">
      <div class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 class="text-lg font-semibold mb-4">Fliiply</h3>
            <p class="text-gray-300">
              The premier marketplace for trading card games and collectibles.
            </p>
          </div>
          
          <div>
            <h4 class="font-semibold mb-4">Products</h4>
            <ul class="space-y-2 text-gray-300">
              <li><NuxtLink to="/products?tcg_type=pokemon" class="hover:text-white">Pokemon</NuxtLink></li>
              <li><NuxtLink to="/products?tcg_type=yugioh" class="hover:text-white">Yu-Gi-Oh</NuxtLink></li>
              <li><NuxtLink to="/products?tcg_type=magic" class="hover:text-white">Magic: The Gathering</NuxtLink></li>
            </ul>
          </div>
          
          <div>
            <h4 class="font-semibold mb-4">Support</h4>
            <ul class="space-y-2 text-gray-300">
              <li><NuxtLink to="/help" class="hover:text-white">Help Center</NuxtLink></li>
              <li><NuxtLink to="/contact" class="hover:text-white">Contact Us</NuxtLink></li>
              <li><NuxtLink to="/disputes" class="hover:text-white">Disputes</NuxtLink></li>
            </ul>
          </div>
          
          <div>
            <h4 class="font-semibold mb-4">Legal</h4>
            <ul class="space-y-2 text-gray-300">
              <li><NuxtLink to="/terms" class="hover:text-white">Terms of Service</NuxtLink></li>
              <li><NuxtLink to="/privacy" class="hover:text-white">Privacy Policy</NuxtLink></li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-gray-700 mt-8 pt-8 text-center text-gray-300">
          <p>&copy; 2025 Fliiply. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import {
  UserCircleIcon,
  ShoppingCartIcon,
  ChevronDownIcon,
} from '@heroicons/vue/24/outline'

const { isAuthenticated, user, logout } = useAuth()
const cartStore = useCartStore()

const cartItemCount = computed(() => cartStore.itemCount)

// Fetch cart items on mount if authenticated
onMounted(async () => {
  if (isAuthenticated.value) {
    try {
      await cartStore.fetchCartItems()
    } catch (error) {
      // Handle error silently for cart
    }
  }
})

const handleLogout = async () => {
  try {
    await logout()
    const { $toast } = useNuxtApp()
    $toast.success('Logged out successfully')
  } catch (error: any) {
    const { $toast } = useNuxtApp()
    $toast.error('Logout failed')
  }
}
</script>
```

This comprehensive Nuxt 3 integration guide provides:

1. **Complete project setup** with proper dependencies and configuration
2. **Type-safe API client** with automatic JWT token management
3. **Pinia stores** for state management (auth, products, cart, orders)
4. **Vue 3 Composition API** components with proper TypeScript interfaces
5. **Authentication system** with middleware and route protection
6. **Search functionality** with filters and pagination
7. **Cart management** with real-time updates
8. **Responsive design** using Tailwind CSS
9. **SEO optimization** with proper meta tags
10. **Error handling** with toast notifications

The code is production-ready and follows Nuxt 3 best practices for building a modern, scalable frontend application.