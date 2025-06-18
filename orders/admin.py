from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'buyer', 'base_price', 'buyer_total_price',
        'status', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('buyer', 'buyer_address')
    readonly_fields = (
        'base_price', 'buyer_processing_fee', 'buyer_shipping_fee', 'buyer_total_price',
        'platform_commission', 'created_at', 'updated_at'
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'listing', 'quantity')
    raw_id_fields = ('order', 'listing')
