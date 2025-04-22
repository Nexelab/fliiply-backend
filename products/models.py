from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PriceHistory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='price_histories')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.price}€ on {self.recorded_at}"

class Product(models.Model):
    set = models.CharField(max_length=100)  # Ex. "Écarlate et Violet ParadoXe RiFT Lune Néo"
    name = models.CharField(max_length=200)  # Ex. "Boîte de dressage d’élite du Centre Pokémon"
    image = models.URLField(max_length=500, blank=True, null=True)  # URL de l'image
    description = models.TextField(blank=True, null=True)  # Description détaillée
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.set})"

    def calculate_average_price(self):
        listings = self.listings.all()
        if listings.exists():
            total_price = sum(listing.price for listing in listings)
            return total_price / listings.count()
        return 0  # Retourne 0 si aucune annonce n'existe

    def calculate_total_stock(self):
        listings = self.listings.all()
        if listings.exists():
            return sum(listing.stock for listing in listings)
        return 0  # Retourne 0 si aucune annonce n'existe

    class Meta:
        unique_together = ['set', 'name']  # Garantir l'unicité par set et name