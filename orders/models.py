from django.db import models
from accounts.models import User, Address
from products.models import Listing


class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    reserved_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("buyer", "listing")

    def __str__(self):
        return f"{self.quantity} of {self.listing} reserved by {self.buyer}"


class CartItem(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    reserved_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("buyer", "offer")

    def __str__(self):
        return f"{self.quantity} of {self.offer} reserved by {self.buyer}"


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_orders')  # Ajouté
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)

    # Adresses
    buyer_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True,
                                      related_name='buyer_orders')
    seller_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True,
                                       related_name='seller_orders')

    # Prix de base (listing.price * quantity)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Frais pour l'acheteur
    buyer_processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Frais pour le vendeur
    seller_transaction_fee = models.DecimalField(max_digits=10, decimal_places=2)
    seller_processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    seller_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    seller_net_amount = models.DecimalField(max_digits=10, decimal_places=2)

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

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username} for {self.listing.product.name}"
