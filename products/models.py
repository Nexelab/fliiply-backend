from django.db import models
from django.utils.text import slugify

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

class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Version(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    tcg_types = models.JSONField(default=list)
    description = models.TextField(blank=True, null=True)
    displayable = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Condition(models.Model):
    code = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=100)

    def __str__(self):
        return self.label

class Grade(models.Model):
    value = models.DecimalField(max_digits=4, decimal_places=1)  # ex: 9.5

    def __str__(self):
        return str(self.value)

class Product(models.Model):
    TCG_TYPES = (
        ('pokemon', 'Pokémon'),
        ('yugioh', 'Yu-Gi-Oh'),
        ('magic', 'Magic: The Gathering'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    block = models.CharField(max_length=100, blank=True, null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tcg_type = models.CharField(max_length=50, choices=TCG_TYPES, default='pokemon')
    categories = models.ManyToManyField(Category, related_name='products')
    allowed_languages = models.ManyToManyField(Language, blank=True)
    allowed_versions = models.ManyToManyField(Version, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.block or 'No Block'}, {self.series or 'No Series'}, {self.tcg_type})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
            models.UniqueConstraint(fields=['name', 'block', 'series'], name='unique_product')
        ]

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = 'product image'
        verbose_name_plural = 'product images'

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    version = models.ForeignKey(Version, on_delete=models.PROTECT)
    condition = models.ForeignKey(Condition, on_delete=models.PROTECT)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.language} - {self.version} - {self.condition}{' - Graded ' + str(self.grade) if self.grade else ''}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'language', 'version', 'condition', 'grade'],
                name='unique_variant_combination'
            )
        ]

class Listing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('inactive', 'Inactive'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='listings')
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT)
    seller = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.seller} selling {self.variant} at {self.price}€ (Stock: {self.stock})"

    class Meta:
        ordering = ['-created_at']
