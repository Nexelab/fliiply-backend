from django.contrib import admin
from .models import Category, Product, PriceHistory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'id')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'set', 'category', 'average_price', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'set')
    date_hierarchy = 'created_at'
    raw_id_fields = ('category',)
    readonly_fields = ('created_at', 'updated_at', 'average_price')

    def average_price(self, obj):
        return obj.calculate_average_price()
    average_price.short_description = 'Average Price'

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('product__name',)
    date_hierarchy = 'recorded_at'
    raw_id_fields = ('product',)
    readonly_fields = ('recorded_at',)