from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'buyer', 'seller', 'listing', 'quantity', 'base_price',
        'buyer_total_price', 'seller_net_amount', 'status',
        'created_at', 'updated_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'seller__username', 'listing__product__name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('buyer', 'seller', 'listing', 'buyer_address', 'seller_address')
    readonly_fields = (
        'base_price', 'buyer_processing_fee', 'buyer_shipping_fee', 'buyer_total_price',
        'seller_transaction_fee', 'seller_processing_fee', 'seller_shipping_fee', 'seller_net_amount',
        'created_at', 'updated_at'
    )
