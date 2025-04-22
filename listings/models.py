from django.db import models
from accounts.models import User
from products.models import Product

class Listing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='listings')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=50, choices=[
        ('mint', 'Mint'),
        ('near_mint', 'Near Mint'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('played', 'Played'),
        ('poor', 'Poor'),
    ])
    stock = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} (Listed by {self.seller.username} for {self.price}€)"