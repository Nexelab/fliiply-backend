from django.db import models
from accounts.models import User
from products.models import Listing


class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    reserved_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['buyer']),
            models.Index(fields=['listing']),
            models.Index(fields=['reserved_until']),
            models.Index(fields=['created_at']),
            models.Index(fields=['buyer', 'created_at']),
        ]
        unique_together = ("buyer", "listing")

    def __str__(self):
        return f"{self.quantity} of {self.listing} reserved by {self.buyer}"


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # Adresses
    buyer_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True,
                                      related_name='buyer_orders')

    # Prix de base (somme des listings)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Frais pour l'acheteur
    buyer_processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_total_price = models.DecimalField(max_digits=10, decimal_places=2)


    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['buyer']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['listing']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.listing} in order {self.order_id}"
