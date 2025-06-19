from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.conf import settings

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
    is_graded = models.BooleanField(default=False)

    def __str__(self):
        return self.label

class Grade(models.Model):
    GRADER_CHOICES = [
        ('PSA', 'PSA'),
        ('PCA', 'PCA'),
        ('BGS', 'BGS'),
        ('CGC', 'CGC'),
        ('CCC', 'CCC'),
        ('SGC', 'SGC'),
        ('OTHER', 'Autre'),
    ]
    value = models.DecimalField(max_digits=4, decimal_places=1)
    grader = models.CharField(max_length=20, choices=GRADER_CHOICES, default='PSA')

    def __str__(self):
        return f"{self.grader} {self.value}"

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
        from django.db.models import Avg
        return self.listings.aggregate(avg_price=Avg('price'))['avg_price'] or 0

    def calculate_total_stock(self):
        from django.db.models import Sum
        return self.listings.aggregate(total_stock=Sum('stock'))['total_stock'] or 0

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['tcg_type']),
            models.Index(fields=['block']),
            models.Index(fields=['series']),
            models.Index(fields=['created_at']),
            models.Index(fields=['tcg_type', 'name']),
            models.Index(fields=['block', 'series']),
        ]
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

    def clean(self):
        # Empêche une incohérence entre condition non-graded et grade renseigné
        if self.grade and self.condition and not self.condition.is_graded:
            raise ValidationError("You cannot assign a grade with a non-graded condition.")
        if not self.grade and self.condition and self.condition.is_graded:
            raise ValidationError("A graded condition must have a grade value.")

    def __str__(self):
        base = f"{self.product.name} - {self.language} - {self.version} - {self.condition}"
        if self.grade:
            base += f" - {self.grade}"
        return base

    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['language']),
            models.Index(fields=['version']),
            models.Index(fields=['condition']),
            models.Index(fields=['grade']),
            models.Index(fields=['product', 'language']),
            models.Index(fields=['condition', 'grade']),
        ]
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
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['seller']),
            models.Index(fields=['product']),
            models.Index(fields=['variant']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'price']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['stock']),
        ]
        ordering = ['-created_at']


class Collection(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    variants = models.ManyToManyField(Variant, through='CollectionItem', related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('collection', 'variant')

    def __str__(self):
        return f"{self.variant} in {self.collection.name} x{self.quantity}"


class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    filters = models.JSONField(blank=True, null=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} searched '{self.query}' at {self.searched_at}"
