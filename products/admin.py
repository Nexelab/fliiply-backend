# products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, PriceHistory

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = "Prévisualisation"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'description')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'series', 'collection', 'tcg_type', 'language', 'created_at')
    list_filter = ('tcg_type', 'language', 'categories')
    search_fields = ('name', 'series', 'collection', 'description')
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'series', 'collection', 'description')
        }),
        ('Détails TCG', {
            'fields': ('tcg_type', 'language')
        }),
        ('Catégories', {
            'fields': ('categories',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['duplicate_product', 'mark_as_verified']

    def duplicate_product(self, request, queryset):
        for product in queryset:
            images = list(product.images.all())
            product.pk = None
            product.name = f"{product.name} (Copie)"
            product.save()
            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image.image,
                    alt_text=image.alt_text
                )
        self.message_user(request, f"{queryset.count()} produit(s) dupliqué(s).")
    duplicate_product.short_description = "Dupliquer les produits sélectionnés"

    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} produit(s) marqué(s) comme vérifié(s).")
    mark_as_verified.short_description = "Marquer comme vérifié"

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'alt_text', 'created_at', 'image_preview')
    list_filter = ('product',)
    search_fields = ('alt_text', 'product__name')
    readonly_fields = ('created_at', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = "Prévisualisation"

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'recorded_at')
    list_filter = ('product',)
    search_fields = ('product__name',)
    readonly_fields = ('recorded_at',)