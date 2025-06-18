from rest_framework import viewsets
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order, Offer, CartItem
from accounts.services import create_payment_intent
from django.conf import settings
from .serializers import OrderSerializer, OfferSerializer, CartItemSerializer
from accounts.permissions import IsBuyer, IsSeller
from accounts.models import Address
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

User = get_user_model()

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

    def get_permissions(self):
        if self.action in ['create']:
            if self.request.data.get('offer_type') == Offer.OFFER_TYPE_BUY:
                permission_classes = [IsAuthenticated, IsBuyer]
            else:
                permission_classes = [IsAuthenticated, IsSeller]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Vérifier si nous sommes en mode génération de schéma Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Offer.objects.none()

        # Vérifier si l'utilisateur est authentifié
        user = self.request.user
        if not user.is_authenticated:
            return Offer.objects.none()

        now = timezone.now()
        base_qs = Offer.objects.filter(
            Q(cart_items__isnull=True) |
            Q(cart_items__buyer=user) |
            Q(cart_items__reserved_until__lte=now)
        )
        if user.is_buyer:
            return base_qs.filter(offer_type=Offer.OFFER_TYPE_SELL, status='pending').distinct()
        elif user.is_seller:
            return base_qs.filter(offer_type=Offer.OFFER_TYPE_BUY, status='pending').distinct()
        return Offer.objects.none()

    @swagger_auto_schema(
        operation_description="List all offers (buyers see sell offers, sellers see buy offers).",
        responses={200: OfferSerializer(many=True), 401: "Unauthorized"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new offer (buyers create buy offers, sellers create sell offers).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product', 'offer_type', 'price', 'quantity'],
            properties={
                'product': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the product'),
                'offer_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of offer (buy or sell)'),
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Proposed price'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of items', default=1),
                'condition': openapi.Schema(type=openapi.TYPE_STRING, description='Condition of the item (for sell offers)', enum=['mint', 'near_mint', 'excellent', 'good', 'played', 'poor']),
                'stock': openapi.Schema(type=openapi.TYPE_INTEGER, description='Available stock (for sell offers)')
            }
        ),
        responses={201: OfferSerializer, 403: "Forbidden", 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve an offer by ID (buyers and sellers only).",
        responses={200: OfferSerializer, 401: "Unauthorized", 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        offer = self.get_object()
        if offer.user != self.request.user:
            raise serializers.ValidationError("Only the creator of the offer can update it.")
        serializer.save()


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
        offer_id = self.request.data.get('offer')
        quantity = int(self.request.data.get('quantity', 1))
        try:
            offer = Offer.objects.get(id=offer_id, status='pending')
        except Offer.DoesNotExist:
            raise serializers.ValidationError('Invalid offer')
        now = timezone.now()
        if CartItem.objects.filter(offer=offer, reserved_until__gt=now).exclude(buyer=self.request.user).exists():
            raise serializers.ValidationError('Offer is reserved')
        reserved_until = now + timedelta(minutes=getattr(settings, 'CART_RESERVATION_MINUTES', 30))
        serializer.save(buyer=self.request.user, offer=offer, quantity=quantity, reserved_until=reserved_until)


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
            return Order.objects.filter(seller=user)
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
                            "offer": {
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
                                "offer_type": "sell",
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
            required=['offer', 'quantity', 'buyer_address'],
            properties={
                'offer': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the offer to accept'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of items to order', default=1),
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
                        "offer": {
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
                            "offer_type": "sell",
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
        offer_id = self.request.data.get('offer')
        quantity = int(self.request.data.get('quantity', 1))
        buyer_address_id = self.request.data.get('buyer_address')

        # Récupérer l'offre
        offer = Offer.objects.get(id=offer_id)

        # Vérifier les données
        if offer.status != 'pending':
            raise serializers.ValidationError("Offer is not available.")

        # Déterminer le vendeur et l'acheteur
        if offer.offer_type == Offer.OFFER_TYPE_BUY:
            # Acheteur a créé l'offre, vendeur accepte
            if not self.request.user.is_seller:
                raise serializers.ValidationError("Only sellers can accept buy offers.")
            seller = self.request.user
            buyer = offer.user
            if offer.quantity < quantity:
                raise serializers.ValidationError("Not enough quantity available in the offer.")
        else:
            # Vendeur a créé l'offre, acheteur accepte
            if not self.request.user.is_buyer:
                raise serializers.ValidationError("Only buyers can accept sell offers.")
            seller = offer.user
            buyer = self.request.user
            if offer.stock < quantity:
                raise serializers.ValidationError("Not enough stock available.")

        # Récupérer l'adresse de l'acheteur
        try:
            buyer_address = Address.objects.get(id=buyer_address_id, user=buyer)
        except Address.DoesNotExist:
            raise serializers.ValidationError("Invalid buyer address.")

        # Récupérer l'adresse du vendeur
        try:
            seller_address = Address.objects.filter(user=seller).first()
            if not seller_address:
                raise serializers.ValidationError("Seller has no address.")
        except Address.DoesNotExist:
            raise serializers.ValidationError("Seller has no address.")

        # Calculer les frais
        base_price = offer.price * quantity
        buyer_processing_fee = max(base_price * 0.06, 5.00)
        buyer_shipping_fee = 10.00
        platform_commission = base_price * Decimal(str(getattr(settings, 'PLATFORM_COMMISSION_PERCENT', 0.05)))
        buyer_total_price = base_price + buyer_processing_fee + buyer_shipping_fee + platform_commission

        seller_transaction_fee = max(base_price * 0.09, 5.00)
        seller_processing_fee = base_price * 0.03
        seller_shipping_fee = buyer_shipping_fee
        seller_net_amount = base_price - seller_transaction_fee - seller_processing_fee - seller_shipping_fee - platform_commission

        payment_intent = create_payment_intent(buyer, buyer_total_price)

        # Mettre à jour le stock si c'est une offre de vente
        if offer.offer_type == Offer.OFFER_TYPE_SELL:
            offer.stock -= quantity
            offer.save()

        # Mettre à jour le statut de l'offre
        offer.status = 'accepted'
        offer.save()

        # Remove reservation from cart if exists
        CartItem.objects.filter(buyer=buyer, offer=offer).delete()

        # Créer la commande
        serializer.save(
            buyer=buyer,
            seller=seller,
            base_price=base_price,
            buyer_address=buyer_address,
            seller_address=seller_address,
            buyer_processing_fee=buyer_processing_fee,
            buyer_shipping_fee=buyer_shipping_fee,
            buyer_total_price=buyer_total_price,
            seller_transaction_fee=seller_transaction_fee,
            seller_processing_fee=seller_processing_fee,
            seller_shipping_fee=seller_shipping_fee,
            seller_net_amount=seller_net_amount,
            platform_commission=platform_commission,
            stripe_payment_intent_id=payment_intent.id,
        )

    def perform_update(self, serializer):
        order = serializer.save()
        if order.seller != self.request.user:
            raise serializers.ValidationError("Only the seller can update this order.")