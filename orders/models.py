from django.db import models
from accounts.models import User, Address
from products.models import Product


class Offer(models.Model):
    OFFER_TYPE_BUY = 'buy'
    OFFER_TYPE_SELL = 'sell'
    OFFER_TYPE_CHOICES = [
        (OFFER_TYPE_BUY, 'Buy'),
        (OFFER_TYPE_SELL, 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=50, choices=[
        ('mint', 'Mint'),
        ('near_mint', 'Near Mint'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('played', 'Played'),
        ('poor', 'Poor'),
    ], null=True, blank=True)
    stock = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.offer_type} offer by {self.user.username} for {self.product.name} at {self.price}€"


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_orders')  # Ajouté
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)

    # Adresses
    buyer_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True,
                                      related_name='buyer_orders')
    seller_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True,
                                       related_name='seller_orders')

    # Prix de base (offer.price * quantity)
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

    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username} for {self.offer.product.name}"