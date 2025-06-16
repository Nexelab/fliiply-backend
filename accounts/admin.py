from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Address

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'subscribed_to_newsletter', 'is_staff', 'is_verifier', 'is_active')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'subscribed_to_newsletter', 'accepted_terms', 'accepted_terms_at', 'is_staff', 'is_verifier', 'is_active', 'groups')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'username', 'email', 'phone_number',
        'role', 'rating', 'stripe_account_id', 'is_kyc_verified',
        'subscribed_to_newsletter', 'accepted_terms', 'accepted_terms_at',
        'is_staff', 'is_verifier', 'is_superuser', 'is_active'
    )
    list_filter = ('is_staff', 'is_verifier', 'is_superuser', 'is_active', 'subscribed_to_newsletter', 'accepted_terms')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': (
            'email', 'phone_number',
            'subscribed_to_newsletter', 'accepted_terms', 'accepted_terms_at'
            'role', 'rating', 'stripe_account_id', 'is_kyc_verified'
        )
        }),
        ('Permissions', {'fields': ('is_staff', 'is_verifier', 'is_superuser', 'is_active', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'phone_number', 'subscribed_to_newsletter',
                'role',
                'password1', 'password2',
                'is_staff', 'is_verifier', 'is_active', 'groups'
            ),
        }),
    )
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)
    filter_horizontal = ('groups',)
    readonly_fields = ('rating', 'stripe_account_id', 'is_kyc_verified')

    def save_model(self, request, obj, form, change):
        # S'assurer que le mot de passe est haché pour les nouveaux utilisateurs
        if not change and form.cleaned_data.get('password1'):
            obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'city', 'postal_code', 'country')
    search_fields = ('user__username', 'street', 'city', 'postal_code', 'country')
    list_filter = ('country', 'city')