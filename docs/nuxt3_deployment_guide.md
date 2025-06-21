# Nuxt 3 Deployment Guide - Fliiply Frontend

## Environment Setup

### Environment Variables

```bash
# .env.production
NUXT_PUBLIC_API_BASE_URL=https://api.fliiply.com
NUXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key
NUXT_PUBLIC_APP_URL=https://app.fliiply.com
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key

# .env.staging
NUXT_PUBLIC_API_BASE_URL=https://staging-api.fliiply.com
NUXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
NUXT_PUBLIC_APP_URL=https://staging-app.fliiply.com
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key

# .env.development
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
NUXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
NUXT_PUBLIC_APP_URL=http://localhost:3000
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
```

### Production Nuxt Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // Enable SSR for better SEO
  ssr: true,
  
  // Nitro configuration for production
  nitro: {
    preset: 'node-server', // or 'vercel', 'netlify', etc.
    compressPublicAssets: true,
    minify: true,
  },
  
  // Build optimization
  build: {
    transpile: ['@stripe/stripe-js'],
  },
  
  // Runtime config
  runtimeConfig: {
    stripeSecretKey: process.env.STRIPE_SECRET_KEY,
    
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL,
      apiVersion: '/api/v1',
      stripePublicKey: process.env.NUXT_PUBLIC_STRIPE_PUBLIC_KEY,
      appUrl: process.env.NUXT_PUBLIC_APP_URL,
    }
  },
  
  // SEO and Performance
  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      title: 'Fliiply - TCG Marketplace',
      meta: [
        { name: 'description', content: 'The premier marketplace for trading card games and collectibles' },
        { name: 'keywords', content: 'trading cards, pokemon, yugioh, magic the gathering, tcg, marketplace' },
        { property: 'og:title', content: 'Fliiply - TCG Marketplace' },
        { property: 'og:description', content: 'Buy, sell, and collect trading cards on the premier TCG marketplace' },
        { property: 'og:type', content: 'website' },
        { property: 'og:url', content: 'https://app.fliiply.com' },
        { property: 'og:image', content: 'https://app.fliiply.com/og-image.jpg' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: 'Fliiply - TCG Marketplace' },
        { name: 'twitter:description', content: 'Buy, sell, and collect trading cards' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'canonical', href: 'https://app.fliiply.com' },
      ]
    }
  },
  
  // CSS optimization
  css: [
    '~/assets/css/main.css'
  ],
  
  // Performance optimizations
  experimental: {
    payloadExtraction: false, // Disable payload extraction for better performance
  },
  
  // Security headers
  routeRules: {
    '/**': {
      headers: {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
      }
    },
    // Cache static assets
    '/images/**': { headers: { 'Cache-Control': 's-maxage=31536000' } },
    '/icons/**': { headers: { 'Cache-Control': 's-maxage=31536000' } },
    '/fonts/**': { headers: { 'Cache-Control': 's-maxage=31536000' } },
  },
  
  // Modules
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/google-fonts',
    '@nuxt/image',
    '@nuxtjs/sitemap',
    '@nuxtjs/robots',
  ],
  
  // Image optimization
  image: {
    provider: 'ipx',
    quality: 80,
    format: ['webp'],
    screens: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      xxl: 1536,
    },
  },
  
  // Sitemap configuration
  sitemap: {
    hostname: 'https://app.fliiply.com',
    gzip: true,
    routes: [
      '/products',
      '/search',
      '/collections',
      '/auth/login',
      '/auth/register',
    ]
  },
  
  // Robots.txt
  robots: {
    UserAgent: '*',
    Allow: '/',
    Disallow: ['/admin', '/api', '/checkout'],
    Sitemap: 'https://app.fliiply.com/sitemap.xml'
  },
})
```

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Set environment to production
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["npm", "run", "start"]
```

### Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NUXT_PUBLIC_API_BASE_URL=https://api.fliiply.com
      - NUXT_PUBLIC_STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
      - NUXT_PUBLIC_APP_URL=https://app.fliiply.com
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`app.fliiply.com`)"
      - "traefik.http.routers.frontend.tls=true"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
    networks:
      - web

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
    restart: unless-stopped
    networks:
      - web

networks:
  web:
    external: true
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.fliiply.com https://api.stripe.com;" always;
    
    server {
        listen 80;
        server_name app.fliiply.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name app.fliiply.com;
        
        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Security
        client_max_body_size 10M;
        
        # Rate limiting
        limit_req zone=general burst=20 nodelay;
        
        # Static assets caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header X-Content-Type-Options nosniff;
        }
        
        # Auth endpoints rate limiting
        location ~ ^/(auth|api)/ {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Main application
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## Cloud Deployment Options

### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add NUXT_PUBLIC_API_BASE_URL production
vercel env add NUXT_PUBLIC_STRIPE_PUBLIC_KEY production
vercel env add STRIPE_SECRET_KEY production
```

### Vercel Configuration

```json
{
  "version": 2,
  "builds": [
    {
      "src": "nuxt.config.ts",
      "use": "@nuxtjs/vercel-builder"
    }
  ],
  "routes": [
    {
      "src": "/sw.js",
      "headers": {
        "cache-control": "public, max-age=0, must-revalidate",
        "service-worker-allowed": "/"
      }
    }
  ],
  "env": {
    "NUXT_PUBLIC_API_BASE_URL": "@nuxt_public_api_base_url",
    "NUXT_PUBLIC_STRIPE_PUBLIC_KEY": "@nuxt_public_stripe_public_key",
    "STRIPE_SECRET_KEY": "@stripe_secret_key"
  },
  "functions": {
    "pages/api/**": {
      "maxDuration": 30
    }
  }
}
```

### Netlify Deployment

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = ".output/public"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/server"
  status = 200

[functions]
  node_bundler = "esbuild"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### AWS ECS Deployment

```yaml
# aws-task-definition.json
{
  "family": "fliiply-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/fliiply-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "NUXT_PUBLIC_API_BASE_URL",
          "value": "https://api.fliiply.com"
        }
      ],
      "secrets": [
        {
          "name": "NUXT_PUBLIC_STRIPE_PUBLIC_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:stripe-public-key"
        },
        {
          "name": "STRIPE_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:stripe-secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fliiply-frontend",
          "awslogs-region": "REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/api/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/frontend

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linting
        run: npm run lint
      
      - name: Run type checking
        run: npm run typecheck
      
      - name: Run tests
        run: npm run test
      
      - name: Build application
        run: npm run build
        env:
          NUXT_PUBLIC_API_BASE_URL: ${{ secrets.API_BASE_URL }}
          NUXT_PUBLIC_STRIPE_PUBLIC_KEY: ${{ secrets.STRIPE_PUBLIC_KEY }}

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /opt/fliiply
            docker-compose pull frontend
            docker-compose up -d frontend
            docker system prune -f
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  NODE_VERSION: "18"
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

cache:
  paths:
    - node_modules/

test:
  stage: test
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run lint
    - npm run typecheck
    - npm run test
    - npm run build
  artifacts:
    reports:
      junit: junit.xml
    paths:
      - coverage/
    expire_in: 1 day

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main

deploy:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan $DEPLOY_HOST >> ~/.ssh/known_hosts
    - chmod 644 ~/.ssh/known_hosts
  script:
    - ssh $DEPLOY_USER@$DEPLOY_HOST "cd /opt/fliiply && docker-compose pull frontend && docker-compose up -d frontend"
  only:
    - main
  when: manual
```

## Performance Optimization

### Build Optimization

```typescript
// nuxt.config.ts - Performance optimizations
export default defineNuxtConfig({
  // Build optimizations
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router'],
            pinia: ['pinia', '@pinia/nuxt'],
            ui: ['@headlessui/vue', '@heroicons/vue'],
            utils: ['@vueuse/core', '@vueuse/nuxt'],
          }
        }
      }
    }
  },
  
  // Nitro optimizations
  nitro: {
    compressPublicAssets: true,
    minify: true,
    storage: {
      redis: {
        driver: 'redis',
        // Redis connection for caching
        host: process.env.REDIS_HOST,
        port: process.env.REDIS_PORT,
        password: process.env.REDIS_PASSWORD,
      }
    }
  },
  
  // PWA configuration
  pwa: {
    registerType: 'autoUpdate',
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
    },
    client: {
      installPrompt: true,
      periodicSyncForUpdates: 20,
    },
    devOptions: {
      enabled: true,
      type: 'module',
    },
  },
})
```

### Caching Strategy

```typescript
// server/api/cache.ts
export default defineEventHandler(async (event) => {
  const key = `cache:${getRouterParam(event, 'key')}`
  
  // Try to get from cache first
  const cached = await useStorage('redis').getItem(key)
  if (cached) {
    return cached
  }
  
  // Fetch fresh data
  const data = await fetchDataFromAPI()
  
  // Cache for 5 minutes
  await useStorage('redis').setItem(key, data, { ttl: 300 })
  
  return data
})
```

## Monitoring and Analytics

### Health Check Endpoint

```typescript
// server/api/health.ts
export default defineEventHandler(async (event) => {
  try {
    // Check API connectivity
    const apiHealth = await $fetch(`${useRuntimeConfig().public.apiBaseUrl}/health/`)
    
    // Check Redis (if using)
    const redisStatus = await useStorage('redis').hasItem('health-check')
    
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        api: apiHealth ? 'healthy' : 'unhealthy',
        cache: redisStatus !== null ? 'healthy' : 'warning',
      },
      version: process.env.npm_package_version || 'unknown',
    }
  } catch (error) {
    setResponseStatus(event, 503)
    return {
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message,
    }
  }
})
```

### Analytics Integration

```typescript
// plugins/analytics.client.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  
  // Google Analytics
  if (config.public.gaId) {
    useHead({
      script: [
        {
          async: true,
          src: `https://www.googletagmanager.com/gtag/js?id=${config.public.gaId}`,
        },
        {
          innerHTML: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${config.public.gaId}');
          `,
        },
      ],
    })
  }
  
  // Custom analytics
  const router = useRouter()
  router.afterEach((to) => {
    // Track page views
    if (typeof gtag !== 'undefined') {
      gtag('config', config.public.gaId, {
        page_path: to.fullPath,
      })
    }
  })
})
```

## Security Best Practices

### Content Security Policy

```typescript
// nuxt.config.ts - CSP configuration
export default defineNuxtConfig({
  routeRules: {
    '/**': {
      headers: {
        'Content-Security-Policy': [
          "default-src 'self'",
          "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://www.googletagmanager.com",
          "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
          "font-src 'self' https://fonts.gstatic.com",
          "img-src 'self' data: https: blob:",
          "connect-src 'self' https://api.fliiply.com https://api.stripe.com https://www.google-analytics.com",
          "frame-src 'self' https://js.stripe.com",
          "object-src 'none'",
          "base-uri 'self'",
          "form-action 'self'",
          "frame-ancestors 'none'",
        ].join('; '),
      }
    }
  }
})
```

### Environment Validation

```typescript
// server/plugins/validate-env.ts
export default defineNitroPlugin(async (nitroApp) => {
  const config = useRuntimeConfig()
  
  const requiredEnvVars = [
    'NUXT_PUBLIC_API_BASE_URL',
    'NUXT_PUBLIC_STRIPE_PUBLIC_KEY',
    'STRIPE_SECRET_KEY',
  ]
  
  const missing = requiredEnvVars.filter(
    key => !config[key] && !config.public[key.replace('NUXT_PUBLIC_', '')]
  )
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`)
  }
})
```

This deployment guide provides comprehensive instructions for deploying a production-ready Nuxt 3 application with proper security, performance optimization, and monitoring capabilities.