from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_buyer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=True)
    is_verifier = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    billing_address = models.OneToOneField(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_user',
    )

    def __str__(self):
        return self.username

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('billing', 'Facturation'),
        ('delivery', 'Livraison'),
        ('both', 'Facturation et Livraison'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100, blank=True, help_text="Nom de l'adresse (ex. Maison, Bureau")
    street_number = models.CharField(max_length=10, blank=True, help_text="Numéro de voie")
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='delivery')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.street_number} {self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'address_type'],
                condition=models.Q(address_type='billing'),
                name='unique_billing_address_per_user'
            )
        ]

