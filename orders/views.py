from rest_framework import viewsets
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order, CartItem, OrderItem
from accounts.services import create_payment_intent
from django.conf import settings
from .serializers import OrderSerializer, CartItemSerializer
from accounts.permissions import IsBuyer, IsSeller
from accounts.models import Address
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        user = self.request.user
        now = timezone.now()
        # Clean expired reservations
        CartItem.objects.filter(reserved_until__lt=now).delete()
        return CartItem.objects.filter(buyer=user)

    def perform_create(self, serializer):
        listing_id = self.request.data.get('listing')
        quantity = int(self.request.data.get('quantity', 1))
        from products.models import Listing
        try:
            listing = Listing.objects.get(id=listing_id, status='active')
        except Listing.DoesNotExist:
            raise serializers.ValidationError('Invalid listing')
        now = timezone.now()
        if CartItem.objects.filter(listing=listing, reserved_until__gt=now).exclude(buyer=self.request.user).exists():
            raise serializers.ValidationError('Listing is reserved')
        reserved_until = now + timedelta(minutes=getattr(settings, 'CART_RESERVATION_MINUTES', 30))
        serializer.save(buyer=self.request.user, listing=listing, quantity=quantity, reserved_until=reserved_until)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsSeller]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Vérifier si nous sommes en mode génération de schéma Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        # Vérifier si l'utilisateur est authentifié
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()

        if user.is_buyer:
            return Order.objects.filter(buyer=user)
        elif user.is_seller:
            return Order.objects.filter(items__listing__seller=user).distinct()
        return Order.objects.none()

    @swagger_auto_schema(
        operation_description="List all orders (buyers see their own orders, sellers see orders they sold).",
        responses={
            200: openapi.Response(
                description="List of orders",
                schema=OrderSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "buyer": {
                                "id": 2,
                                "username": "buyer1",
                                "email": "buyer1@example.com",
                                "is_buyer": True,
                                "is_seller": False,
                                "is_verifier": False
                            },
                            "seller": {
                                "id": 1,
                                "username": "papa",
                                "email": "papa@example.com",
                                "is_buyer": True,
                                "is_seller": True,
                                "is_verifier": False
                            },
                            "listing": {
                                "id": 1,
                                "user": {
                                    "id": 1,
                                    "username": "papa",
                                    "email": "papa@example.com",
                                    "is_buyer": True,
                                    "is_seller": True,
                                    "is_verifier": False
                                },
                                "product": {
                                    "id": 1,
                                    "set": "Écarlate et Violet ParadoXe RiFT Lune Néo",
                                    "name": "Boîte de dressage d’élite du Centre Pokémon",
                                    "image": "https://example.com/boite.jpg",
                                    "description": "Prix du set : 60B SUG\nContenu : ParadoXe RiFT Moon Pokémon Center",
                                    "average_price": "90.00",
                                    "total_stock": 3,
                                    "category": {
                                        "id": 1,
                                        "name": "Pokémon",
                                        "slug": "pokemon",
                                        "description": None
                                    },
                                    "created_at": "2025-04-22T13:00:00Z",
                                    "updated_at": "2025-04-22T13:00:00Z",
                                    "price_histories": [],
                                    "similar_products": []
                                },
                                "status": "active",
                                "price": "90.00",
                                "quantity": 2,
                                "condition": "mint",
                                "stock": 3,
                                "buyer_processing_fee": "10.80",
                                "buyer_shipping_fee": "10.00",
                                "buyer_total_price": "200.80",
                                "seller_transaction_fee": "16.20",
                                "seller_processing_fee": "5.40",
                                "seller_shipping_fee": "10.00",
                                "seller_net_amount": "148.40",
                                "status": "accepted",
                                "created_at": "2025-04-22T13:07:00Z",
                                "updated_at": "2025-04-22T13:07:00Z"
                            },
                            "quantity": 2,
                            "base_price": "180.00",
                            "buyer_address": {
                                "id": 1,
                                "street": "123 Buyer St",
                                "city": "Buyer City",
                                "state": "Buyer State",
                                "postal_code": "12345",
                                "country": "Buyer Country",
                                "created_at": "2025-04-22T13:00:00Z",
                                "updated_at": "2025-04-22T13:00:00Z"
                            },
                            "seller_address": {
                                "id": 2,
                                "street": "456 Seller St",
                                "city": "Seller City",
                                "state": "Seller State",
                                "postal_code": "67890",
                                "country": "Seller Country",
                                "created_at": "2025-04-22T13:00:00Z",
                                "updated_at": "2025-04-22T13:00:00Z"
                            },
                            "buyer_processing_fee": "10.80",
                            "buyer_shipping_fee": "10.00",
                            "buyer_total_price": "200.80",
                            "seller_transaction_fee": "16.20",
                            "seller_processing_fee": "5.40",
                            "seller_shipping_fee": "10.00",
                            "seller_net_amount": "148.40",
                            "status": "pending",
                            "created_at": "2025-04-22T13:10:00Z",
                            "updated_at": "2025-04-22T13:10:00Z"
                        }
                    ]
                }
            ),
            401: "Unauthorized"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new order (buyers only).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['cart_items', 'buyer_address'],
            properties={
                'cart_items': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='IDs of the cart items to order'
                ),
                'buyer_address': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the buyer’s address for shipping')
            }
        ),
        responses={
            201: openapi.Response(
                description="Order created",
                schema=OrderSerializer(),
                examples={
                    "application/json": {
                        "id": 1,
                        "buyer": {
                            "id": 2,
                            "username": "buyer1",
                            "email": "buyer1@example.com",
                            "is_buyer": True,
                            "is_seller": False,
                            "is_verifier": False
                        },
                        "seller": {
                            "id": 1,
                            "username": "papa",
                            "email": "papa@example.com",
                            "is_buyer": True,
                            "is_seller": True,
                            "is_verifier": False
                        },
                        "listing": {
                            "id": 1,
                            "user": {
                                "id": 1,
                                "username": "papa",
                                "email": "papa@example.com",
                                "is_buyer": True,
                                "is_seller": True,
                                "is_verifier": False
                            },
                            "product": {
                                "id": 1,
                                "set": "Écarlate et Violet ParadoXe RiFT Lune Néo",
                                "name": "Boîte de dressage d’élite du Centre Pokémon",
                                "image": "https://example.com/boite.jpg",
                                "description": "Prix du set : 60B SUG\nContenu : ParadoXe RiFT Moon Pokémon Center",
                                "average_price": "90.00",
                                "total_stock": 3,
                                "category": {
                                    "id": 1,
                                    "name": "Pokémon",
                                    "slug": "pokemon",
                                    "description": None
                                },
                                "created_at": "2025-04-22T13:00:00Z",
                                "updated_at": "2025-04-22T13:00:00Z",
                                "price_histories": [],
                                "similar_products": []
                            },
                            "status": "active",
                            "price": "90.00",
                            "quantity": 2,
                            "condition": "mint",
                            "stock": 3,
                            "buyer_processing_fee": "10.80",
                            "buyer_shipping_fee": "10.00",
                            "buyer_total_price": "200.80",
                            "seller_transaction_fee": "16.20",
                            "seller_processing_fee": "5.40",
                            "seller_shipping_fee": "10.00",
                            "seller_net_amount": "148.40",
                            "status": "accepted",
                            "created_at": "2025-04-22T13:07:00Z",
                            "updated_at": "2025-04-22T13:07:00Z"
                        },
                        "quantity": 2,
                        "base_price": "180.00",
                        "buyer_address": {
                            "id": 1,
                            "street": "123 Buyer St",
                            "city": "Buyer City",
                            "state": "Buyer State",
                            "postal_code": "12345",
                            "country": "Buyer Country",
                            "created_at": "2025-04-22T13:00:00Z",
                            "updated_at": "2025-04-22T13:00:00Z"
                        },
                        "seller_address": {
                            "id": 2,
                            "street": "456 Seller St",
                            "city": "Seller City",
                            "state": "Seller State",
                            "postal_code": "67890",
                            "country": "Seller Country",
                            "created_at": "2025-04-22T13:00:00Z",
                            "updated_at": "2025-04-22T13:00:00Z"
                        },
                        "buyer_processing_fee": "10.80",
                        "buyer_shipping_fee": "10.00",
                        "buyer_total_price": "200.80",
                        "seller_transaction_fee": "16.20",
                        "seller_processing_fee": "5.40",
                        "seller_shipping_fee": "10.00",
                        "seller_net_amount": "148.40",
                        "status": "pending",
                        "created_at": "2025-04-22T13:10:00Z",
                        "updated_at": "2025-04-22T13:10:00Z"
                    }
                }
            ),
            403: "Forbidden",
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve an order by ID (buyers and sellers only).",
        responses={
            200: OrderSerializer,
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        cart_item_ids = self.request.data.get('cart_items', [])
        if isinstance(cart_item_ids, str):
            cart_item_ids = [i for i in cart_item_ids.split(',') if i]
        buyer_address_id = self.request.data.get('buyer_address')

        if not cart_item_ids:
            raise serializers.ValidationError('No cart items provided.')

        cart_items = list(CartItem.objects.filter(id__in=cart_item_ids, buyer=self.request.user))
        if len(cart_items) != len(cart_item_ids):
            raise serializers.ValidationError('Invalid cart items.')

        buyer = self.request.user
        if not buyer.is_buyer:
            raise serializers.ValidationError('Only buyers can create orders.')

        try:
            buyer_address = Address.objects.get(id=buyer_address_id, user=buyer)
        except Address.DoesNotExist:
            raise serializers.ValidationError('Invalid buyer address.')

        base_price = sum(item.listing.price * item.quantity for item in cart_items)
        buyer_processing_fee = max(base_price * Decimal('0.06'), Decimal('5.00'))
        buyer_shipping_fee = Decimal('10.00')
        platform_commission = base_price * Decimal(str(getattr(settings, 'PLATFORM_COMMISSION_PERCENT', 0.05)))
        buyer_total_price = base_price + buyer_processing_fee + buyer_shipping_fee + platform_commission

        payment_intent = create_payment_intent(buyer, buyer_total_price)

        order = serializer.save(
            buyer=buyer,
            base_price=base_price,
            buyer_address=buyer_address,
            buyer_processing_fee=buyer_processing_fee,
            buyer_shipping_fee=buyer_shipping_fee,
            buyer_total_price=buyer_total_price,
            platform_commission=platform_commission,
            stripe_payment_intent_id=payment_intent.id,
        )

        for cart_item in cart_items:
            listing = cart_item.listing
            if listing.status != 'active' or listing.stock < cart_item.quantity:
                raise serializers.ValidationError('Listing unavailable.')
            listing.stock -= cart_item.quantity
            listing.save()
            OrderItem.objects.create(order=order, listing=listing, quantity=cart_item.quantity)
            cart_item.delete()

    def perform_update(self, serializer):
        order = self.get_object()
        if not (
            self.request.user == order.buyer or
            order.items.filter(listing__seller=self.request.user).exists()
        ):
            raise serializers.ValidationError("You cannot update this order.")
        serializer.save()
