from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        PARTICULIER = 'particulier', 'Particulier'
        PROFESSIONNEL = 'professionnel', 'Professionnel'

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
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_expiry = models.DateTimeField(blank=True, null=True)
    subscribed_to_newsletter = models.BooleanField(
        default=False,
        help_text="Indique si l'utilisateur est abonné à la newsletter."
    )
    accepted_terms = models.BooleanField(
        default=False,
        help_text="Indique si l'utilisateur a accepté les conditions générales."
    )
    accepted_terms_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date à laquelle l'utilisateur a accepté les conditions générales."
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICULIER,
        help_text="Définit le rôle de l'utilisateur (particulier ou professionnel)."
    )
    rating = models.FloatField(
        default=0.0,
        help_text="Note moyenne de l'utilisateur en tant que vendeur."
    )
    stripe_account_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Identifiant du compte Stripe de l'utilisateur."
    )
    is_kyc_verified = models.BooleanField(
        default=False,
        help_text="Indique si l'utilisateur a complété le KYC avec succès."
    )
    total_sales_amount = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2,
        help_text="Montant total des ventes réalisées par l'utilisateur."
    )

    def __str__(self):
        return self.username

    def is_verification_token_valid(self):
        """Vérifie si le token de vérification est encore valide."""
        if not self.email_verification_expiry:
            return False
        return timezone.now() <= self.email_verification_expiry

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

