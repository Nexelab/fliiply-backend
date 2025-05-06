from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = 'product image'
        verbose_name_plural = 'product images'

class PriceHistory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='price_histories')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.price}€ on {self.recorded_at}"

class Product(models.Model):
    TCG_TYPES = (
        ('pokemon', 'Pokémon'),
        ('yugioh', 'Yu-Gi-Oh'),
        ('magic', 'Magic: The Gathering'),
        ('other', 'Other'),
    )
    LANGUAGES = (
        ('fr', 'Français'),
        ('en', 'Anglais'),
        ('jp', 'Japonais'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    series = models.CharField(max_length=100, blank=True, null=True)
    collection = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tcg_type = models.CharField(max_length=50, choices=TCG_TYPES, default='pokemon')
    language = models.CharField(max_length=50, choices=LANGUAGES, default='fr')
    categories = models.ManyToManyField(Category, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.series or 'No Series'}, {self.collection or 'No Collection'}, {self.tcg_type}, {self.language})"

    def calculate_average_price(self):
        listings = self.listings.all()
        if listings.exists():
            total_price = sum(listing.price for listing in listings)
            return total_price / listings.count()
        return 0

    def calculate_total_stock(self):
        listings = self.listings.all()
        if listings.exists():
            return sum(listing.stock for listing in listings)
        return 0

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'series', 'collection'], name='unique_product')
        ]