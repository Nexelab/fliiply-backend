from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('product', 'seller', 'price', 'condition', 'stock', 'created_at', 'updated_at')  # Colonnes affichées
    list_filter = ('condition', 'created_at')  # Filtres
    search_fields = ('product__name', 'seller__username')  # Recherche sur le nom du produit et le nom du vendeur
    date_hierarchy = 'created_at'  # Navigation par date
    raw_id_fields = ('product', 'seller')  # Utiliser un champ ID pour les relations ForeignKey
    readonly_fields = ('created_at', 'updated_at')  # Champs en lecture seule