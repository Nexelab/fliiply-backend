from django.contrib import admin
from .models import Category, Product, PriceHistory, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'id')
    list_filter = ('parent', 'name')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('parent',)
    list_select_related = ('parent',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'alt_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'alt_text')
    raw_id_fields = ('product',)
    readonly_fields = ('created_at',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text')
    raw_id_fields = ('product',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'series', 'collection', 'tcg_type', 'language', 'average_price', 'total_stock', 'created_at')
    list_filter = ('categories', 'tcg_type', 'language', 'series', 'created_at')
    search_fields = ('name', 'series', 'collection')
    date_hierarchy = 'created_at'
    filter_horizontal = ('categories',)
    inlines = [ProductImageInline]
    readonly_fields = ('created_at', 'updated_at', 'average_price', 'total_stock')
    list_select_related = ('categories',)

    def average_price(self, obj):
        return obj.calculate_average_price()
    average_price.short_description = 'Average Price'

    def total_stock(self, obj):
        return obj.calculate_total_stock()
    total_stock.short_description = 'Total Stock'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('product__name',)
    date_hierarchy = 'recorded_at'
    raw_id_fields = ('product',)
    readonly_fields = ('recorded_at',)